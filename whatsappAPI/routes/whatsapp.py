from typing import Optional, List, Dict, Any
from ninja_extra import api_controller, route
from ninja_extra.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import StreamingHttpResponse
from django.conf import settings
import requests

from ..models import Contact, WAMessage, WATemplateSchema, Status, WebhookEvent
from ..schemas import (
    ContactSchema, ContactListResponseSchema,
    CreateContactSchema, UpdateContactSchema,
    WAMessageSchema, WAMessageListResponseSchema,
    CreateWAMessageSchema, UpdateWAMessageSchema,
    WATemplateSchemaSchema, WATemplateSchemaListResponseSchema,
    CreateWATemplateSchemaSchema, UpdateWATemplateSchemaSchema,
    StatusSchema, StatusListResponseSchema,
    WebhookEventSchema, WebhookEventListResponseSchema,
    SuccessResponseSchema, ErrorResponseSchema,
    MediaResponseSchema
)


@api_controller('/whatsapp', tags=['WhatsApp API'])
class WhatsAppController:
    
    @route.get('/contacts', response=list[ContactSchema])
    def get_contacts(self):
        """Get all WhatsApp contacts with last message and unread count"""
        contacts = Contact.objects.all()
        contact_list = []
        for contact in contacts:
            contact_list.append(ContactSchema.from_django_model(contact))
        return contact_list
    
    @route.get('/contacts/{contact_id}', response=ContactSchema)
    def get_contact(self, contact_id: int):
        """Get a specific contact by ID"""
        contact = get_object_or_404(Contact, id=contact_id)
        return ContactSchema.from_django_model(contact)
    
    @route.post('/contacts', response=ContactSchema, permissions=[IsAuthenticated])
    def create_contact(self, payload: CreateContactSchema):
        """Create a new WhatsApp contact"""
        try:
            contact_data = payload.model_dump()
            contact = Contact.objects.create(**contact_data)
            return ContactSchema.from_django_model(contact)
        except Exception as e:
            return {"error": str(e)}
    
    @route.put('/contacts/{contact_id}', response=ContactSchema, permissions=[IsAuthenticated])
    def update_contact(self, contact_id: int, payload: UpdateContactSchema):
        """Update a WhatsApp contact"""
        contact = get_object_or_404(Contact, id=contact_id)
        
        contact_data = payload.model_dump(exclude_unset=True)
        for attr, value in contact_data.items():
            setattr(contact, attr, value)
        contact.save()
        
        return ContactSchema.from_django_model(contact)
    
    @route.delete('/contacts/{contact_id}', response=SuccessResponseSchema, permissions=[IsAuthenticated])
    def delete_contact(self, contact_id: int):
        """Delete a WhatsApp contact"""
        contact = get_object_or_404(Contact, id=contact_id)
        contact.delete()
        return {"message": "Contact deleted successfully"}
    
    @route.get('/messages/{contact_id}', response=list[WAMessageSchema])
    def get_contact_messages(self, contact_id: int):
        """Get all WhatsApp messages for a specific contact"""
        contact = get_object_or_404(Contact, id=contact_id)
        messages = WAMessage.objects.filter(contact=contact).order_by('-timestamp')
        return messages
    
    @route.get('/messages/detail/{message_id}', response=WAMessageSchema)
    def get_message(self, message_id: int):
        """Get a specific message by ID"""
        message = get_object_or_404(WAMessage, id=message_id)
        return message
    
    @route.post('/messages', response=WAMessageSchema, permissions=[IsAuthenticated])
    def create_message(self, payload: CreateWAMessageSchema):
        """Create a new WhatsApp message"""
        try:
            message_data = payload.model_dump()
            contact_id = message_data.pop('contact')
            contact = get_object_or_404(Contact, id=contact_id)
            
            message = WAMessage.objects.create(
                contact=contact,
                **message_data
            )
            return message
        except Exception as e:
            return {"error": str(e)}
    
    @route.put('/messages/{message_id}', response=WAMessageSchema, permissions=[IsAuthenticated])
    def update_message(self, message_id: int, payload: UpdateWAMessageSchema):
        """Update a WhatsApp message"""
        message = get_object_or_404(WAMessage, id=message_id)
        
        message_data = payload.model_dump(exclude_unset=True)
        for attr, value in message_data.items():
            setattr(message, attr, value)
        message.save()
        
        return message
    
    @route.delete('/messages/{message_id}', response=SuccessResponseSchema, permissions=[IsAuthenticated])
    def delete_message(self, message_id: int):
        """Delete a WhatsApp message"""
        message = get_object_or_404(WAMessage, id=message_id)
        message.delete()
        return {"message": "Message deleted successfully"}
    
    @route.patch('/messages/{message_id}/mark-read', response=WAMessageSchema, permissions=[IsAuthenticated])
    def mark_message_read(self, message_id: int):
        """Mark a message as read"""
        message = get_object_or_404(WAMessage, id=message_id)
        message.seen = True
        message.save()
        return message
    
    @route.patch('/messages/{message_id}/mark-unread', response=WAMessageSchema, permissions=[IsAuthenticated])
    def mark_message_unread(self, message_id: int):
        """Mark a message as unread"""
        message = get_object_or_404(WAMessage, id=message_id)
        message.seen = False
        message.save()
        return message


