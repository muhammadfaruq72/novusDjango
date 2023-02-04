from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync


class MyConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        print("Channel layer", self.channel_layer, self.channel_name)
        print("Connected!")
        await self.channel_layer.group_add("programmers", self.channel_name)

        await self.accept()
        await self.send_json(
            {
                "type": "welcome_message",
                "message": "Hey there! You've successfully connected!",
            }
        )

    async def disconnect(self, code):
        print("Disconnected!")

    async def receive_json(self, content, **kwargs):
        print(content['client'])
        # self.send_json({"message": "From server to Client"})
        await self.channel_layer.group_send("programmers", {
            "type": "chat.message",
            "message": content['client'],
        })
    
    async def chat_message(self, event):
        print("hat message Channel layer...", self.channel_layer, self.channel_name, event["message"])
        await self.send_json({"message": event['message']})




# from channels.consumer import AsyncConsumer
# from channels.exceptions import StopConsumer

# class MyConsumer(AsyncConsumer):

#     async def websocket_connect(self, event):
#         print("Channel layer", self.channel_layer, self.channel_name)

#         await self.channel_layer.group_add("programmers", self.channel_name)
        
#         await self.send({
#             "type": "websocket.accept",
#         })

       

#     async def websocket_receive(self, event):

        # await self.channel_layer.group_send("programmers", {
        #     "type": "chat.message",
        #     "message": event["text"],
        # })

        
    # async def chat_message(self, event):
    #     print("hat message Channel layer...", self.channel_layer, self.channel_name, event["message"])
    #     self.send({
    #         "type": "websocket.send",
    #         "text": event["message"],
    #     })


#     async def websocket_disconnect(self, event):
#          await self.channel_layer.group_discard("programmers", self.channel_name)
#          raise StopConsumer