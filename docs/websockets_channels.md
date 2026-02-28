# Real-Time Updates (Django Channels)

To deliver a transparent "AI Assembly Line" experience, the dashboard needs to reflect the internal state of the background Celery workers instantly. Standard HTTP polling (e.g., AJAX every 2 seconds) is inefficient and scales poorly. Instead, we use **Django Channels** to maintain a persistent, bidirectional WebSocket connection between the browser and the server.

## 1. ASGI vs. WSGI
Traditional Django runs on WSGI (Web Server Gateway Interface), which is strictly synchronous. Channels requires ASGI (Asynchronous Server Gateway Interface) to handle long-lived connections. We use the Daphne ASGI server.
Our `config/asgi.py` routes incoming traffic:
- Standard HTTP traffic goes to standard Django views.
- WebSocket traffic (`ws://`) is intercepted and handed to our `URLRouter` defined in `campaigns/routing.py`.

## 2. Consumers (`campaigns/consumers.py`)
A Consumer is the WebSocket equivalent of a Django View. The `CampaignDashboardConsumer` inherits from `AsyncWebsocketConsumer`.

1. **Connection:** When a user opens the Dashboard (`/campaign/ID/`), JavaScript opens a WebSocket to `/ws/campaigns/ID/`.
2. **Channel Groups:** Upon `connect()`, the Consumer grabs the campaign ID from the URL kwargs and subscribes the user's connection to a Redis Channel Group named `campaign_ID`. It then `accept()`s the connection.
3. **Disconnection:** When the user closes the tab, `disconnect()` removes them from the Redis group.

## 3. The Redis Channel Layer
The tricky part of out-of-band architecture: *How does a separate Celery process talk to Daphne?* 

Daphne doesn't know about Celery, and Celery isn't running an HTTP server.

We use **Redis** as a Channel Layer (`channels_redis.core.RedisChannelLayer`).

When the Celery Worker (executing `run_campaign_pipeline.delay()`) invokes `log_agent_action()`, we do two things:
1. Save the log message to the SQLite database (for persistence).
2. Execute an `async_to_sync` group send to the `campaign_ID` Redis group.

```python
# from campaigns/utils.py
channel_layer = get_channel_layer()
async_to_sync(channel_layer.group_send)(
    room_group_name,
    {
        'type': 'campaign_message', # triggers campaign_message() on the Consumer
        'message': message,
        'agent_name': agent_name,
        'timestamp': log_entry.created_at.strftime("%H:%M:%S")
    }
)
```

## 4. Frontend Subscription & Rendering
On the client side (`dashboard.html`), Vanilla JavaScript maintains the open socket (`chatSocket = new WebSocket(...)`). 
When a broadcast arrives on `chatSocket.onmessage`, the JS parses the JSON payload, dynamically updates the relevant Agent's SVG pulse animation ("Working...", "Critiquing..."), and appends the new log line to the live feed div.
