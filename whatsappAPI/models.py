from django.db import models

class WhatsAppBusinessAccount(models.Model):
    account_id = models.CharField(max_length=255)
    display_phone_number = models.CharField(max_length=20)
    phone_number_id = models.CharField(max_length=255)

    def __str__(self):
        return self.account_id

class Contact(models.Model):
    wa_id = models.CharField(max_length=20)
    profile_name = models.CharField(max_length=255)

    def __str__(self):
        return self.profile_name

class Message(models.Model):
    whatsapp_account = models.ForeignKey(WhatsAppBusinessAccount, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    message_id = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    text_body = models.TextField()
    message_type = models.CharField(max_length=50)

    def __str__(self):
        return self.message_id

# {
#   "object": "whatsapp_business_account",
#   "entry": [
#     {
#       "id": "365421663321122",
#       "changes": [
#         {
#           "value": {
#             "messaging_product": "whatsapp",
#             "metadata": {
#               "display_phone_number": "2347065458493",
#               "phone_number_id": "344588788746391"
#             },
#             "contacts": [
#               {
#                 "profile": {
#                   "name": "Engr Gozzy"
#                 },
#                 "wa_id": "2348080982606"
#               }
#             ],
#             "messages": [
#               {
#                 "from": "2348080982606",
#                 "id": "wamid.HBgNMjM0ODA4MDk4MjYwNhUCABIYIDQyQ0FBNUMwM0JDODg4OTlFRjEyQUM5MkM5RDlBQjFGAA==",
#                 "timestamp": "1720793840",
#                 "text": {
#                   "body": "How much is your Service first of all"
#                 },
#                 "type": "text"
#               }
#             ]
#           },
#           "field": "messages"
#         }
#       ]
#     }
#   ]
# }
