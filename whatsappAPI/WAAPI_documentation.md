Sure! Below is the information you provided, formatted into a Markdown file. I'll structure it with appropriate headers, lists, and code blocks to make it easy to read.


# Webhooks Notification Payload Reference

Webhooks are triggered when a customer performs an action or when the status of a message sent by a business changes. You will receive a webhook notification in the following scenarios:

## When a Customer Performs an Action
- Sends a text message to the business
- Sends an image, video, audio, document, or sticker to the business
- Sends contact information to the business
- Sends location information to the business
- Clicks a reply button set up by the business
- Clicks a call-to-action button on an Ad that clicks to WhatsApp
- Clicks an item on a business' list
- Updates their profile information, such as their phone number
- Asks for information about a specific product
- Orders products being sold by the business

## When the Status for a Message Sent by a Business Changes
- **delivered**: Message has been delivered
- **read**: Message has been read
- **sent**: Message has been sent

## Notification Payload Object
The notification payload is a combination of nested JSON arrays and objects containing information about the change.

### Example Notification Payload

```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "id": "WHATSAPP-BUSINESS-ACCOUNT-ID",
    "changes": [{
      "value": {
        "messaging_product": "whatsapp",
        "metadata": {
          "display_phone_number": "PHONE-NUMBER",
          "phone_number_id": "PHONE-NUMBER-ID"
        },
        "contacts": [{...}],
        "errors": [{...}],
        "messages": [{...}],
        "statuses": [{...}]
      },
      "field": "messages"
    }]
  }]
}
```

```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "365421663321122",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "2347065458493",
              "phone_number_id": "344588788746391"
            },
            "contacts": [
              {
                "profile": {
                  "name": "Engr Gozzy"
                },
                "wa_id": "2348080982606"
              }
            ],
            "messages": [
              {
                "from": "2348080982606",
                "id": "wamid.HBgNMjM0ODA4MDk4MjYwNhUCABIYIDQyQ0FBNUMwM0JDODg4OTlFRjEyQUM5MkM5RDlBQjFGAA==",
                "timestamp": "1720793840",
                "text": {
                  "body": "How much is your Service first of all"
                },
                "type": "text"
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}
```

### The Nested Structure of the Notification Payload

#### Object
- **object** (string): The specific webhook a business is subscribed to. Value is always `whatsapp_business_account`.

#### Entry
- **entry** (array of objects): An array of entry objects.
  - **id** (string): The WhatsApp Business Account ID for the business subscribed to the webhook.
  - **changes** (array of objects): An array of change objects.
    - **value** (object): Contains details about the change that triggered the webhook (see **Value Object**).
    - **field** (string): Notification type. Value will be `messages`.

### Value Object
The value object contains details about the change that triggered the webhook.

#### Contacts
- **contacts** (array of objects): Array of contact objects with information about the customer.
  - **wa_id** (string): The customer's WhatsApp ID.
  - **user_id** (string): Additional unique, alphanumeric identifier for a WhatsApp user.
  - **profile** (object): Customer profile object.
    - **name** (string): The customer's name.

#### Errors
- **errors** (array of objects): An array of error objects.
  - **code** (integer): Error code (e.g., `130429`).
  - **title** (string): Error code title (e.g., `Rate limit hit`).
  - **message** (string): Error message. Same as title value.
  - **error_data** (object): Additional error data.
    - **details** (string): Description of the error.

#### Messaging Product
- **messaging_product** (string): Product used to send the message. Value is always `whatsapp`.

