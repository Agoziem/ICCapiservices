from django.db import models
from django.conf import settings
import os
import shortuuid
from ICCapp.models import Organization

User = settings.AUTH_USER_MODEL

# Model for chat group
class ChatGroup(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    group_name = models.CharField(max_length=128, unique=True, blank=True)
    group_description = models.TextField(blank=True, null=True)
    admins = models.ManyToManyField(User, related_name='admin_of_groups', blank=True)
    users_online = models.ManyToManyField(User, related_name='online_in_groups', blank=True)
    members = models.ManyToManyField(User, related_name='members_of_group', blank=True)
    owner = models.ForeignKey(User, related_name='owned_groups', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.group_name

    def save(self, *args, **kwargs):
        if not self.group_name:
            self.group_name = shortuuid.uuid()
        super().save(*args, **kwargs)

message_types = [('text', 'text'), ('file', 'file'), ('image', 'image')]

# Model for chat message   
class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, related_name='chat_messages', on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=message_types, default='text')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.CharField(max_length=300, blank=True, null=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    caption = models.CharField(max_length=300, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    users_seen = models.ManyToManyField(User, related_name='seen_messages', blank=True)
    is_reply = models.BooleanField(default=False)
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    
    @property
    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        elif self.image:
            return os.path.basename(self.image.name)
        else:
            return None
    
    def __str__(self):
        if self.body:
            return f'{self.author.username} : {self.body}'
        elif self.file:
            return f'{self.author.username} : {self.filename}'
        else:
            return f'{self.author.username} : {self.image}'
    
    class Meta:
        ordering = ['-created']