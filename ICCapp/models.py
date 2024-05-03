from django.db import models

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
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    other_names = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
# Testimonials model
class Testimonial(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    author = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Testimonial by {self.author}'
    
# subscription model
class Subscription(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    email = models.EmailField()

    def __str__(self):
        return self.email
    
# Notification model attached to the organization
class Notification(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title