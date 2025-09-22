import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from .models import TrackingUpdate, ChatMessage, TrackingHistory
from channels.db import database_sync_to_async


class TrackingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f"tracking_{self.order_id}"

        # Add this socket connection to group (order specific)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Send recent locations when someone joins
        latest_locations = await self.get_latest_locations(self.order_id)
        await self.send(text_data=json.dumps({
            "type": "init",
            "order_id": self.order_id,
            "latest_locations": latest_locations
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get("type")

        if msg_type == "location":
            latitude = data["latitude"]
            longitude = data["longitude"]
            sender = data["sender"]

            # Save to DB
            await self.save_location(self.order_id, latitude, longitude, sender)

            # Broadcast
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "location_update",
                    "latitude": latitude,
                    "longitude": longitude,
                    "sender": sender,
                    "timestamp": str(now())
                }
            )

        elif msg_type == "chat":
            message = data["message"]
            sender = data["sender"]

            # Save to DB
            await self.save_chat(self.order_id, message, sender)

            # Broadcast
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender": sender,
                    "timestamp": str(now())
                }
            )

    # ----------------- Event Handlers -----------------
    async def location_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "location",
            "latitude": event["latitude"],
            "longitude": event["longitude"],
            "sender": event["sender"],
            "timestamp": event["timestamp"]
        }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat",
            "message": event["message"],
            "sender": event["sender"],
            "timestamp": event["timestamp"]
        }))

    # ----------------- DB Save Methods -----------------
    @database_sync_to_async
    def save_location(self, order_id, latitude, longitude, sender):
        # Save latest (overwrite for sender)
        obj, created = TrackingUpdate.objects.update_or_create(
            order_id=order_id,
            sender=sender,
            defaults={
                "latitude": latitude,
                "longitude": longitude,
                "timestamp": now()
            }
        )
        # Save history (append always)
        TrackingHistory.objects.create(
            order_id=order_id,
            latitude=latitude,
            longitude=longitude,
            sender=sender,
            timestamp=now()
        )
        return obj

    @database_sync_to_async
    def save_chat(self, order_id, message, sender):
        ChatMessage.objects.create(
            order_id=order_id,
            message=message,
            sender=sender,
            timestamp=now()
        )

    @database_sync_to_async
    def get_latest_locations(self, order_id):
        """ Return last known locations of all participants in this order """
        updates = TrackingUpdate.objects.filter(order_id=order_id)
        return [
            {
                "sender": u.sender,
                "latitude": u.latitude,
                "longitude": u.longitude,
                "timestamp": str(u.timestamp)
            }
            for u in updates
        ]
