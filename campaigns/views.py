from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .models import Campaign, AgentLog
from .utils import extract_text_from_url, process_uploaded_file
from .tasks import run_campaign_pipeline

def create_campaign(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        raw_text = request.POST.get('raw_text', '').strip()
        url = request.POST.get('url', '').strip()
        uploaded_file = request.FILES.get('document')

        source_text = ""
        
        # Priority: File > URL > Raw Text
        if uploaded_file:
            source_text = process_uploaded_file(uploaded_file)
            if not title:
                title = uploaded_file.name
        elif url:
            source_text = extract_text_from_url(url)
            if not title:
                title = url.split("://")[-1].split("/")[0]
        elif raw_text:
            source_text = raw_text
            if not title:
                title = f"Campaign {Campaign.objects.count() + 1}"

        if not source_text or source_text.startswith("Error") or source_text.startswith("Unsupported"):
            messages.error(request, f"Failed to extract source content: {source_text}")
            return render(request, 'campaigns/create.html', {'title': title, 'raw_text': raw_text, 'url': url})

        campaign = Campaign.objects.create(
            title=title,
            source_text=source_text,
            status='pending'
        )
        AgentLog.objects.create(campaign=campaign, agent_name="System", message="Campaign Created. Source material extracted.")

        run_campaign_pipeline.delay(campaign.id)
        
        return redirect(reverse('campaigns:dashboard', args=[campaign.id]))

    return render(request, 'campaigns/create.html')

def dashboard(request, campaign_id):
    campaign = Campaign.objects.get(id=campaign_id)
    logs = campaign.logs.order_by('created_at')
    return render(request, 'campaigns/dashboard.html', {
        'campaign': campaign,
        'logs': logs
    })

def review_campaign(request, campaign_id):
    campaign = Campaign.objects.get(id=campaign_id)
    pieces = campaign.pieces.all()
    return render(request, 'campaigns/review.html', {
        'campaign': campaign,
        'pieces': pieces
    })

def regenerate_piece(request, piece_id):
    if request.method == 'POST':
        from .models import ContentPiece
        piece = ContentPiece.objects.get(id=piece_id)
        feedback = request.POST.get('feedback', '').strip()
        
        piece.status = 'rejected'
        piece.editor_feedback = feedback if feedback else "User requested regeneration without specific feedback."
        piece.save()
        
        AgentLog.objects.create(campaign=piece.campaign, agent_name="System", message=f"User requested regeneration for {piece.get_channel_display()}.")
        
        # We re-run the pipeline. It handles looping over channels and it'll skip ones that are already 'approved'
        # Wait, the current run_campaign_pipeline doesn't skip approved ones natively yet. We need to update that too!
        run_campaign_pipeline.delay(piece.campaign.id)
        
        messages.success(request, f"Regeneration started for {piece.get_channel_display()}.")
        return redirect('campaigns:dashboard', campaign_id=piece.campaign.id)
def download_campaign(request, campaign_id):
    import io
    import zipfile
    from django.http import HttpResponse

    campaign = Campaign.objects.get(id=campaign_id)
    pieces = campaign.pieces.filter(status='approved')

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Add Source Fact Sheet
        if campaign.fact_sheet:
            import json
            zip_file.writestr("fact_sheet.json", json.dumps(campaign.fact_sheet, indent=2))
        
        # Add Pieces
        for piece in pieces:
            filename = f"{piece.channel}_copy.md"
            zip_file.writestr(filename, piece.content)

    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="campaign_{campaign.id}_assets.zip"'
    return response
