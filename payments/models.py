from django.db import models
from ICCapp.models import Organization
from services.models import Service
from products.models import Product
from vidoes.models import Video
from django.conf import settings
import secrets

# Payment status choices
PAYMENT_STATUS = (
    ("Pending", "Pending"),
    ("Completed", "Completed"),
    ("Failed", "Failed"),
)


# Payment model
class Orders(models.Model):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True
    )
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    services = models.ManyToManyField(Service)
    products = models.ManyToManyField(Product)
    videos = models.ManyToManyField(Video)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="Pending")
    reference = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    service_delivered = models.BooleanField(default=False)
    last_updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment of {self.amount}"

    def save(self, *args, **kwargs):
        if not self.reference:
            reference = secrets.token_urlsafe(20)
            object_with_similar_reference = Orders.objects.filter(reference=reference)
            if not object_with_similar_reference:
                self.reference = reference
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
