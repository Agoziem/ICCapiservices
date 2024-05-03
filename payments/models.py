from django.db import models
from django.contrib.auth.models import User
from services.models import Service
from customers.models import Customer

# Payment status choices
PAYMENT_STATUS = (
    ('Pending', 'Pending'),
    ('Completed', 'Completed'),
    ('Failed', 'Failed'),
)

# Payment model
class Payment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    services = models.ManyToManyField(Service)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Payment of {self.amount}'