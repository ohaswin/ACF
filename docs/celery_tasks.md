# Background Processing (Celery)

The multi-agent pipeline involves multiple sequential, slow external API calls. Directly blocking a user's HTTP request to wait for three Gemini agents to finish reading and drafting would result in widespread `504 Gateway Timeout` errors. 

The Autonomous Content Factory solves this by offloading the pipeline to **Celery**.

## Architecture & Configuration
Celery is a distributed task queue built for real-time operation and scheduling.
1. **Broker:** Celery uses Redis (`redis://127.0.0.1:6379/0`) as the message broker (`CELERY_BROKER_URL`). When Django calls `.delay()`, it simply dumps a message into a Redis list and immediately responds to the HTTP Request.
2. **Worker:** A separate long-running `celery worker` process constantly reads the Redis list. When it sees the task, it unpacks the parameters and executes it.
3. **Backend:** Celery writes the final state back to Redis (`CELERY_RESULT_BACKEND`), however, we primarily rely on our own SQLite state tracking (`Campaign.status`).

## The AI Orchestrator (`run_campaign_pipeline`)
The core task is defined in `campaigns/tasks.py`.

It receives the sterile integer `campaign_id` rather than a Django Model instance. This is a crucial Celery best practice: *Task arguments must be strictly JSON-serializable, and passing ORM instances risks database race conditions.*

### The Execution Loop
1. Fetch `Campaign.objects.get(id=campaign_id)`.
2. **Phase 1:** Trigger `run_agent_1_lead_research`. If it returns `None` (JSON parse failed), halt the entire task and abort.
3. **Phase 2:** Enter the Creative Loop over three requested channels: `['blog', 'social', 'email']`.
4. **Idempotency:** The task explicitly looks for `existing_piece.status == 'approved'`. If the user asked for a selective chunk regeneration of an *already generated* campaign, Celery will `continue` and skip channels that are already finished.
5. **Phase 3:** For unfinished channels, loop Agent 2 (Writer) and Agent 3 (Editor) up to `max_retries = 3` times. Pass the Editor's feedback recursively back into the Writer function on each failure.
6. **Completion:** When all channels are approved (or the retry ceiling is hit), set the global Campaign status to `completed` and exit.

## Production Considerations
Because the LLM pipeline executes blindly in the background, robust internal `.log` records are necessary. Celery `stdout` is captured to `/celery.log` by the `launch.sh` bash wrapper to diagnose hard crashes (e.g. Gemini 429 Too Many Requests errors), while standard operations are logged directly into the GUI Dashboard database logic.
