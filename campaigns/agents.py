import os
import json
from google import genai
from .models import Campaign, ContentPiece, AgentLog
from .utils import log_agent_action

def get_genai_client():
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    return genai.Client(api_key=api_key)

def run_agent_1_lead_research(campaign: Campaign):
    """
    Agent 1: Reads raw text and extracts the factual Source of Truth.
    Returns the JSON fact sheet.
    """
    log_agent_action(campaign, "Agent 1 (Research)", "Analyzing source material to extract core facts...")
    
    client = get_genai_client()
    
    prompt = f"""
    You are the 'Lead Research & Fact-Check' Agent. Your job is to read the raw source material and extract the "Truth".
    
    Source Material:
    ----------------
    {campaign.source_text}
    ----------------
    
    Identify the core product features, technical specs, the target audience, and the main Value Proposition.
    Flag any "ambiguous" statements in the source text that might lead to confusion.
    
    You MUST return your findings as a strict JSON object with exactly these keys:
    {{
        "core_features": ["feature 1", "feature 2"],
        "technical_specs": ["spec 1", "spec 2"],
        "target_audience": "Who this is for",
        "value_proposition": "The main selling point",
        "ambiguities_flagged": ["ambiguity 1", "ambiguity 2"] or []
    }}
    
    Return ONLY the raw JSON object. Do not wrap it in markdown codeblocks like ```json.
    """
    
    # Using gemini-2.5-flash as the default model for speed and capability
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    
    try:
        fact_sheet = json.loads(response.text.strip())
        campaign.fact_sheet = fact_sheet
        campaign.status = 'writing'
        campaign.save()
        log_agent_action(campaign, "Agent 1 (Research)", "Fact sheet successfully generated.")
        return fact_sheet
    except json.JSONDecodeError as e:
        log_agent_action(campaign, "Agent 1 (Research)", f"Failed to parse JSON: {e}. Output was: {response.text}")
        campaign.status = 'failed'
        campaign.save()
        return None

def run_agent_2_creative_copywriter(campaign: Campaign, channel: str, editor_feedback: str = None) -> ContentPiece:
    """
    Agent 2: Takes the Fact-Sheet and transforms it into the requested format (blog, social, email).
    """
    client = get_genai_client()
    
    action_text = f"Drafting {channel} content..."
    if editor_feedback:
        action_text = f"Re-drafting {channel} based on Editor feedback..."
    log_agent_action(campaign, "Agent 2 (Copywriter)", action_text)

    fact_sheet_str = json.dumps(campaign.fact_sheet, indent=2)
    
    channel_instructions = {
        'blog': "Write a 500-word Blog Post. The tone MUST be 'Professional and Trustworthy'. Use markdown formatting.",
        'social': "Write a 5-post Social Media Thread (e.g. for Twitter/X). The tone MUST be 'Engaging and Punchy'. Separate posts with '---'.",
        'email': "Write a 1-paragraph Email Teaser to send to our mailing list. The tone should be 'Direct and Exciting'."
    }
    
    instruction = channel_instructions.get(channel, "Write content.")
    
    prompt = f"""
    You are the 'Creative Copywriter' Agent. Your job is to write marketing copy based STRICTLY on the approved Fact-Sheet below.
    
    Fact-Sheet:
    -----------
    {fact_sheet_str}
    -----------
    
    Instructions for this task:
    {instruction}
    
    CRITICAL: You must ensure that the specific "Value Proposition" identified in the Fact-Sheet is the hero of the content.
    """

    if editor_feedback:
        prompt += f"\n\nREVIOUS DRAFT REJECTED! Please apply this feedback from the Editor-in-Chief:\n{editor_feedback}"

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    
    # Create or update ContentPiece
    piece, created = ContentPiece.objects.get_or_create(
        campaign=campaign,
        channel=channel,
        defaults={'status': 'draft', 'content': ''}
    )
    
    if not created:
        piece.iteration_count += 1
        
    piece.content = response.text.strip()
    piece.status = 'draft'
    piece.editor_feedback = '' # Clear old feedback
    piece.save()
    
    log_agent_action(campaign, "Agent 2 (Copywriter)", f"Draft for {channel} completed (Iteration {piece.iteration_count}).")
    return piece

def run_agent_3_editor_in_chief(campaign: Campaign, piece: ContentPiece) -> bool:
    """
    Agent 3: Critiques and approves the drafted content against the fact sheet.
    Returns True if approved, False if rejected.
    """
    client = get_genai_client()
    log_agent_action(campaign, "Agent 3 (Editor)", f"Reviewing {piece.channel} draft...")

    fact_sheet_str = json.dumps(campaign.fact_sheet, indent=2)
    
    prompt = f"""
    You are the 'Editor-in-Chief' Agent. You are the Gatekeeper. You do not write; you only critique and approve.
    
    You must evaluate the following Draft against the original Fact-Sheet.
    
    Fact-Sheet (The Source of Truth):
    -----------
    {fact_sheet_str}
    -----------
    
    Draft Content ({piece.channel}):
    -----------
    {piece.content}
    -----------
    
    Your Task:
    1. Hallucination Check: Did the Copywriter invent any features, prices, or facts not present in the Fact-Sheet?
    2. Tone Audit: Is the language too "salesy" or "robotic"? Does it fit the requested channel?
    
    You MUST respond with a strict JSON object containing exactly these keys:
    {{
        "approved": true or false,
        "feedback": "If rejected, write a specific Correction Note back to the Copywriter (e.g., 'The blog post is too long; shorten the intro and fix the price in paragraph 2.'). If approved, just say 'Looks good.'"
    }}
    
    Return ONLY the raw JSON object without markdown formatting.
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    
    try:
        feedback_data = json.loads(response.text.strip())
        is_approved = feedback_data.get('approved', False)
        feedback_text = feedback_data.get('feedback', '')
        
        if is_approved:
            piece.status = 'approved'
            piece.save()
            log_agent_action(campaign, "Agent 3 (Editor)", f"APPROVED {piece.channel}.")
            return True
        else:
            piece.status = 'rejected'
            piece.editor_feedback = feedback_text
            piece.save()
            log_agent_action(campaign, "Agent 3 (Editor)", f"REJECTED {piece.channel}. Feedback: {feedback_text}")
            return False
            
    except json.JSONDecodeError as e:
        log_agent_action(campaign, "Agent 3 (Editor)", f"Error parsing Editor decision. Defaulting to Rejected. Output was: {response.text}")
        piece.status = 'rejected'
        piece.editor_feedback = "System Error: Editor failed to provide formatted feedback. Please regenerate."
        piece.save()
        return False
