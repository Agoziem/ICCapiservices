from rest_framework import serializers
from .models import *

class PaymentSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()
    class Meta:
        model = Payment
        fields = '__all__'

    def get_organization(self, obj):
        return {'id': obj.organization.id, 'name': obj.organization.name}
    
    def get_customer(self, obj):
        return {'id': obj.customer.id, 'name': obj.customer.name}

    def get_services(self, obj):
        return [{'id': service.id, 'name': service.name} for service in obj.services.all()]
    


