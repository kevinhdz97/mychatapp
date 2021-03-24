from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatRoomConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]

        # this is going to be the GROUP in which we are going to place the users' reply_channels so that we can send messages to this GROUP
        self.room_group_name = f"chat_{self.room_name}"

        # The channel_name attribute contains a pointer to the channnel layer instance and the channel name that will reach the consumer
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Handshake before sending messages
        await self.accept()

        # As soon as we connect we are going to send a message to the group
        # we are going to send json
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'tester_message',
                'tester': 'This is our first testing message',
            }
        )
    
    # Notice that this is the type of message that we defined when we sent something to the group
    async def tester_message(self, event):
        tester = event["tester"]

        await self.send(text_data=json.dumps({
            "tester": tester,
        }))

    async def disconnect(self, close_code):

        # The group name that we are going to discard
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # The information we got from user
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user_name = text_data_json["user"]

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type":"chat_message",
                "message": f"{user_name}: {message}"
            }
        )

    async def chat_message(self, event):
        message = event["message"]

        await self.send(text_data=json.dumps(
            {
                "message":message,
            }
        ))

    