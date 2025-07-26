from django.db import models
from ICCapp.models import Organization
from django.conf import settings
from ckeditor.fields import RichTextField
import uuid


class Category(models.Model):
    category = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.category if self.category else "Unknown Category"

    class Meta:
        verbose_name_plural = "Categories"


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.CharField(max_length=100)

    def __str__(self):
        return self.subcategory

    class Meta:
        verbose_name_plural = "SubCategories"


# Services Model
class Service(models.Model):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True
    )
    preview = models.ImageField(upload_to="services/", null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    service_token = models.CharField(max_length=100, blank=True, null=True)
    service_flow = RichTextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_times_bought = models.IntegerField(default=0, blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True
    )
    subcategory = models.ForeignKey(
        SubCategory, on_delete=models.CASCADE, null=True, blank=True
    )
    userIDs_that_bought_this_service = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="userIDs_that_bought_this_service",
    )
    userIDs_whose_services_is_in_progress = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="userIDs_whose_services_is_in_progress",
    )
    userIDs_whose_services_have_been_completed = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="userIDs_whose_services_have_been_completed",
    )
    details_form_link = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-updated_at"]

    # Save the Service
    def save(self, *args, **kwargs):
        if not self.service_token:
            self.service_token = self.generate_token()
        return super().save(*args, **kwargs)

    # Generate a token for the Service
    def generate_token(self):
        return uuid.uuid4().hex


# Prebuilt Categories Form
