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

