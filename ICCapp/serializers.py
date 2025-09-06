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
    
class PaginatedStaffSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True, required=False)
    previous = serializers.URLField(allow_null=True, required=False)
    results = StaffSerializer(many=True)
    
    class Meta:
        ref_name = "PaginatedStaffSerializer"
        
class CreateStaffSerializer(serializers.ModelSerializer):
    img = serializers.ImageField(allow_null=True, required=False)
    
    class Meta:
        model = Staff
        exclude = ['organization']
        
class UpdateStaffSerializer(serializers.ModelSerializer):
    img = serializers.ImageField(allow_null=True, required=False)
    
    class Meta:
        model = Staff
        exclude = ['organization']

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
    
class PaginatedTestimonialSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True, required=False)
    previous = serializers.URLField(allow_null=True, required=False)
    results = TestimonialSerializer(many=True)
    
    class Meta:
        ref_name = "PaginatedTestimonialSerializer"

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'

class PaginatedSubscriptionSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True, required=False)
    previous = serializers.URLField(allow_null=True, required=False)
    results = SubscriptionSerializer(many=True)
    
    class Meta:
        ref_name = "PaginatedSubscriptionSerializer"
    
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
    
    def get_img_url(self, obj):
        return get_full_image_url(obj.img)
    
    def get_img_name(self, obj):
        return get_image_name(obj.img)
    
    def get_organization(self, obj):
        if obj.organization:
            return {'id': obj.organization.id, 'name': obj.organization.name}
        return None
    
    def get_staff_in_charge(self, obj):
        if obj.staff_in_charge:
            return {
                'id': obj.staff_in_charge.id, 
                'name': obj.staff_in_charge.first_name + ' ' + obj.staff_in_charge.last_name, 
                'img_url': get_full_image_url(obj.staff_in_charge.img) if obj.staff_in_charge.img else None
            }
        return None
    
    def get_services(self, obj):
        services = obj.services.all()
        return [{'id': service.id, 'name': service.name} for service in services]
    
class PaginatedDepartmentSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True, required=False)
    previous = serializers.URLField(allow_null=True, required=False)
    results = DepartmentSerializer(many=True)
    
    class Meta:
        ref_name = "PaginatedDepartmentSerializer"
        
class CreateDepartmentSerializer(serializers.ModelSerializer):
    img = serializers.ImageField(allow_null=True, required=False)
    staff_in_charge = serializers.IntegerField(required=False, allow_null=True)
    services = serializers.ListField(child=serializers.CharField(), required=False)
    
    class Meta:
        model = Department
        exclude = ['organization']
        
class UpdateDepartmentSerializer(serializers.ModelSerializer):
    img = serializers.ImageField(allow_null=True, required=False)
    staff_in_charge = serializers.IntegerField(required=False, allow_null=True)
    services = serializers.ListField(child=serializers.CharField(), required=False)
    
    class Meta:
        model = Department
        exclude = ['organization']
    
class OrganizationSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(allow_null=True, required=False)
    Organizationlogoname = serializers.SerializerMethodField()
    Organizationlogo = serializers.SerializerMethodField()
    # staffs = serializers.SerializerMethodField()
    # testimonials = serializers.SerializerMethodField()
    # subscriptions = serializers.SerializerMethodField()
    # departments = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = '__all__'
    
    def get_Organizationlogo(self, obj):
        return get_full_image_url(obj.logo)
    
    def get_Organizationlogoname(self, obj):
        return get_image_name(obj.logo)
    
    # def get_staffs(self, obj):
    #     staffs = obj.staff_set.all()
    #     return StaffSerializer(staffs, many=True).data
    
    # def get_testimonials(self, obj):
    #     testimonials = obj.testimonial_set.all()
    #     return TestimonialSerializer(testimonials, many=True).data
    
    # def get_subscriptions(self, obj):
    #     subscriptions = obj.subscription_set.all()
    #     return SubscriptionSerializer(subscriptions, many=True).data
    
    # def get_departments(self, obj):
    #     departments = obj.department_set.all()
    #     return DepartmentSerializer(departments, many=True).data
    
    
