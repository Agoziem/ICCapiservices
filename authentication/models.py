from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    isOauth = models.BooleanField(default=False)
    Oauthprovider = models.CharField(max_length=100, null=True, blank=True, default='email')
    emailIsVerified = models.BooleanField(default=False)
    twofactorIsEnabled = models.BooleanField(default=False)
    verificationToken = models.CharField(max_length=100, null=True, blank=True,unique=True)
    expiryTime = models.DateTimeField(null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    Sex = models.CharField(max_length=10, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Change this to avoid clash
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='customuser',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # Change this to avoid clash
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='customuser',
    )
