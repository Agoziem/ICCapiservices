from typing import Optional, List, Dict, Any
from pydantic import Field
from ninja import Schema, ModelSchema
from datetime import datetime
from enum import Enum

from whatsappAPI.admin import WAMessage
from whatsappAPI.models import Contact, Status, WATemplateSchema, WebhookEvent


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




# WAMessage Schemas
class WAMessageSchema(ModelSchema):
    class Meta:
        model = WAMessage
        fields = ["id", "message_id", "contact", "message_type", "body", "media_id", 
                 "mime_type", "filename", "animated", "caption", "link", "message_mode", 
                 "seen", "status", "timestamp"]
        
class WAMessageMiniSchema(Schema):
    id: int
    message_id: str
    message_type: MessageType
    body: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class CreateWAMessageSchema(Schema):
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


class UpdateWAMessageSchema(Schema):
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
class StatusSchema(ModelSchema):
    class Meta:
        model = Status
        fields = ["id", "message", "status", "timestamp"]


class CreateStatusSchema(Schema):
    message: int  # WAMessage ID
    status: str

# Contact Schemas
class ContactSchema(ModelSchema):
    last_message: Optional[WAMessageMiniSchema] = None
    unread_message_count: int = 0

    class Meta:
        model = Contact
        fields = ["id", "wa_id", "profile_name"]

    @classmethod
    def from_django_model(cls, contact):
        from django.utils.dateformat import DateFormat

        # Get last message
        last_message = None
        last_wa_message = contact.messages.order_by("-timestamp").first()
        if last_wa_message:
            last_message = WAMessageMiniSchema.model_validate(last_wa_message)

        # Get unread message count
        unread_count = contact.messages.filter(
            message_mode="received", seen=False
        ).count()

        # Create a dictionary with all the data
        data = {
            "id": contact.id,
            "wa_id": contact.wa_id,
            "profile_name": contact.profile_name,
            "last_message": last_message,
            "unread_message_count": unread_count,
        }
        
        # Return the schema instance using model_validate
        return cls.model_validate(data)


class CreateContactSchema(Schema):
    wa_id: str
    profile_name: Optional[str] = None


class UpdateContactSchema(Schema):
    wa_id: Optional[str] = None
    profile_name: Optional[str] = None



# WebhookEvent Schemas
class WebhookEventSchema(ModelSchema):
    class Meta:
        model = WebhookEvent
        fields = ["id", "event_id", "payload", "received_at"]


class CreateWebhookEventSchema(Schema):
    event_id: str
    payload: Dict[str, Any]


# WATemplateSchema Schemas
class WATemplateSchemaSchema(ModelSchema):
    class Meta:
        model = WATemplateSchema
        fields = ["id", "title", "template", "text", "link", "status", "created_at"]


class CreateWATemplateSchemaSchema(Schema):
    title: str = "No Title"
    template: TemplateType = TemplateType.textonly
    text: Optional[str] = None
    link: Optional[str] = None


class UpdateWATemplateSchemaSchema(Schema):
    title: Optional[str] = None
    template: Optional[TemplateType] = None
    text: Optional[str] = None
    link: Optional[str] = None
    status: Optional[MessageStatus] = None


# Webhook Payload Schemas
class WebhookPayloadSchema(Schema):
    entry: List[Dict[str, Any]] = Field(..., description="List of entry objects")


# Send Message Schemas
class SendMessageSchema(Schema):
    message_type: MessageType = MessageType.text
    body: Optional[str] = Field(None, description="Message text body")
    media_id: Optional[str] = Field(
        None, description="ID of media for non-text messages"
    )
    link: Optional[str] = Field(None, description="URL for media messages")


class TemplateMessageSchema(Schema):
    to_phone_number: str = Field(
        ..., description="Recipient's phone number with country code"
    )
    template_name: str = Field(..., description="Name of the template to use")
    language_code: str = Field("en_US", description="Language code for the template")


# Response Schemas
class ContactListResponseSchema(Schema):
    results: List[ContactSchema]


class WAMessageListResponseSchema(Schema):
    results: List[WAMessageSchema]


class WATemplateSchemaListResponseSchema(Schema):
    results: List[WATemplateSchemaSchema]


class StatusListResponseSchema(Schema):
    results: List[StatusSchema]


class WebhookEventListResponseSchema(Schema):
    results: List[WebhookEventSchema]


# Paginated Response Schemas
class PaginatedContactResponseSchema(Schema):
    count: int
    items: List[ContactSchema]


class PaginatedWAMessageResponseSchema(Schema):
    count: int
    items: List[WAMessageSchema]


class PaginatedWATemplateSchemaResponseSchema(Schema):
    count: int
    items: List[WATemplateSchemaSchema]


class PaginatedStatusResponseSchema(Schema):
    count: int
    items: List[StatusSchema]


class PaginatedWebhookEventResponseSchema(Schema):
    count: int
    items: List[WebhookEventSchema]


class SuccessResponseSchema(Schema):
    message: str


class ErrorResponseSchema(Schema):
    error: str


# Media Response Schema
class MediaResponseSchema(Schema):
    media_url: str
    mime_type: str
    success: bool = True


# WebSocket Message Schemas
class WebSocketMessageSchema(Schema):
    operation: str
    contact: Optional[ContactSchema] = None
    message: Optional[WAMessageSchema] = None
