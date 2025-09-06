from rest_framework import serializers
from .models import *
from services.serializers import ServiceSerializer
from products.serializers import ProductSerializer
from vidoes.serializers import VideoSerializer

class VerifyPaymentSerializer(serializers.Serializer):
    reference = serializers.CharField(required=True, help_text="Payment reference code")
    customer_id = serializers.IntegerField(required=True, help_text="ID of the customer making the payment")

class CustomerPaymentStatsSerializer(serializers.Serializer):
    customer__id = serializers.IntegerField(help_text="Customer ID")
    customer__username = serializers.CharField(help_text="Customer username")
    customer__count = serializers.IntegerField(help_text="Number of payments by this customer")
    amount__sum = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="Total amount paid by this customer")
    amount__avg = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="Average payment amount by this customer")

class PaymentCountStatsSerializer(serializers.Serializer):
    totalorders = serializers.IntegerField(help_text="Total number of orders/payments")
    totalcustomers = serializers.IntegerField(help_text="Total number of unique customers")
    customers = CustomerPaymentStatsSerializer(many=True, help_text="Detailed statistics for each customer")
    
class PaymentSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    services = ServiceSerializer(many=True)
    products = ProductSerializer(many=True)
    videos = VideoSerializer(many=True)
    class Meta:
        model = Orders
        fields = '__all__'

    def get_organization(self, obj):
        return {'id': obj.organization.id, 'name': obj.organization.name}
    
    def get_customer(self, obj):
        return {'id': obj.customer.id, 'name': obj.customer.username, 'email': obj.customer.email}
    


