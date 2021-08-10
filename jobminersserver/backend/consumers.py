# from jobminersserver.requestutils.requestgooglemodule.requestgoogle import RequestGoogle
# import json

from channels.generic.websocket import WebsocketConsumer

class JobMinersConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        pass

    def receive(self):
        print("received")