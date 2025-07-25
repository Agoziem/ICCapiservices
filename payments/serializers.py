from rest_framework import serializers
from .models import *
from services.serializers import ServiceSerializer
from products.serializers import ProductSerializer
from vidoes.serializers import VideoSerializer

class VerifyPaymentSerializer(serializers.Serializer):
    reference = serializers.CharField(required=True, help_text="Payment reference code")
    customer_id = serializers.IntegerField(required=True, help_text="ID of the customer making the payment")
    
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
    


