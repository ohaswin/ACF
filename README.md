<div align="center">
  <h1>🏭 Autonomous Content Factory</h1>
  <p>An AI-driven pipeline that instantly transforms raw technical content into high-quality, multi-channel marketing campaigns.</p>
  <br>
  <a href="https://youtu.be/Cn5YVNLUJpA">
    <img src="https://img.shields.io/badge/Watch%20Demo%20Video-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="Watch Demo Video" />
  </a>
  <br>
</div>

---

## 📖 Overview



The **Autonomous Content Factory** is an internal marketing tool designed to combat "Creative Burnout" and guarantee brand consistency. Instead of manually rewriting the same product announcement into various formats, users simply provide a single source document. An assembly line of specialized AI agents then collaborates to analyze the text, extract accurate facts, and instantly generate coordinated content for blogs, social media, and emails—all while providing real-time visibility into their decision-making process.

## ✨ Key Features

- **Omnichannel Content Generation**: Simultaneously generates a Blog Post (Professional tone), a Social Media Thread (Punchy tone), and an Email Teaser (Engaging tone) from a single source.
- **Multi-Agent AI Pipeline**:
  - 🧠 **Lead Research & Fact-Check (Agent 1)**: Analyzes raw input to extract a structured "Source of Truth" Fact-Sheet, flagging ambiguous statements.
  - ✍️ **Creative Copywriter (Agent 2)**: Drafts the content forms tailored specifically to the targeted channels and their distinct tones.
  - 🛡️ **Editor-in-Chief (Agent 3)**: Acts as the quality control gatekeeper. Rejects drafts with hallucinations or inappropriate tones, sending specific correction notes back to the Copywriter.
- **Live Agent Room Dashboard**: A real-time chat/feed interface mapping the workflow and interaction between the agents using WebSockets.
- **Flexible Inputs**: Accepts direct text input, URL scraping, and document uploads (`.txt`, `.md`, `.pdf`).
- **Interactive Final Review**: Side-by-side comparisons of source text and generated outputs. Includes responsive previews (mobile vs. desktop) and granular regeneration with targeted feedback.
- **One-Click Export**: Download the fully approved "Campaign Kit" as a `.zip` archive or copy individual pieces to the clipboard.

## 🛠️ Tech Stack

- **Backend framework**: Python Django
- **Frontend styling**: TailwindCSS
- **Real-Time Communication**: Django Channels (WebSockets)
- **AI Integration**: Gemini API via `python-genai`
- **Asynchronous Processing**: Celery / `asyncio` for the multi-agent execution loop
- **File Parsing**: `PyPDF2` / `python-docx`

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- [Redis](https://redis.io/) (used as a message broker for Django Channels and Celery)
- A valid Google Gemini API Key.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/autonomous-content-factory.git
   cd autonomous-content-factory
   ```

2. **Set up a virtual environment & install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the project root and add configurations such as:
   ```env
   SECRET_KEY=your_django_secret_key
   DEBUG=True
   GEMINI_API_KEY=your_gemini_api_key
   REDIS_URL=redis://localhost:6379/0
   ```

4. **Run Database Migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Start Redis server:**
   Ensure your local Redis server is running.
   ```bash
   redis-server
   ```

6. **Start the Celery worker (if using Celery):**
   ```bash
   celery -A acf worker -l info
   ```

7. **Run the Django development server:**
   ```bash
   python manage.py runserver
   ```

Access the application by navigating to `http://localhost:8000` in your web browser.

## 🎯 Usage

1. **Start a Campaign**: Upload your source material (PDF, docx, URL, or raw text) on the Start Page.
2. **Watch the Process**: Observe the *Agent Room* as Agent 1 extracts facts, Agent 2 writes drafts, and Agent 3 reviews and critiques them in real time.
3. **Review & Refine**: Analyze the outputs side-by-side with your original text. Use the "Regenerate" feature to provide specific directives to the AI if needed.
4. **Deploy**: Click to download your compiled Campaign Kit and publish across your marketing channels!

---
*Built to reduce campaign production time by 80% with zero hallucinated features.*
