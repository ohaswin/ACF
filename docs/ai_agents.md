# AI Agents & Pipelines

The core of the Autonomous Content Factory is a multi-stage pipeline utilizing the `google-genai` SDK and the `gemini-2.5-flash` model. We chose Flash for its speed, low latency, and robust JSON-parsing abilities critical to our structured data extraction needs.

The logic resides almost entirely in `campaigns/agents.py`.

## Prompt Engineering Philosophy
Generative models can be unpredictable. To ensure stability in an automated pipeline, we employ **role-based prompting** and strict output constraints. Each agent is completely unaware of the other agents; they only receive the specific context required to do their job.

### Agent 1: Lead Research & Fact-Check
**Goal:** Ingest unstructured human text (PDFs, URLs, raw brain dumps) and extract the "Source of Truth."
**Input:** Raw Text from `Campaign.source_text`.
**Output:** A strict JSON string defining the campaign's features, specs, audience, and value props.

Agent 1 forces the LLM to act as an objective researcher. It actively searches for and flags ambiguous or contradictory statements. By forcing the LLM to output pure JSON, we deserialize the response into a Python dictionary (`json.loads()`) and store it securely in the PostgreSQL/SQLite `JSONField` as the `fact_sheet`.

### Agent 2: Creative Copywriter
**Goal:** Take the sterile JSON `fact_sheet` and generate marketing copy tailored for specific channels (Blog, Social Media Thread, Email Teaser).
**Input:** The JSON `fact_sheet`.
**Output:** Markdown-formatted text.

Agent 2 is triggered multiple times (in a loop) for each required channel. We define a dictionary of `channel_instructions` (Tone: Professional vs. Engaging vs. Direct) and inject it into the prompt. Crucially, Agent 2 is instructed that the "Value Proposition" from the fact sheet *must* be the hero of the text.

### Agent 3: Editor-in-Chief
**Goal:** Act as a quality-assurance gatekeeper. Validate Agent 2's output against Agent 1's facts.
**Input:** The JSON `fact_sheet` AND Agent 2's Draft Content.
**Output:** A strict JSON string containing `{"approved": true/false, "feedback": "Correction notes"}`.

Agent 3 performs a "Hallucination Check" to ensure no new prices, timelines, or features were invented by the Copywriter. It also performs a "Tone Audit" to ensure the text matches the channel requirements.

If `approved` is true, the `ContentPiece` state advances. If false, the `feedback` string is saved to the database.

## Orchestration Loop & Retries

The multi-agent system runs until the Editor is satisfied, up to a hardcoded `max_retries = 3` limit.

1. **Agent 2 Drafts:** Generate copy.
2. **Agent 3 Reviews:** Critique the copy against the Fact Sheet.
3. **Rejection Handling:** If rejected, the orchestrator appends a special block to Agent 2's prompt on the next iteration: `PREVIOUS DRAFT REJECTED! Please apply this feedback from the Editor-in-Chief: [feedback]`.
4. **Infinite Loop Prevention:** If Agent 3 continues to reject the copy after 3 attempts, the pipeline deliberately bails out, marking the piece as `failed` to prevent infinite LLM billing loops.

## Handling LLM Failures
We explicitly wrap all `json.loads(response.text)` calls in `try/except json.JSONDecodeError` blocks. If Gemini returns conversational text instead of raw JSON (e.g., `Here is the JSON you requested: { ... }`), the parse fails. 

When this happens on Agent 1, the entire pipeline is halted. When this happens on Agent 3, we default to "Rejected" with a generic system error, forcing a safe retry.
