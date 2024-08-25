# Chatroom WebSocket Documentation

## Overview

This document provides an overview of the WebSocket consumer implemented in the `chatroom/consumers.py` file. It explains the WebSocket operations supported for managing messages within chat groups and outlines how the frontend can interact with these operations.

The WebSocket consumer is designed to handle message-related CRUD (Create, Read, Update, Delete) operations, as well as additional features like marking messages as seen, replying to messages, and tracking typing status.

## WebSocket URL Routing

The WebSocket connection is managed through URL routing, which is defined in the `chatroom/routing.py` file. The WebSocket connection URL pattern is as follows:

```python
from django.urls import path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    path('ws/chat/<str:group_name>/', ChatConsumer.as_asgi()),
]
```

- **`<str:group_name>`**: This parameter in the URL identifies the chat group the WebSocket connection is associated with.

## WebSocket Consumer Operations

### 1. **Connection and Disconnection**

- **`connect`**: When a WebSocket connection is established, the user joins the specified chat group, identified by the `group_name` in the URL. The user is then added to the channel group.

- **`disconnect`**: When the WebSocket connection is closed, the user is removed from the channel group.

### 2. **Receiving Messages**

The WebSocket consumer listens for incoming messages and determines the operation to perform based on the `operation` field in the received JSON payload. The following operations are supported:

### 2.1. **Create Operation**

**Description**: Creates a new message in the chat group.

**Payload Structure**:
```json
{
    "operation": "create",
    "user": "user id",
    "type": "text or file",
    "body": "Message content",
    "file": "file data (optional)"
}
```

- **`user`**: The username of the message sender.
- **`group`**: The name of the chat group where the message is sent.
- **`type`**: The type of message (e.g., `text`, `file`, `image`).
- **`body`**: The textual content of the message.
- **`file`**: The file to be attached to the message, if any.

**Response**: Broadcasts the created message to all users in the group.

### 2.2. **Delete Operation**

**Description**: Deletes a message from the chat group.

**Payload Structure**:
```json
{
    "operation": "delete",
    "user": "user id",
    "message_id": "ID of the message to be deleted"
}
```

- **`message_id`**: The ID of the message to be deleted.

**Response**: Broadcasts a delete notification to all users in the group.

### 2.3. **Update Operation**

**Description**: Updates an existing message in the chat group.

**Payload Structure**:
```json
{
    "operation": "update",
    "user": "user id",
    "message_id": "ID of the message to be updated",
    "body": "Updated message content",
    "file": "Updated file data (optional)"
}
```

- **`message_id`**: The ID of the message to be updated.
- **`body`**: The updated textual content of the message.
- **`file`**: The updated file to be attached to the message, if any.

**Response**: Broadcasts the updated message to all users in the group.

### 2.4. **Reply Operation**

**Description**: Sends a reply to an existing message in the chat group.

**Payload Structure**:
```json
{
    "operation": "reply",
    "user": "user id",
    "message_id": "ID of the message being replied to",
    "type": "text or file",
    "body": "Reply content",
    "file": "file data (optional)"
}
```

- **`message_id`**: The ID of the message being replied to.
- **`type`**: The type of the reply message (e.g., `text`, `file`, `image`).
- **`body`**: The textual content of the reply message.
- **`file`**: The file to be attached to the reply, if any.

**Response**: Broadcasts the reply message to all users in the group.

### 2.5. **Seen Operation**

**Description**: Marks a message as seen by the user.

**Payload Structure**:
```json
{
    "operation": "seen",
    "user": "user id",
    "message_id": "ID of the message to be marked as seen"
}
```

- **`message_id`**: The ID of the message to be marked as seen.

**Response**: Broadcasts a "seen" notification to all users in the group.

### 2.6. **Typing Operation**

**Description**: Indicates that a user is typing a message in the chat group.

**Payload Structure**:
```json
{
    "operation": "typing",
    "user": "user id",
    "typing_status": "status (e.g., typing, not_typing)"
}
```

- **`typing_status`**: The typing status (e.g., `typing`, `not_typing`).

**Response**: Broadcasts the typing status to all users in the group.

## Broadcasting and Receiving Events

The consumer can broadcast various events to all users in a group using the `group_send` method. These events trigger corresponding methods in the consumer that handle specific operations. For example:

- **`chat_message`**: Broadcasts a newly created, updated, or replied message.
- **`delete_message`**: Broadcasts a message deletion event.
- **`mark_seen`**: Broadcasts a message seen event.
- **`typing_status`**: Broadcasts a typing status event.

### Example Event Handling in the Frontend

When a message is created, updated, or replied to, the frontend receives a WebSocket message in the following format:

```json
{
    "operation": "create",
    "message": {
        "id": "message_id",
        "user": "user_id",
        "body": "Message content",
        "type": "text or file",
        "file": "filename (optional)",
        "reply_to": "ID of replied message (if any)",
        "created": "timestamp"
    }
}
```

The frontend can then parse this JSON and update the chat interface accordingly.

## Conclusion

This documentation provides a comprehensive guide for frontend engineers to understand and interact with the WebSocket consumer for chat operations. By following the outlined operations and handling the corresponding events, the frontend can seamlessly integrate with the chatroom backend to provide real-time messaging functionality.