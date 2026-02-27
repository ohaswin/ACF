import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CampaignDashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.campaign_id = self.scope['url_route']['kwargs']['campaign_id']
        self.room_group_name = f'campaign_{self.campaign_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from room group
    async def agent_log(self, event):
        message = event['message']
        agent_name = event['agent_name']
        timestamp = event.get('timestamp', '')
        status = event.get('status', '')

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'agent_name': agent_name,
            'timestamp': timestamp,
            'status': status
        }))
