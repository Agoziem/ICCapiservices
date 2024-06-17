from django.db import models
from django.conf import settings
from ICCapp.models import Organization
import json
from ckeditor.fields import RichTextField

class Blog(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    img = models.ImageField(upload_to='blogs/', null=True, blank=True)
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100, blank=True, null=True)
    body = RichTextField( blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # tags = models.CharField(max_length=350, blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    readTime = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    

    def __str__(self):
        return self.title
    
    # def set_tags(self, tags_list):
    #     self.tags = json.dumps(tags_list)

    # def get_tags(self):
    #     return json.loads(self.tags) if self.tags else []

    # def add_tag(self, tag):
    #     tags_list = self.get_tags()
    #     if tag not in tags_list:
    #         tags_list.append(tag)
    #         self.set_tags(tags_list)

    # def remove_tag(self, tag):
    #     tags_list = self.get_tags()
    #     if tag in tags_list:
    #         tags_list.remove(tag)
    #         self.set_tags(tags_list)


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.comment

