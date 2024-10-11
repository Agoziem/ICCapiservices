from django.db import models
from ICCapp.models import Organization

class Email(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE , related_name='emails', null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)


    def __str__(self):
        return self.name

class EmailResponse(models.Model):
    message = models.ForeignKey(Email,on_delete=models.CASCADE,related_name='rsponses', null=True, blank=True)
    recipient_email = models.EmailField()
    response_subject= models.CharField(max_length=100)
    response_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

Email_status = [("pending","pending"),("sent","sent"),("failed","failed")]
class EmailMessage(models.Model):
    subject = models.CharField(max_length=355)  # You can adjust the max_length as needed
    body = models.TextField()  # Assuming the body can be longer text
    template = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the creation timestamp
    status = models.CharField(max_length=255, blank=True, choices=Email_status , default="pending")

    def __str__(self):
        return self.subject

