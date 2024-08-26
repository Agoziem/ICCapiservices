### WhatsApp API Integration Documentation

This documentation outlines the API endpoints available for interacting with the WhatsApp API, including sending messages, handling webhooks, and retrieving messages and contacts.

## Table of Contents

1. [Send WhatsApp Template Message](#send-whatsapp-template-message)
2. [WhatsApp Webhook](#whatsapp-webhook)
3. [Send Message to WhatsApp API](#send-message-to-whatsapp-api)
4. [Message List](#message-list)
5. [Contact List](#contact-list)
6. [Get Media](#get-media)

---

### 1. Send WhatsApp Template Message

**Endpoint:** `POST /send-template-message/`  
**Description:** Sends a template message to a specified WhatsApp phone number.

**Request Body:**

```json
{
  "to_phone_number": "recipient_phone_number",
  "template_name": "template_name",
  "language_code": "en_US"
}
```

- **to_phone_number**: The recipient's phone number.
- **template_name**: The name of the template to send (spaces replaced with underscores and lowercase).
- **language_code**: The language code of the template (default is `en_US`).

**Response:**

- **200 OK**
  ```json
  {
    "status": "success",
    "message": "Message sent successfully!"
  }
  ```

- **400 Bad Request**
  ```json
  {
    "status": "error",
    "message": "Error message from WhatsApp API"
  }
  ```

---

### 2. WhatsApp Webhook

**Endpoint:** `POST /whatsapp-webhook/`  
**Description:** Handles incoming WhatsApp webhook events, storing the event data and sending messages to WebSocket rooms.

**Request Body:**

```json
{
  "entry": [
    {
      "id": "event_id",
      "changes": [
        {
          "value": {
            "contacts": [
              {
                "wa_id": "contact_wa_id",
                "profile": {
                  "name": "contact_name"
                }
              }
            ],
            "messages": [
              {
                "id": "message_id",
                "timestamp": "timestamp",
                "type": "text",
                "text": {
                  "body": "message_body"
                }
              }
            ],
            "statuses": [
              {
                "id": "message_id",
                "status": "status",
                "timestamp": "timestamp"
              }
            ]
          }
        }
      ]
    }
  ]
}
```

**Response:**

- **200 OK**
  ```json
  {
    "status": "success"
  }
  ```

---

### 3. Send Message to WhatsApp API

**Endpoint:** `POST /<int:contact_list>/send_message/`  
**Description:** Sends a message (text, image, or document) to a specified WhatsApp contact.

**Request Body:**

```json
{
  "to": "recipient_phone_number",
  "type": "text",
  "body": "message_body"
}
```

- **to**: The recipient's phone number.
- **type**: The type of message (`text`, `image`, `document`).
- **body**: The text of the message (required for text messages).
- **link**: The URL of the image or document (required for image and document messages).
- **caption**: The caption of the image (optional for image messages).
- **filename**: The filename of the document (optional for document messages).

**Response:**

- **200 OK**
  ```json
  {
    "message_id": "message_id",
    "contact": "contact_wa_id",
    "message_type": "text",
    "body": "message_body",
    "link": "",
    "status": "sent"
  }
  ```

- **400 Bad Request**
  ```json
  {
    "status": "error",
    "message": "Error message from WhatsApp API"
  }
  ```

- **500 Internal Server Error**
  ```json
  {
    "status": "error",
    "message": "Internal server error"
  }
  ```

---

### 4. Message List

**Endpoint:** `GET /messages/<int:contact_list>/`  
**Description:** Retrieves a list of messages associated with a specified contact.

**Response:**

- **200 OK**
  ```json
  [
    {
      "message_id": "message_id",
      "contact": "contact_wa_id",
      "message_type": "text",
      "body": "message_body",
      "link": "",
      "status": "sent",
      "timestamp": "timestamp"
    },
    ...
  ]
  ```

---

### 5. Contact List

**Endpoint:** `GET /contacts/`  
**Description:** Retrieves a list of all contacts.

**Response:**

- **200 OK**
  ```json
  [
    {
      "wa_id": "contact_wa_id",
      "profile_name": "contact_name"
    },
    ...
  ]
  ```

---

### 6. Get Media

**Endpoint:** `GET /media/<str:media_id>/`  
**Description:** Retrieves a specific media file by its ID.

**Response:**

- **200 OK**
  ```json
  {
    "media_id": "media_id",
    "link": "media_url",
    "mime_type": "media_mime_type"
  }
  ```

- **404 Not Found**
  ```json
  {
    "status": "error",
    "message": "Media not found"
  }
  ```

---

### Notes:

- All endpoints except `GET` requests expect a `Content-Type: application/json` header.
- Ensure that the `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_VERSION`, and `WHATSAPP_FROM_PHONE_NUMBER_ID` settings are correctly configured in your Django settings.
- For WebSocket integration, ensure that `channels` is properly set up in your Django project.