@api_controller('/whatsapp/templates', tags=['WhatsApp Templates'])
class WhatsAppTemplateController:
    
    @route.get('/', response=list[WATemplateSchemaSchema])
    def get_templates(self):
        """Get all WhatsApp templates"""
        templates = WATemplateSchema.objects.all().order_by('-created_at')
        return templates
    
    @route.get('/{template_id}', response=WATemplateSchemaSchema)
    def get_template(self, template_id: int):
        """Get a specific template by ID"""
        template = get_object_or_404(WATemplateSchema, id=template_id)
        return template
    
    @route.post('/', response=WATemplateSchemaSchema, permissions=[IsAuthenticated])
    def create_template(self, payload: CreateWATemplateSchemaSchema):
        """Create a new WhatsApp template"""
        try:
            template_data = payload.model_dump()
            # Set status to 'sent' when creating (as per original logic)
            template_data['status'] = 'sent'
            template = WATemplateSchema.objects.create(**template_data)
            return template
        except Exception as e:
            return {"error": str(e)}
    
    @route.put('/{template_id}', response=WATemplateSchemaSchema, permissions=[IsAuthenticated])
    def update_template(self, template_id: int, payload: UpdateWATemplateSchemaSchema):
        """Update a WhatsApp template"""
        template = get_object_or_404(WATemplateSchema, id=template_id)
        
        template_data = payload.model_dump(exclude_unset=True)
        for attr, value in template_data.items():
            setattr(template, attr, value)
        template.save()
        
        return template
    
    @route.delete('/{template_id}', response=SuccessResponseSchema, permissions=[IsAuthenticated])
    def delete_template(self, template_id: int):
        """Delete a WhatsApp template"""
        template = get_object_or_404(WATemplateSchema, id=template_id)
        template.delete()
        return {"message": "Template deleted successfully"}


@api_controller('/whatsapp/media', tags=['WhatsApp Media'])
class WhatsAppMediaController:
    
    @route.get('/{media_id}')
    def get_media(self, media_id: str):
        """Fetch and stream media content from WhatsApp API using media ID"""
        try:
            # Step 1: Fetch media metadata from WhatsApp API
            url = f"https://graph.facebook.com/v17.0/{media_id}"
            headers = {'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}'}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                media = response.json()
                media_url = media.get('url')
                mime_type = media.get('mime_type')
                
                if media_url:
                    # Step 2: Fetch the actual media content
                    media_response = self._fetch_media_from_whatsapp_api(media_url)
                    
                    if media_response:
                        # Stream the media content directly
                        return StreamingHttpResponse(
                            media_response.iter_content(chunk_size=8192),
                            content_type=mime_type
                        )
                    else:
                        return {"error": "Failed to fetch media content"}
                else:
                    return {"error": "Media URL not found"}
            else:
                return {"error": "Failed to fetch media metadata from WhatsApp API"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def _fetch_media_from_whatsapp_api(self, media_url):
        """Helper method to fetch media from WhatsApp API"""
        headers = {'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}'}
        response = requests.get(media_url, headers=headers, stream=True)
        if response.status_code == 200:
            return response
        return None


@api_controller('/whatsapp/webhooks', tags=['WhatsApp Webhooks'])
class WhatsAppWebhookController:
    
    @route.get('/events', response=list[WebhookEventSchema])
    def get_webhook_events(self):
        """Get all webhook events"""
        events = WebhookEvent.objects.all().order_by('-received_at')
        return events
    
    @route.get('/events/{event_id}', response=WebhookEventSchema)
    def get_webhook_event(self, event_id: int):
        """Get a specific webhook event by ID"""
        event = get_object_or_404(WebhookEvent, id=event_id)
        return event
    
    @route.delete('/events/{event_id}', response=SuccessResponseSchema, permissions=[IsAuthenticated])
    def delete_webhook_event(self, event_id: int):
        """Delete a webhook event"""
        event = get_object_or_404(WebhookEvent, id=event_id)
        event.delete()
        return {"message": "Webhook event deleted successfully"}
