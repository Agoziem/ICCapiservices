from django.db import models
from django.conf import settings

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
    
# Notification model attached to the organization
class Notification(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
user_group=(
	('admin', 'admin'),
	('dashboard', 'dashboard'),
	('All', 'All'),
)

class Notifications(models.Model):
    Notification_group = models.CharField(max_length=100, choices=user_group, blank=True)
    headline=models.CharField(max_length=100, blank=True)
    Notification= models.TextField(blank=True)
    Notificationdate=models.DateField(auto_now_add=True, blank=True, null=True)
    last_updated_date = models.DateTimeField(auto_now=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    users_seen=models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def __str__(self):
        return f"{self.Notificationdate} {self.organization.name}"