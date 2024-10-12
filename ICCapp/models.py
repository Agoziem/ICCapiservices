from django.db import models
from django.conf import settings
from ckeditor.fields import RichTextField

# Organization model
class Organization(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    logo = models.ImageField(upload_to='organizations/logos')
    vision = models.TextField()
    mission = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)
    whatsapplink = models.CharField(max_length=200, blank=True, null=True)
    facebooklink = models.CharField(max_length=200, blank=True, null=True)
    instagramlink = models.CharField(max_length=200, blank=True, null=True)
    twitterlink = models.CharField(max_length=200, blank=True, null=True)
    tiktoklink = models.CharField(max_length=200, blank=True, null=True)
    linkedinlink = models.CharField(max_length=200, blank=True, null=True)
    youtubechannel = models.CharField(max_length=200, blank=True, null=True)
    privacy_policy = RichTextField( blank=True, null=True)
    terms_of_use = RichTextField( blank=True, null=True)

    def __str__(self):
        return self.name
    
# Staff model
class Staff(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    other_names = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    img = models.ImageField(upload_to='staff/images',blank=True, null=True)
    role = models.CharField(max_length=100, blank=True, null=True)
    facebooklink = models.CharField(max_length=100, blank=True, null=True)
    instagramlink = models.CharField(max_length=20, blank=True, null=True)
    twitterlink = models.CharField(max_length=100, blank=True, null=True)
    linkedinlink = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
# Testimonials model
class Testimonial(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100,default='Anonymous')
    content = models.TextField()
    role = models.CharField(max_length=100, blank=True, null=True)
    img = models.ImageField(upload_to='testimonials/images',blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Testimonial by {self.name}'
    
# subscription model
class Subscription(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()
    date_added = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.email

class DepartmentService(models.Model):
    name = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    
# department model
class Department(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    img = models.ImageField(upload_to='departments/images',blank=True, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    staff_in_charge = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True)
    services = models.ManyToManyField(DepartmentService, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    