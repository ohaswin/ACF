## Relevant Files

- `config/settings.py` - Core Django settings, installed apps, Celery/Channels configuration.
- `campaigns/models.py` - Models for Campaign, Content Piece, and Agent interactions.
- `campaigns/views.py` - Views for campaign creation, dashboard, and final review.
- `campaigns/agents.py` - AI agent logic using python-genai.
- `campaigns/consumers.py` - Django Channels consumer for real-time WebSocket updates.
- `campaigns/tasks.py` - Celery/Async tasks for running the AI pipeline in the background.
- `templates/campaigns/create.html` - Start page for inputting content.
- `templates/campaigns/dashboard.html` - The live Agent Room UI.
- `templates/campaigns/review.html` - The final review and regeneration view.
- `requirements.txt` - Python dependencies.

### Notes

- Unit tests should typically be placed alongside the code files they are testing.
- Use `python manage.py test` to run tests. Running without a path executes all tests found by the Django test runner.
- TailwindCSS should be managed via a Django package or raw CDN strategy for the MVP depending on standard practices.

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:
- `- [ ] 1.1 Read file` → `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout a new branch for this feature (e.g., `git checkout -b feature/autonomous-content-factory`)
- [ ] 1.0 Setup Django Project & Core Architecture
  - [ ] 1.1 Initialize a new Django project and create a main `campaigns` application.
  - [ ] 1.2 Install required libraries (`django`, `google-genai`, `channels`, `daphne`, `redis`, `celery`).
  - [ ] 1.3 Configure Django settings for ASGI (Daphne), Channels channel layers (Redis), and optionally Celery for task queuing.
  - [ ] 1.4 Setup base TailwindCSS integration for styling.
  - [ ] 1.5 Create core database models in `campaigns/models.py` (e.g., `Campaign`, `ContentPiece` for Blog/Social/Email).
- [ ] 2.0 Implement Document Input & Processing Methods
  - [ ] 2.1 Build the 'Campaign Start Page' UI (`create.html`) with form inputs for raw text, URL, and file uploads.
  - [ ] 2.2 Create utility functions to extract text from user input (e.g., parsing PDF/DOCX or fetching basic HTML text from a URL).
  - [ ] 2.3 Implement the form submission view to save the initial source text to the database and trigger the AI pipeline.
- [ ] 3.0 Build the AI Agent Pipeline (Gemini Integration)
  - [ ] 3.1 Configure the `google-genai` client using an API key stored in environment variables.
  - [ ] 3.2 Implement **Agent 1 (Lead Research)** logic to consume source text and generate a structured JSON/Markdown Fact-Sheet.
  - [ ] 3.3 Implement **Agent 2 (Creative Copywriter)** logic to consume the Fact-Sheet and generate Blog, Social Thread, and Email drafts simultaneously.
  - [ ] 3.4 Implement **Agent 3 (Editor-in-Chief)** logic to evaluate Agent 2’s output against the Fact-Sheet and return either approval or specific correction notes.
  - [ ] 3.5 Write the orchestrator loop that ties Agent 1 -> Agent 2 -> Agent 3 together, including retry limits for rejected drafts.
- [ ] 4.0 Develop the Agent Room Real-Time Dashboard (Django Channels)
  - [ ] 4.1 Create a Channels `AsyncWebsocketConsumer` in `campaigns/consumers.py` to handle client connections.
  - [ ] 4.2 Update the AI pipeline orchestrator (from Task 3.5) to broadcast status messages (e.g., "Agent 2 is typing...", "Agent 3 rejected the blog") to the WebSocket group at each step.
  - [ ] 4.3 Build the frontend UI (`dashboard.html`) to connect to the WebSocket, receive messages, and visually update the agent status icons and live chat feed.
- [ ] 5.0 Build Final Review, Regeneration, and Export Views
  - [ ] 5.1 Create the Final Review view (`review.html`) displaying the original source alongside the approved outputs.
  - [ ] 5.2 Add responsive UI toggles to preview content for different devices (mobile vs desktop).
  - [ ] 5.3 Implement the "Regenerate" functionality: Build an endpoint/WebSocket action that accepts specific user feedback, triggers Agent 2 (and Agent 3) for that singular piece, and visually updates the content.
  - [ ] 5.4 Implement individual "Copy to Clipboard" buttons for each generated text block.
  - [ ] 5.5 Implement a "Download Campaign Kit" view that bundles the final texts into a single `.zip` file and serves it for download.
