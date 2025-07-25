from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from ninja import Schema
from datetime import datetime
from enum import Enum


# Enums for choices
class MessageType(str, Enum):
    text = "text"
    image = "image"
    video = "video"
    audio = "audio"
    document = "document"
    sticker = "sticker"


class MessageMode(str, Enum):
    received = "received"
    sent = "sent"


class MessageStatus(str, Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"


class TemplateType(str, Enum):
    textonly = "textonly"
    textwithimage = "textwithimage"
    textwithvideo = "textwithvideo"
    textwithaudio = "textwithaudio"
    textwithdocument = "textwithdocument"
    textwithCTA = "textwithCTA"


# Contact Schemas
class ContactSchema(BaseModel):
    id: int
    wa_id: str
    profile_name: Optional[str] = None
    last_message: Optional[Dict[str, Any]] = None
    unread_message_count: int = 0

    class Config:
        from_attributes = True

    @classmethod
    def from_django_model(cls, contact):
        from django.utils.dateformat import DateFormat
        
        # Get last message
        last_message = None
        last_wa_message = contact.messages.order_by('-timestamp').first()
        if last_wa_message:
            last_message = {
                'id': last_wa_message.id,
                'message_id': last_wa_message.message_id,
                'message_type': last_wa_message.message_type,
                'body': last_wa_message.body,
                'timestamp': DateFormat(last_wa_message.timestamp).format('Y-m-d H:i:s')
            }
        
        # Get unread message count
        unread_count = contact.messages.filter(message_mode='received', seen=False).count()
        
        return cls(
            id=contact.id,
            wa_id=contact.wa_id,
            profile_name=contact.profile_name,
            last_message=last_message,
            unread_message_count=unread_count
        )


class CreateContactSchema(BaseModel):
    wa_id: str
    profile_name: Optional[str] = None


class UpdateContactSchema(BaseModel):
    wa_id: Optional[str] = None
    profile_name: Optional[str] = None


# WAMessage Schemas
class WAMessageSchema(BaseModel):
    id: int
    message_id: str
    contact: int  # Contact ID
    message_type: MessageType = MessageType.text
    body: str = ""
    media_id: str = ""
    mime_type: str = ""
    filename: str = ""
    animated: bool = False
    caption: str = ""
    link: str = "https://www.example.com"
    message_mode: MessageMode = MessageMode.received
    seen: bool = False
    status: MessageStatus = MessageStatus.pending
    timestamp: datetime

    class Config:
        from_attributes = True


class CreateWAMessageSchema(BaseModel):
    message_id: str
    contact: int  # Contact ID
    message_type: MessageType = MessageType.text
    body: str = ""
    media_id: str = ""
    mime_type: str = ""
    filename: str = ""
    animated: bool = False
    caption: str = ""
    link: str = "https://www.example.com"
    message_mode: MessageMode = MessageMode.received
    seen: bool = False
    status: MessageStatus = MessageStatus.pending


class UpdateWAMessageSchema(BaseModel):
    message_type: Optional[MessageType] = None
    body: Optional[str] = None
    media_id: Optional[str] = None
    mime_type: Optional[str] = None
    filename: Optional[str] = None
    animated: Optional[bool] = None
    caption: Optional[str] = None
    link: Optional[str] = None
    message_mode: Optional[MessageMode] = None
    seen: Optional[bool] = None
    status: Optional[MessageStatus] = None


# Status Schemas
class StatusSchema(BaseModel):
    id: int
    message: int  # WAMessage ID
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True


class CreateStatusSchema(BaseModel):
    message: int  # WAMessage ID
    status: str


# WebhookEvent Schemas
class WebhookEventSchema(BaseModel):
    id: int
    event_id: str
    payload: Dict[str, Any]
    received_at: datetime

    class Config:
        from_attributes = True


class CreateWebhookEventSchema(BaseModel):
    event_id: str
    payload: Dict[str, Any]


# WATemplateSchema Schemas
class WATemplateSchemaSchema(BaseModel):
    id: int
    title: str = "No Title"
    template: TemplateType = TemplateType.textonly
    text: Optional[str] = None
    link: Optional[str] = None
    status: MessageStatus = MessageStatus.pending
    created_at: datetime

    class Config:
        from_attributes = True


class CreateWATemplateSchemaSchema(BaseModel):
    title: str = "No Title"
    template: TemplateType = TemplateType.textonly
    text: Optional[str] = None
    link: Optional[str] = None


class UpdateWATemplateSchemaSchema(BaseModel):
    title: Optional[str] = None
    template: Optional[TemplateType] = None
    text: Optional[str] = None
    link: Optional[str] = None
    status: Optional[MessageStatus] = None


# Webhook Payload Schemas
class WebhookPayloadSchema(BaseModel):
    entry: List[Dict[str, Any]] = Field(..., description="List of entry objects")


# Send Message Schemas
class SendMessageSchema(BaseModel):
    message_type: MessageType = MessageType.text
    body: Optional[str] = Field(None, description="Message text body")
    media_id: Optional[str] = Field(None, description="ID of media for non-text messages")
    link: Optional[str] = Field(None, description="URL for media messages")


class TemplateMessageSchema(BaseModel):
    to_phone_number: str = Field(..., description="Recipient's phone number with country code")
    template_name: str = Field(..., description="Name of the template to use")
    language_code: str = Field("en_US", description="Language code for the template")


# Response Schemas
class ContactListResponseSchema(BaseModel):
    results: List[ContactSchema]


class WAMessageListResponseSchema(BaseModel):
    results: List[WAMessageSchema]


class WATemplateSchemaListResponseSchema(BaseModel):
    results: List[WATemplateSchemaSchema]


class StatusListResponseSchema(BaseModel):
    results: List[StatusSchema]


class WebhookEventListResponseSchema(BaseModel):
    results: List[WebhookEventSchema]


class SuccessResponseSchema(BaseModel):
    message: str


class ErrorResponseSchema(BaseModel):
    error: str


# Media Response Schema
class MediaResponseSchema(BaseModel):
    media_url: str
    mime_type: str
    success: bool = True


# WebSocket Message Schemas
class WebSocketMessageSchema(BaseModel):
    operation: str
    contact: Optional[ContactSchema] = None
    message: Optional[WAMessageSchema] = None