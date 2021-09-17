import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class ClassConsumer(WebsocketConsumer):
    def connect(self):
        self.class_name = self.scope['url_route']['kwargs']['class_name']
        self.class_group_name = 'class_%s' % self.class_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.class_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.class_group_name,
            self.channel_name
        )

    # Receive message from room group
    def post_message(self, event):
        post = event['post']
        self.send(text_data=json.dumps({
            'post': post,
        }))

    def comment_message(self, event):
        comment = event['comment']
        self.send(text_data=json.dumps({
            'comment': comment
        }))

    def announcement(self,event):
        announcement = event['announcement']
        self.send(text_data=json.dumps({
            'announcement': announcement
        }))
