from django.db import models
from ICCapp.models import Organization

class Email(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE , related_name='emails', null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
