import json
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.authentication import JWTAuthentication

class LiveRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.class_name = self.scope['url_route']['kwargs']['class_name']
        self.class_group_name = 'class_%s' % self.class_name
        # print(self.scope['user'].id)

        if self.scope['user'] is None:
            await self.close()

        else:
            await self.channel_layer.group_add(
                self.class_group_name,
                self.channel_name
            )

            await self.accept()

    # @sync_to_async
    # def authenticate_socket(self):
    #     try:
    #         jwt_auth = JWTAuthentication()
    #         raw_token = self.scope['cookies'].get('token')
    #         validated_token = jwt_auth.get_validated_token(raw_token)
    #         return jwt_auth.get_user(validated_token)
    #     except Exception as e:
    #         return None
        # Join room group

    async def disconnect(self, close_code):
        # Leave the video call group
        await self.channel_layer.group_discard(
            self.class_group_name,
            self.channel_name
        )


    # Receive message from room group
    async def post_message(self, event):
        post = event['post']
        await self.send(text_data=json.dumps({
            'post': post,
        }))

    async def comment_message(self, event):
        comment = event['comment']
        await self.send(text_data=json.dumps({
            'comment': comment
        }))

    async def announcement(self,event):
        announcement = event['announcement']
        await self.send(text_data=json.dumps({
            'announcement': announcement
        }))



class VideoRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.class_name = self.scope['url_route']['kwargs']['class_name']
        self.class_group_name = 'video_%s' % self.class_name

        if self.scope['user'] is None:
            await self.close()

        else:
            # Join room group
            await self.channel_layer.group_add(
                self.class_group_name,
                self.channel_name
            )

            await self.accept()

    async def disconnect(self, close_code):
        # Leave the video call group
        await self.channel_layer.group_discard(
            self.class_group_name,
            self.channel_name
        )


    # Receive SDP offers, answers, and ICE candidates from the frontend
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        print(data)
        if message_type == 'offer':
            # Handle SDP offer and send it to the appropriate participant(s)
            await self.handle_offer(data)
        elif message_type == 'answer':
            # Handle SDP answer and send it to the appropriate participant(s)
            await self.handle_answer(data)
        elif message_type == 'ice_candidate':
            # Handle ICE candidate and send it to the appropriate participant(s)
            await self.handle_ice_candidate(data)
        elif message_type == 'join_room_ack':
            # Handle ICE candidate and send it to the appropriate participant(s)
            await self.handle_join_room_reqs(data)
        elif message_type == 'join_room_allow':
            # Handle ICE candidate and send it to the appropriate participant(s)
            await self.handle_join_room_allows(data)

    async def handle_offer(self, data):
        # Get the participant's room name and send the offer to that room
        participant_room = data['class_name']
        id = self.scope['user'].id

        await self.channel_layer.group_send(
            'video_%s' % participant_room,
            {
                'type': 'send_offer',
                'id': id,
                'offer': data['sdp'],
                'participant_channel': self.channel_name
            }
        )

    # Handle SDP answer and send it to the appropriate participant(s)
    async def handle_answer(self, data):
        # Get the participant's room name and send the answer to that room

        participant_room = data['class_name']
        id = self.scope['user'].id
        await self.channel_layer.group_send(
            'video_%s' % participant_room,
            {
                'type': 'send_answer',
                'id': id,
                'answer': data['sdp'],
                'participant_channel': self.channel_name
            }
        )

    # Handle ICE candidate and send it to the appropriate participant(s)
    async def handle_ice_candidate(self, data):
        # Get the participant's room name and send the ICE candidate to that room
        participant_room = data['class_name']
        id = self.scope['user'].id
        candidate = data['sdp']
        print(candidate)
        await self.channel_layer.group_send(
            'video_%s' % participant_room,
            {
                'type': 'send_ice_candidate',
                'candidate': candidate,
                'id': id,
                'participant_channel': self.channel_name
            }
        )

    async def handle_join_room_reqs(self, data):
        # Get the participant's room name and send the answer to that room

        participant_room = data['class_name']
        id = self.scope['user'].id
        await self.channel_layer.group_send(
            'video_%s' % participant_room,
            {
                'type': 'send_join_room_ack',
                'id': id,
                # 'participant_channel': self.channel_name
            }
        )

    async def handle_join_room_allows(self, data):
        # Get the participant's room name and send the answer to that room

        participant_room = data['class_name']
        id = self.scope['user'].id
        for_user = data['for_user']
        await self.channel_layer.group_send(
            'video_%s' % participant_room,
            {
                'type': 'send_join_room_allow',
                'id': id,
                'for_user': for_user
                # 'participant_channel': self.channel_name
            }
        )



    # Receive SDP offer and send it to the participant(s) in the room
    async def send_offer(self, event):
        await self.send(text_data=json.dumps({
            'type': 'offer',
            'id': event['id'],
            'sdp': event['offer']
        }))

    # Receive SDP answer and send it to the participant(s) in the room
    async def send_answer(self, event):
        await self.send(text_data=json.dumps({
            'type': 'answer',
            'id': event['id'],
            'sdp': event['answer']
        }))

    # Receive ICE candidate and send it to the participant(s) in the room
    async def send_ice_candidate(self, event):
        await self.send(text_data=json.dumps({
            'type': 'ice_candidate',
            'id': event['id'],
            'candidate': event['candidate']
        }))

    async def send_join_room_ack(self, event):
        await self.send(text_data=json.dumps({
            'type': 'join_room_ack',
            'id': event['id'],
        }))

    async def send_join_room_allow(self, event):
        await self.send(text_data=json.dumps({
            'type': 'join_room_allow',
            'id': event['id'],
            'for_user': event['for_user']
        }))
