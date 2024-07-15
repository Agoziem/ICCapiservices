from django.db import models
from ICCapp.models import Organization
from django.conf import settings
import uuid

# Product Category
class Category(models.Model):
    category = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.category
    
    class Meta:
        verbose_name_plural = 'Categories'

# Product model
class Product(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    preview = models.ImageField(upload_to='products/',null=True, blank=True)
    name = models.CharField(max_length=200, unique=True , null=True, blank=False)
    description = models.TextField(default='No description available')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.IntegerField(default=0)
    video_token = models.CharField(max_length=200, blank=True) # This is the token that will be used to access the product, it will be unique for all products
    usersID_that_purchased_product = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    digital = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-last_updated_date']

    # Save the product
    def save(self, *args, **kwargs):
        if not self.video_token:
            self.video_token = self.generate_token()
        return super().save(*args, **kwargs)
    
    # Generate a token for the product
    def generate_token(self):
        return uuid.uuid4().hex

# 