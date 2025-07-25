from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        
class CreateCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        exclude = ['organization']
        
class UpdateCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        exclude = ['organization']