#### Messages
- **messages** (array of objects): Information about a message received by the business.
  - **audio** (object): Contains information if the message type is audio or voice.
    - **id** (string): ID for the audio file.
    - **mime_type** (string): Mime type of the audio file.
  - **button** (object): Contains information if the message type is button.
    - **payload** (string): The payload for the button clicked by the customer.
    - **text** (string): Button text.
  - **context** (object): Contains context information if the customer interacts with your message.
    - **forwarded** (boolean): True if the message was forwarded.
    - **frequently_forwarded** (boolean): True if the message was forwarded more than 5 times.
    - **from** (string): The WhatsApp ID of the customer who replied.
    - **id** (string): The ID of the message being replied to.
    - **referred_product** (object): Information about the product being referred to.
      - **catalog_id** (string): ID of the Meta catalog.
      - **product_retailer_id** (string): ID of the product in the catalog.
  - **document** (object): Contains information if the message type is document.
    - **caption** (string): Caption for the document.
    - **filename** (string): Name of the file.
    - **sha256** (string): SHA 256 hash.
    - **mime_type** (string): Mime type of the document.
    - **id** (string): ID for the document.
  - **image** (object): Contains information if the message type is image.
    - **caption** (string): Caption for the image.
    - **sha256** (string): Image hash.
    - **id** (string): ID for the image.
    - **mime_type** (string): Mime type for the image.
  - **interactive** (object): Contains information if the customer interacts with your message.
    - **type** (object): Describes the interaction.
      - **button_reply** (object): Information when a customer clicks a button.
        - **id** (string): Unique ID of the button.
        - **title** (string): Title of the button.
      - **list_reply** (object): Information when a customer selects an item from a list.
        - **id** (string): Unique ID of the list item.
        - **title** (string): Title of the selected item.
        - **description** (string): Description of the selected item.
  - **order** (object): Information if the customer places an order.
    - **catalog_id** (string): ID for the catalog.
    - **text** (string): Text message sent along with the order.
    - **product_items** (array of objects): Contains product items information.
      - **product_retailer_id** (string): Unique ID of the product.
      - **quantity** (string): Number of items.
      - **item_price** (string): Price of each item.
      - **currency** (string): Currency of the price.
  - **referral** (object): Information when a customer clicks an ad redirecting to WhatsApp.
    - **source_url** (string): URL leading to the ad or post.
    - **source_type** (string): Type of source (e.g., `ad`, `post`).
    - **source_id** (string): Meta ID for the ad or post.
    - **headline** (string): Headline used in the ad or post.
    - **body** (string): Body of the ad or post.
    - **media_type** (string): Media type in the ad or post (e.g., `image`, `video`).
    - **image_url** (string): URL of the image, if applicable.
    - **video_url** (string): URL of the video, if applicable.
    - **thumbnail_url** (string): URL for the video thumbnail, if applicable.
    - **ctwa_clid** (string): Click ID generated by Meta for ads that click to WhatsApp.
  - **sticker** (object): Information if the message type is sticker.
    - **mime_type** (string): Mime type of the sticker.
    - **sha256** (string): Hash for the sticker.
    - **id** (string): ID for the sticker.
    - **animated** (boolean): True if the sticker is animated.
  - **system** (object): Information if the customer updates their profile or phone number.
    - **body** (string): Description of the change.
    - **identity** (string): Hash for the identity fetched from the server.
    - **new_wa_id** (string): New WhatsApp ID if the customer's phone number is updated.
    - **wa_id** (string): New WhatsApp ID (v12.0+).
    - **type** (string): Type of system update (e.g., `customer_changed_number`, `customer_identity_changed`).
    - **customer** (string): The WhatsApp ID for the customer prior to the update.
  - **text** (object): Information if the message type is text.
    - **body** (string): The text of the message.
  - **video** (object): Information if the message type is video.
    - **caption** (string): The caption for the video, if provided.
    - **filename** (string): The name for the file on the sender's device.
    - **sha256** (string): The hash for the video.
    - **id** (string): The ID for the video.
    - **mime_type** (string): The mime type for the video file.

### Metadata
- **metadata** (object): Metadata describing the business subscribed to the webhook.
  - **display_phone_number** (string): The phone number displayed for the business.
  - **phone_number_id** (string): ID for the phone number. Businesses can respond using

 this ID.

#### Statuses
- **statuses** (array of objects): Status updates for messages sent by the business.
  - **conversation** (object): Describes the conversation a business is having with a customer.
    - **expiration_timestamp** (string): The timestamp when the conversation expires.
    - **id** (string): Unique ID for the conversation.
    - **origin** (object): Describes how the conversation was initiated.
      - **type** (string): Initiation type (e.g., `business_initiated`, `customer_initiated`, `referral_conversion`).
  - **id** (string): Unique ID for the status.
  - **pricing** (object): The pricing type and category for the conversation.
    - **billable** (boolean): True if the conversation is billable.
    - **category** (string): The category of the conversation (e.g., `authentication`, `service`, `marketing`, `utility`).
    - **pricing_model** (string): The model used for pricing.
  - **recipient_id** (string): WhatsApp ID of the customer.
  - **status** (string): Status of the message (e.g., `delivered`, `read`, `sent`).
  - **timestamp** (string): The timestamp when the message status changed.
```

---

## Notes

This document is formatted in Markdown and includes the necessary details from your provided content. Make sure to replace any placeholders like `WHATSAPP-BUSINESS-ACCOUNT-ID`, `PHONE-NUMBER`, etc., with actual data where necessary.

Let me know if you need any adjustments or additional formatting!