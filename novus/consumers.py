from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async
import json
import re
from . import models


class MyConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        print("Channel layer", self.channel_layer, self.channel_name)
        

        Space = self.scope['subprotocols'][0]
        print("Connected!", Space)
        # for i in self.scope['headers']:
        #     if i[0].decode() == "payload":
        #         Headers = json.loads(i[1].decode())

        # # print(Headers)
        # channel = Headers['Channel']
        # pattern = r"[^A-Za-z0-9]+"
        # channel = re.sub(pattern, "", channel)
        # Space_and_Channel = (Space + channel).replace(" ", "")
        # # print(Space_and_Channel)
        

        await self.channel_layer.group_add(Space, self.channel_name)

        await self.accept()
        # await self.send_json(
        #     {
        #         "type": "welcome_message",
        #         "message": "Hey there! You've successfully connected!",
        #     }
        # )


        

        
    async def disconnect(self, code):
        print("Disconnected!")

    async def receive_json(self, content, **kwargs):
        print(content)

        # Headers = {}
        # for i in self.scope['headers']:
        #     if i[0].decode() == "payload":
        #         Headers = json.loads(i[1].decode())

        Space = self.scope['subprotocols'][0]

    #     # print(content)
        @sync_to_async
        def Get_DP():
            if content['ReplyUsername'] == None: return [models.CustomUser.objects.filter(username=content['username']).values()[0]["Image"], None]
            else: return [models.CustomUser.objects.filter(username=content['username']).values()[0]["Image"], models.CustomUser.objects.filter(username=content['ReplyUsername']).values()[0]["Image"]]
        try:
            DP = await Get_DP()
        except Exception as e: print(e)

        @sync_to_async
        def Channel_id():
            return models.Channels.objects.filter(Name=content['Channel'], Workspace_id=Space).values()[0]["id"]
        try:
            channel_id = await Channel_id()
        except Exception as e: print(e)

        @sync_to_async
        def CreateMessage():
            if content['ReplyUsername'] == None:
                n = models.Chat.objects.create(
                    Workspace_id=Space,
                    Channel_id=channel_id,
                    Username_id=content['username'],
                    Message=content['Message'],
                    ReplyUsername_id=None,
                    Reply=content['Reply'])
                broadcast_message = {
                    "Workspace": Space,
                    "Channel": {"Name": content['Channel']},
                    "Message": content['Message'],
                    "Username": {"username": content['username'], "Image": {"url": "/"+DP[0]}},
                    "ReplyUsername": None,
                    "Reply": content['Reply'],
                    "id": str(n.pk)

                }
                return broadcast_message
            else:
                n = models.Chat.objects.create(
                    Workspace_id=Space,
                    Channel_id=channel_id,
                    Username_id=content['username'],
                    Message=content['Message'],
                    ReplyUsername_id=content['ReplyUsername'],
                    Reply=content['Reply'])
                broadcast_message = {
                    "Workspace": Space,
                    "Channel": {"Name": content['Channel']},
                    "Message": content['Message'],
                    "Username": {"username": content['username'], "Image": {"url": "/"+DP[0]}},
                    "ReplyUsername": {"username": content['username'], "Image": {"url": "/"+DP[1]}},
                    "Reply": content['Reply'],
                    "id": str(n.pk)
                }
                return broadcast_message
        try:
            Create_Message = await CreateMessage()
            print(Create_Message)
        except Exception as e: print(e)
        

        
        
    #     # await self.send_json({"message": "From server to Client"})

        

        # print(Headers)
        # channel = content['Channel']
        # pattern = r"[^A-Za-z0-9]+"
        # channel = re.sub(pattern, "", channel)
        # Space_and_Channel = (Space + channel).replace(" ", "")
        # print(Space_and_Channel)

        await self.channel_layer.group_send(Space, {
            "type": "chat.message",
            "message": Create_Message,
        })
    
    async def chat_message(self, event):
        # print("hat message Channel layer...", self.channel_layer, self.channel_name, event["message"])
        await self.send_json({"message": event['message']})