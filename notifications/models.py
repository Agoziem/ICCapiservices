from django.db import models
from django.conf import settings

NOTIFICATION_TYPES = (
    ('info', 'Info'),
    ('success', 'Success'),
    ('warning', 'Warning'),
    ('error', 'Error'),
)

# Create your models here.
class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    users_viewed = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='notifications_viewed', blank=True)
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
