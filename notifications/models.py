from django.conf import settings
from django.db import models



class NotificationRecipient(models.Model):
    notification = models.ForeignKey('NotificationModified', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"NotificationRecipient(notification_id={self.notification.id}, user_id={self.user.id})"

# Create your models here.
class NotificationModified(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.URLField(max_length=200, null=True, blank=True)  # Optional link for the notification
    image = models.ImageField(upload_to='notifications/', null=True, blank=True)  # Optional image for the notification
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title