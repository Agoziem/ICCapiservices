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


# Form Builder Models
class ServiceForm(models.Model):
    """Main form associated with a service"""
    service = models.OneToOneField(
        Service, 
        on_delete=models.CASCADE, 
        related_name="form"
    )
    title = models.CharField(max_length=200, default="Service Application Form")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Form for {self.service.name}"

    class Meta:
        ordering = ["-updated_at"]


class FormField(models.Model):
    """Individual fields in a form"""
    FIELD_TYPES = [
        ('text', 'Text Input'),
        ('email', 'Email'),
        ('number', 'Number'),
        ('tel', 'Phone Number'),
        ('textarea', 'Text Area'),
        ('select', 'Select Dropdown'),
        ('radio', 'Radio Button'),
        ('checkbox', 'Checkbox'),
        ('file', 'File Upload'),
        ('date', 'Date'),
        ('time', 'Time'),
        ('datetime', 'Date & Time'),
        ('url', 'URL'),
        ('range', 'Range Slider'),
    ]

    form = models.ForeignKey(
        ServiceForm, 
        on_delete=models.CASCADE, 
        related_name="fields"
    )
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    label = models.CharField(max_length=200)
    placeholder = models.CharField(max_length=200, blank=True, null=True)
    help_text = models.TextField(blank=True, null=True)
    is_required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    # Field specific options
    options = models.JSONField(blank=True, null=True)  # For select, radio, checkbox options
    min_value = models.FloatField(blank=True, null=True)  # For number, range fields
    max_value = models.FloatField(blank=True, null=True)  # For number, range fields
    min_length = models.PositiveIntegerField(blank=True, null=True)  # For text fields
    max_length = models.PositiveIntegerField(blank=True, null=True)  # For text fields
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.label} ({self.field_type})"

    class Meta:
        ordering = ['order', 'created_at']


class FormSubmission(models.Model):
    """User submissions for service forms"""
    form = models.ForeignKey(
        ServiceForm, 
        on_delete=models.CASCADE, 
        related_name="submissions"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="form_submissions"
    )
    submission_data = models.JSONField()  # Store all form field responses
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Submission by {self.user.username} for {self.form.service.name}"

    class Meta:
        ordering = ["-submitted_at"]
        unique_together = ['form', 'user']  # One submission per user per form
