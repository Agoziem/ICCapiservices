"""
the message CRUD operation is handled by the Websocket consumer in chatroom/consumers.py
the message will indicate the type of operation to be performed

if the message is a create operation, 
the message will contain the data to be saved in the database
the message will contain the user who sent the message
the message will contain the group to which the message belongs
the message will contain the type of message (text or file)
the message will contain the file to be saved in the database
the message will contain the body of the message
the message will contain the message id

if the message is a delete operation,
the message will contain the message id to be deleted
the message will contain the group to which the message belongs
the message will contain the user who sent the message

if the message is an update operation,
the message will contain the message id to be updated
the message will contain the group to which the message belongs
the message will contain the user who sent the message
the message will contain the data to be updated in the database
the message will contain the type of message (text or file)
the message will contain the file to be saved in the database
the message will contain the body of the message

for reply operation,
the message will contain the message id to be replied to
the message will contain the group to which the message belongs
the message will contain the user who sent the message
the message will contain the data to be saved in the database
the message will contain the type of message (text or file)
the message will contain the file to be saved in the database
the message will contain the body of the message

for seen operation,
the message will contain the message id to be marked as seen
the message will contain the group to which the message belongs
the message will contain the user who sent the message

for typing operation,
the message will contain the group to which the message belongs
the message will contain the user who sent the message
the message will contain the typing status

"""

import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from .models import ChatGroup, GroupMessage

User = get_user_model()

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        self.group = ChatGroup.objects.get(group_name=self.group_name)

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        operation = data.get('operation')
        user = User.objects.get(username=data['user'])

        if operation == 'create':
            self.create_message(data, user)
        elif operation == 'delete':
            self.delete_message(data)
        elif operation == 'update':
            self.update_message(data)
        elif operation == 'reply':
            self.reply_to_message(data, user)
        elif operation == 'seen':
            self.mark_as_seen(data, user)
        elif operation == 'typing':
            self.typing_status(data, user)

    def create_message(self, data, user):
        message_type = data['type']
        body = data.get('body', '')
        file = data.get('file')
        group = ChatGroup.objects.get(group_name=data['group'])

        if message_type == 'text':
            message = GroupMessage.objects.create(
                group=group,
                author=user,
                body=body,
                type='text'
            )
        else:
            message = GroupMessage.objects.create(
                group=group,
                author=user,
                type=message_type,
                file=file if message_type == 'file' else None,
                image=file if message_type == 'image' else None,
            )

        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'user': user.username,
                    'body': message.body,
                    'type': message.type,
                    'file': message.filename,
                    'created': str(message.created),
                }
            }
        )

    def delete_message(self, data):
        message_id = data['message_id']
        group = ChatGroup.objects.get(group_name=data['group'])

        try:
            message = GroupMessage.objects.get(id=message_id, group=group)
            message.delete()
        except GroupMessage.DoesNotExist:
            pass

        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'delete_message',
                'message_id': message_id
            }
        )

    def update_message(self, data):
        message_id = data['message_id']
        body = data.get('body', '')
        file = data.get('file')
        group = ChatGroup.objects.get(group_name=data['group'])

        try:
            message = GroupMessage.objects.get(id=message_id, group=group)
            message.body = body
            if file:
                if message.type == 'file':
                    message.file = file
                elif message.type == 'image':
                    message.image = file
            message.save()
        except GroupMessage.DoesNotExist:
            pass

        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'user': message.author.username,
                    'body': message.body,
                    'type': message.type,
                    'file': message.filename,
                    'created': str(message.created),
                }
            }
        )

    def reply_to_message(self, data, user):
        message_id = data['message_id']
        group = ChatGroup.objects.get(group_name=data['group'])
        body = data.get('body', '')
        file = data.get('file')

        try:
            reply_to_message = GroupMessage.objects.get(id=message_id, group=group)
            message = GroupMessage.objects.create(
                group=group,
                author=user,
                body=body,
                type=data['type'],
                file=file if data['type'] == 'file' else None,
                image=file if data['type'] == 'image' else None,
                is_reply=True,
                reply_to=reply_to_message
            )
        except GroupMessage.DoesNotExist:
            pass

        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'user': message.author.username,
                    'body': message.body,
                    'type': message.type,
                    'file': message.filename,
                    'reply_to': message.reply_to.id if message.reply_to else None,
                    'created': str(message.created),
                }
            }
        )

    def mark_as_seen(self, data, user):
        message_id = data['message_id']
        group = ChatGroup.objects.get(group_name=data['group'])

        try:
            message = GroupMessage.objects.get(id=message_id, group=group)
            message.users_seen.add(user)
        except GroupMessage.DoesNotExist:
            pass

        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'mark_seen',
                'message_id': message_id,
                'user': user.username
            }
        )

    def typing_status(self, data, user):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'typing_status',
                'user': user.username,
                'status': data['typing_status']
            }
        )

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'operation': 'create',
            'message': message
        }))

    def delete_message(self, event):
        message_id = event['message_id']
        self.send(text_data=json.dumps({
            'operation': 'delete',
            'message_id': message_id
        }))

    def mark_seen(self, event):
        message_id = event['message_id']
        user = event['user']
        self.send(text_data=json.dumps({
            'operation': 'seen',
            'message_id': message_id,
            'user': user
        }))

    def typing_status(self, event):
        user = event['user']
        status = event['status']
        self.send(text_data=json.dumps({
            'operation': 'typing',
            'user': user,
            'status': status
        }))

