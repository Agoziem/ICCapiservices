from rest_framework import serializers
from .models import Email

class EmailSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()
    class Meta:
        model = Email
        fields = '__all__'

    def get_organization(self, obj):
        return {'id': obj.organization.id, 'name': obj.organization.name}