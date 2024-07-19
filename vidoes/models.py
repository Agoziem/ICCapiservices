from django.db import models
from ICCapp.models import Organization
from django.conf import settings
import uuid

# Create your models here.
class Category(models.Model):
    category = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.category
    
    class Meta:
        verbose_name_plural = 'Categories'

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.CharField(max_length=100)
    
    def __str__(self):
        return self.subcategory
    
    class Meta:
        verbose_name_plural = 'SubCategories'

class Video(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    video = models.FileField(upload_to='videos/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='videothumbnails/', null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True)
    video_token = models.CharField(max_length=200, blank=True)
    userIDs_that_bought_this_video = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    number_of_times_bought = models.IntegerField(default=0, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    free = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-updated_at']

    # Save the video
    def save(self, *args, **kwargs):
        if not self.video_token:
            self.video_token = self.generate_token()
        return super().save(*args, **kwargs)
    
    # Generate a token for the video
    def generate_token(self):
        return uuid.uuid4().hex
