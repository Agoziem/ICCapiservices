from rest_framework import serializers
from .models import *

class PaymentSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    class Meta:
        model = Orders
        fields = '__all__'

    def get_organization(self, obj):
        return {'id': obj.organization.id, 'name': obj.organization.name}
    
    def get_customer(self, obj):
        return {'id': obj.customer.id, 'name': obj.customer.username}

    def get_services(self, obj):
        return [{'id': service.id, 'name': service.name,'price': service.price} for service in obj.services.all()]
    
    def get_products(self, obj):
        return [{'id': product.id, 'name': product.name,"price": product.price} for product in obj.products.all()]
    


