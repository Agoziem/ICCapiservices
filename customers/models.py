from django.db import models

# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=200, blank=False, null=False, default="Anonymous")
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
