# Product Requirements Document: Autonomous Content Factory

## 1. Introduction/Overview

The "Autonomous Content Factory" is an internal marketing tool designed to solve "Creative Burnout" and ensure brand consistency by automating the repurposing of technical content. Often, marketers must manually rewrite a single product announcement into various formats (blogs, social threads, emails), which is repetitive, error-prone, and inconsistent in tone. This application solves that by providing a system where users can drop a single source document, and an assembly line of specialized AI agents will analyze it, extract a factual "Source of Truth", and instantly generate a coordinated, multi-channel marketing campaign. 

**Goal:** To build an automated, multi-agent AI pipeline using Django and Gemini that transforms raw technical content into high-quality, channel-specific marketing materials while providing real-time visibility into the AI collaboration process.

## 2. Goals

*   Automate the generation of simultaneous multi-format content (Blog Post, Social Media Thread, Email Teaser) from a single source document.
*   Enforce factual accuracy and consistent, channel-appropriate tone across all outputs through an AI-driven Quality Control loop.
*   Provide a real-time, transparent user interface that shows the AI agents collaborating and communicating.
*   Reduce the time taken to produce a full campaign kit from hours to minutes.

## 3. User Stories

*   **As a marketer**, I want to paste text, provide a URL, or upload a document (.txt, .md, .pdf) as a source so that I don't have to manually summarize new features.
*   **As a marketer**, I want to see a live visual dashboard of the AI agents working ("Thinking", "Typing", "Editor Rejected...") so that I understand the system's progress and decision-making.
*   **As a marketer**, I want to review the generated campaign outputs side-by-side with my original source text so that I can easily verify factual accuracy.
*   **As a marketer**, I want the ability to regenerate a specific piece of content (e.g., just the blog post) and optionally provide specific feedback (e.g., "make this punchier"), without having to restart the entire campaign generation.
*   **As a marketer**, I want to download all approved content in one click (as a zip file or copy to clipboard) so that I can immediately use the materials.

## 4. Functional Requirements

1.  **Input Methods:** Provide a "Campaign Start Page" that accepts direct text input, URL scraping, and document uploads (.txt, .md, .pdf).
2.  **Lead Research & Fact-Check Agent (Agent 1):** Analyze the raw input to extract core features, technical specs, and target audience. Output a structured "Fact-Sheet" (JSON or Markdown) and explicitly flag any ambiguous statements from the source.
3.  **Creative Copywriter Agent (Agent 2):** Using the Fact-Sheet, simultaneously generate a 500-word Blog Post (Professional/Trustworthy tone), a 5-post Social Media Thread (Engaging/Punchy tone), and a 1-paragraph Email Teaser. Ensure the core "Value Proposition" is highlighted in all formats.
4.  **Editor-in-Chief Agent (Agent 3):** Critique Agent 2's drafts against Agent 1's Fact-Sheet. Reject drafts that contain hallucinations (invented prices, features) or inappropriate tone. If rejected, send a specific Correction Note back to Agent 2 to trigger an automatic rewrite.
5.  **Agent Room Dashboard:** Display a real-time chat/feed interface mapping the workflow between agents. Use WebSockets to push live updates (e.g., "Copywriter is regenerating the Twitter thread based on Editor feedback").
6.  **Final Review View:** Present a clean layout showing the original source text alongside the final, approved drafts for the Blog, Social Thread, and Email.
7.  **Responsive Previews:** Provide a toggle to preview content as it would appear on a target device (e.g., mobile view for the social thread, desktop view for the blog).
8.  **Targeted Regeneration:** Allow users to click a "Regenerate" button on individual content pieces in the Final Review View. Provide an optional text input for users to give direct feedback to the AI for that specific piece.
9.  **Export & Delivery:** Provide a one-click action to download the compiled "Campaign Kit" as a zip archive and individual "Copy to Clipboard" buttons for each piece of content.

## 5. Non-Goals (Out of Scope)

*   **User Authentication:** No login or multi-tenant architecture is required for the MVP; this is an internal standalone tool.
*   **Direct Publishing APIs:** The system will not integrate directly with social media APIs (LinkedIn, X) or CMS platforms (WordPress) to auto-publish. Output is manual export only.
*   **Multimedia Processing:** The system will process text-based inputs only. Audio transcription or video analysis is out of scope.

## 6. Design Considerations

*   **Styling:** Use TailwindCSS for a modern, responsive interface.
*   **Agent Room:** Use distinct icons for each of the three agents. Incorporate CSS micro-animations (e.g., pulsing dots) to represent states like "Thinking" or "Typing".
*   **Review Layout:** Consider a split-screen or multi-pane layout to allow easy cross-referencing between the source material and the generated outputs.

## 7. Technical Considerations

*   **Backend Stack:** Python Django.
*   **AI Integration:** Use the official `python-genai` library (`https://googleapis.github.io/python-genai/`) to interface with the Gemini API.
*   **Asynchronous Real-Time Architecture:** 
    *   To prevent HTTP timeouts and provide the live "Agent Room" experience, use **Django Channels (WebSockets)**.
    *   The sequential multi-agent loop (Agent 1 -> Agent 2 -> Agent 3 -> optionally back to Agent 2) should run as an asynchronous background task (e.g., using Celery or an `asyncio` task within the Channels consumer).
    *   The background worker will push status updates over the WebSocket to the frontend as the agents interact.
*   **API Rate Limiting & Safeguards:** Implement strict retry limits for the Copywriter-Editor loop to prevent infinite generation loops and exploding Gemini API costs. Add delays or backoff strategies if API rate limits are hit.
*   **File Parsing:** Leverage lightweight Python libraries (like `PyPDF2` or `python-docx`) to handle document extraction before passing the text to Gemini.

## 8. Success Metrics

*   Decrease time spent creating multi-channel campaigns by 80% compared to manual execution.
*   High acceptance rate on the first Final Review, indicating the Editor-in-Chief agent is effectively catching errors.
*   Zero reported instances of the system publishing "hallucinated" features (verified by human review before export).

## 9. Open Questions

*   What are the strict token limits or file size maximums we should enforce at the upload stage?
*   Should we provide specific past marketing materials to be used as static "few-shot" examples in the Copywriter's system prompt to better match the exact company tone?
