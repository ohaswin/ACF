from celery import shared_task
from .models import Campaign, ContentPiece, AgentLog
from .agents import run_agent_1_lead_research, run_agent_2_creative_copywriter, run_agent_3_editor_in_chief
from .utils import log_agent_action

@shared_task
def run_campaign_pipeline(campaign_id: int):
    """
    Orchestrates the AI agents for the given campaign.
    """
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        
        # 1. Start Lead Research
        fact_sheet = run_agent_1_lead_research(campaign)
        
        if not fact_sheet:
            log_agent_action(campaign, "System", "Pipeline halted due to Agent 1 failure.")
            return

        # 2. Start Creative Copywriting & Editor Loop
        channels = ['blog', 'social', 'email']
        max_retries = 3
        
        for channel in channels:
            # Check if this channel is already approved (e.g. from a previous partial run)
            try:
                existing_piece = ContentPiece.objects.get(campaign=campaign, channel=channel)
                if existing_piece.status == 'approved':
                    log_agent_action(campaign, "System", f"Skipping {channel} (already approved).")
                    continue
                feedback = existing_piece.editor_feedback
            except ContentPiece.DoesNotExist:
                feedback = None

            piece_approved = False
            retries = 0
            
            while not piece_approved and retries < max_retries:
                # Agent 2 drafts
                piece = run_agent_2_creative_copywriter(campaign, channel, editor_feedback=feedback)
                
                # Agent 3 reviews
                is_approved = run_agent_3_editor_in_chief(campaign, piece)
                
                if is_approved:
                    piece_approved = True
                else:
                    feedback = piece.editor_feedback
                    retries += 1
            
            if not piece_approved:
                log_agent_action(campaign, "System", f"Max retries reached for {channel}. Editor unable to approve draft.", status="FAILED")
                
        # Only mark campaign as completed if all pieces are approved
        all_pieces_approved = not campaign.pieces.filter(status__in=['draft', 'rejected']).exists()
        if all_pieces_approved and campaign.pieces.count() == len(channels):
            campaign.status = 'completed'
            campaign.save()
            log_agent_action(campaign, "System", "Campaign pipeline generation completed.", status="COMPLETED")
        else:
            campaign.status = 'writing'
            campaign.save()
            log_agent_action(campaign, "System", "Pipeline paused or awaiting regeneration.", status="PAUSED")
        
    except Campaign.DoesNotExist:
        pass
    except Exception as e:
        log_agent_action(campaign, "System", f"Pipeline encountered a critical error: {e}")
        campaign.status = 'failed'
        campaign.save()
