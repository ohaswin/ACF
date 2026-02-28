# Autonomous Content Factory Documentation

Welcome to the internal documentation for the **Autonomous Content Factory** MVP. This directory serves as a comprehensive guide to understanding the architecture, design decisions, and specific code implementations of the platform.

## Overview
The Autonomous Content Factory is an automated, multi-agent AI pipeline built to resolve "Creative Burnout" for marketing teams. By inputting a single source document (PDF, Text, or URL), an assembly line of specialized AI agents analyzes the text, extracts a factual "Source of Truth," and instantly generates a coordinated, multi-channel marketing campaign (Blog Post, Social Media Thread, and Email Teaser). 

The platform provides a real-time, transparent UI that allows users to watch the AI agents collaborate, critique each other, and iterate on drafts before final approval.

## Table of Contents

If you are reviewing this codebase, please explore the deep dives below:

1. **[System Architecture](architecture.md)** 
   - High-level design (Django, Celery, Channels, Redis)
   - The asynchronous request lifecycle
   - Idempotent startup script (`launch.sh`)

2. **[AI Agents & Prompt Engineering](ai_agents.md)**
   - Gemini 2.5 Flash Integration
   - Breakdowns of Agent 1 (Research), Agent 2 (Copywriter), and Agent 3 (Editor-in-Chief)
   - Structured JSON output enforcement

3. **[Real-Time Updates (Django Channels)](websockets_channels.md)**
   - WebSockets vs. HTTP
   - ASGI configuration (`asgi.py`, `routing.py`, `consumers.py`)
   - Cross-process communication using `RedisChannelLayer`

4. **[Background Processing (Celery)](celery_tasks.md)**
   - Why Celery is necessary for LLM pipelines
   - The orchestrator loop (`tasks.py`)
   - Retry limits and failure handling

5. **[Database Schema (Models)](data_models.md)**
   - Overview of `Campaign`, `ContentPiece`, and `AgentLog` models
   - State tracking and relationships

## Tech Stack Summary
- **Backend Framework:** Django 6.0.2
- **Asynchronous Task Queue:** Celery 5.6.2
- **Message Broker & Cache:** Redis 7.2.1
- **Real-Time Communication:** Django Channels 4.3.0 & Daphne 4.2.1
- **AI/LLM Provider:** Google GenAI SDK (Gemini 2.5 Flash)
- **Frontend:** HTML, TailwindCSS, Vanilla JavaScript (WebSockets)
