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
        verbose_name_plural = "Categories"


# Product Subcategory
class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.CharField(max_length=100)

    def __str__(self):
        return self.subcategory

    class Meta:
        verbose_name_plural = "SubCategories"


# Product model
class Product(models.Model):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True
    )
    preview = models.ImageField(upload_to="products/", null=True, blank=True)
    name = models.CharField(max_length=200, unique=True, null=True, blank=False)
    description = models.TextField(default="No description available")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.IntegerField(default=0)
    product = models.FileField(upload_to="products/", null=True, blank=True)
    product_token = models.CharField(
        max_length=200, blank=True
    )  # This is the token that will be used to access the product, it will be unique for all products
    userIDs_that_bought_this_product = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True
    )
    subcategory = models.ForeignKey(
        SubCategory, on_delete=models.CASCADE, null=True, blank=True
    )
    number_of_times_bought = models.IntegerField(default=0, blank=True, null=True)
    digital = models.BooleanField(default=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)
    free = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-last_updated_date"]

    # Save the product
    def save(self, *args, **kwargs):
        if not self.product_token:
            self.product_token = self.generate_token()
        return super().save(*args, **kwargs)

    # Generate a token for the product
    def generate_token(self):
        return uuid.uuid4().hex


#
