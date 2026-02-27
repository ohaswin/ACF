import httpx
from bs4 import BeautifulSoup
from io import BytesIO
from pypdf import PdfReader
from docx import Document


def extract_text_from_url(url: str) -> str:
    """Fetches text content from a given URL."""
    try:
        response = httpx.get(url, timeout=10.0, follow_redirects=True)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        t = soup.get_text(separator=' ', strip=True)
        return t
    except Exception as e:
        return f"Error extracting from URL: {str(e)}"


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text from a PDF file."""
    try:
        reader = PdfReader(BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting from PDF: {str(e)}"


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extracts text from a DOCX file."""
    try:
        doc = Document(BytesIO(file_bytes))
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        return f"Error extracting from DOCX: {str(e)}"


def process_uploaded_file(file_obj) -> str:
    """Determines file type and extracts text accordingly."""
    filename = file_obj.name.lower()
    file_bytes = file_obj.read()
    
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    elif filename.endswith(".txt") or filename.endswith(".md"):
        try:
            return file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            # Fallback to a broader encoding if utf-8 fails
            return file_bytes.decode('latin-1', errors='replace')
    else:
        return "Unsupported file type. Please upload a .txt, .md, .pdf, or .docx file."


def log_agent_action(campaign, agent_name, message, status=""):
    """Utility to log agent actions to the DB for the dashboard."""
    from .models import AgentLog
    log_entry = AgentLog.objects.create(campaign=campaign, agent_name=agent_name, message=message)
    
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    import datetime

    channel_layer = get_channel_layer()
    if channel_layer:
        room_group_name = f'campaign_{campaign.id}'
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'agent_log',
                'message': message,
                'agent_name': agent_name,
                'status': status,
                'timestamp': log_entry.created_at.strftime('%H:%M:%S')
            }
        )
