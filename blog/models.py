from django.db import models
from django.conf import settings
from ICCapp.models import Organization
from ckeditor.fields import RichTextField

class Tag(models.Model):
    tag = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.tag
  
class Category(models.Model):
    category = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.category
    
class Blog(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    img = models.ImageField(upload_to='blogs/', null=True, blank=True)
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100, blank=True, null=True)
    body = RichTextField( blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, related_name='tags', blank=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    readTime = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-updated_at']



class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.comment

