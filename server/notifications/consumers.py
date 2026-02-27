import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    # async def connect(self):
    #     user = self.scope["user"]
    #     if user.is_authenticated:
    #         self.group_name = f'notifications_{user.id}'
    #         await self.channel_layer.group_add(
    #             self.group_name,
    #             self.channel_name
    #         )
    #         await self.accept()
    #     else:
    #         await self.close()
    async def connect(self):
        user = self.scope.get("user")
        qs = self.scope.get("query_string", b"").decode()
        path = self.scope.get("path")
        print(f"[WS] connect() path={path} qs='{qs[:100]}' user={user} id={getattr(user, 'id', None)}")

        if user and getattr(user, "is_authenticated", False):
            self.group_name = f"notifications_{user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            print(f"[WS] ACCEPT user_id={user.id} group={self.group_name}")
            await self.accept()
        else:
            print("[WS] CLOSE: anonymous user")
            await self.close(code=4001)  # fecha com um code que você reconhece

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        # opcional: pode deixar vazio se só quiser enviar do back pro front
        pass

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'title': event['title'],
            'message': event['message'],
            'type': event['type'],
            'link': event['link'],
        }))
