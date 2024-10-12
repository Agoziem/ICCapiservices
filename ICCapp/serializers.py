from rest_framework import serializers
from .models import *
from utils import *



class StaffSerializer(serializers.ModelSerializer):
    img = serializers.ImageField(allow_null=True, required=False)
    img_url = serializers.SerializerMethodField()
    img_name = serializers.SerializerMethodField()
    class Meta:
        model = Staff
        fields = '__all__'

    def get_img_url(self, obj):
        return get_full_image_url(obj.img)
    
    def get_img_name(self, obj):
        return get_image_name(obj.img)

class TestimonialSerializer(serializers.ModelSerializer):
    img = serializers.ImageField(allow_null=True, required=False)
    img_url = serializers.SerializerMethodField()
    img_name = serializers.SerializerMethodField()
    class Meta:
        model = Testimonial
        fields = '__all__'

    def get_img_url(self, obj):
        return get_full_image_url(obj.img)
    
    def get_img_name(self, obj):
        return get_image_name(obj.img)

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
    
class DepartmentServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentService
        fields = '__all__'
    
class DepartmentSerializer(serializers.ModelSerializer):
    img = serializers.ImageField(allow_null=True, required=False)
    img_url = serializers.SerializerMethodField()
    img_name = serializers.SerializerMethodField()
    staff_in_charge = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()
    class Meta:
        model = Department
        fields = '__all__'

    def get_organization(self, obj):
        return {'id': obj.organization.id, 'name': obj.organization.name}
    
    def get_staff_in_charge(self, obj):
        return {'id': obj.staff_in_charge.id, 'name': obj.staff_in_charge.first_name + ' ' + obj.staff_in_charge.last_name, "img_url": get_full_image_url(obj.staff_in_charge.img)}
    
    def get_services(self, obj):
        services = obj.services.all()
        return DepartmentServiceSerializer(services, many=True).data
    
    def get_img_url(self, obj):
        return get_full_image_url(obj.img)
    
    def get_img_name(self, obj):
        return get_image_name(obj.img)
    
class OrganizationSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(allow_null=True, required=False)
    Organizationlogoname = serializers.SerializerMethodField()
    Organizationlogo = serializers.SerializerMethodField()
    staffs = serializers.SerializerMethodField()
    testimonials = serializers.SerializerMethodField()
    subscriptions = serializers.SerializerMethodField()
    departments = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = '__all__'
    
    def get_Organizationlogo(self, obj):
        return get_full_image_url(obj.logo)
    
    def get_Organizationlogoname(self, obj):
        return get_image_name(obj.logo)
    
    def get_staffs(self, obj):
        staffs = obj.staff_set.all()
        return StaffSerializer(staffs, many=True).data
    
    def get_testimonials(self, obj):
        testimonials = obj.testimonial_set.all()
        return TestimonialSerializer(testimonials, many=True).data
    
    def get_subscriptions(self, obj):
        subscriptions = obj.subscription_set.all()
        return SubscriptionSerializer(subscriptions, many=True).data
    
    def get_departments(self, obj):
        departments = obj.department_set.all()
        return DepartmentSerializer(departments, many=True).data
    
    
