from django.db import models
from ICCapp.models import Organization

# Product model
class Product(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, unique=True , null=True, blank=False)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    digital = models.BooleanField(default=False)
    image = models.ImageField(upload_to='products/images', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
