from rest_framework import serializers
from django.contrib.auth import get_user_model

from authentication.serializers import UserminiSerializer
from utils import get_full_image_url
from .models import NotificationModified, NotificationRecipient

User = get_user_model()

# -----------------------------
# 🔹 Base Notification Serializers
# -----------------------------

class NotificationBaseSerializer(serializers.ModelSerializer):
    """Base notification fields - reusable across different serializers"""
    sender = serializers.IntegerField(required=False, allow_null=True)
    title = serializers.CharField(max_length=255)
    message = serializers.CharField()
    link = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = NotificationModified
        fields = ['sender', 'title', 'message', 'link', 'image']

# -----------------------------
# 🔹 Input Serializers
# -----------------------------

class NotificationCreateSerializer(NotificationBaseSerializer):
    """Serializer for creating new notifications"""
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list,
        help_text="List of user IDs to send notification to"
    )


class NotificationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating existing notifications"""
    id = serializers.IntegerField()
    sender = serializers.IntegerField(required=False, allow_null=True)
    title = serializers.CharField(max_length=255, required=False)
    message = serializers.CharField(required=False)
    link = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    image = serializers.ImageField(required=False, allow_null=True)
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list
    )
    class Meta:
        model = NotificationModified
        fields = ['id', 'sender', 'title', 'message', 'link', 'image', 'user_ids']



class NotificationReadUpdateSerializer(serializers.Serializer):
    """Serializer for updating read status of notifications"""
    notification_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    is_read = serializers.BooleanField()

    def validate_notification_id(self, value):
        """Validate notification exists"""
        if not NotificationModified.objects.filter(id=value).exists():
            raise serializers.ValidationError("Notification does not exist")
        return value

    def validate_user_id(self, value):
        """Validate user exists"""
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User does not exist")
        return value

    def validate(self, attrs):
        """Validate notification recipient relationship exists"""
        try:
            NotificationRecipient.objects.get(
                notification_id=attrs['notification_id'],
                user_id=attrs['user_id']
            )
        except NotificationRecipient.DoesNotExist:
            raise serializers.ValidationError("Notification recipient relationship does not exist")
        return attrs


class RemoveNotificationSerializer(serializers.Serializer):
    """Serializer for removing notification from user's list"""
    notification_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    def validate_notification_id(self, value):
        """Validate notification exists"""
        if not NotificationModified.objects.filter(id=value).exists():
            raise serializers.ValidationError("Notification does not exist")
        return value

    def validate_user_id(self, value):
        """Validate user exists"""
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User does not exist")
        return value

    def validate(self, attrs):
        """Validate notification recipient relationship exists"""
        try:
            NotificationRecipient.objects.get(
                notification_id=attrs['notification_id'],
                user_id=attrs['user_id']
            )
        except NotificationRecipient.DoesNotExist:
            raise serializers.ValidationError("Notification recipient relationship does not exist")
        return attrs

# -----------------------------
# 🔹 Output Serializers (Response)
# -----------------------------

class NotificationUserResponseSerializer(serializers.ModelSerializer):
    """User info in the context of a notification + read status"""
    has_read = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'image_url', 'has_read']

    def get_has_read(self, obj):
        """Get read status from NotificationRecipient"""
        notification_id = self.context.get('notification_id')
        if notification_id:
            try:
                recipient = NotificationRecipient.objects.get(
                    notification_id=notification_id,
                    user=obj
                )
                return recipient.is_read
            except NotificationRecipient.DoesNotExist:
                return False
        return False

    def get_image_url(self, obj):
        """Get user's profile image URL"""
        return get_full_image_url(obj.avatar) if obj.avatar else None


class NotificationOnlyResponseSerializer(serializers.ModelSerializer):
    """Notification without recipient details"""
    sender = UserminiSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = NotificationModified
        fields = ['id', 'sender', 'title', 'message', 'link', 'image', 'created_at', 'image_url', 'updated_at']

    def get_image_url(self, obj):
        """Get notification image URL"""
        return get_full_image_url(obj.image) if obj.image else None


class NotificationResponseSerializer(serializers.ModelSerializer):
    """Complete notification with recipients and their read status"""
    sender = UserminiSerializer(read_only=True)
    recipients = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = NotificationModified
        fields = ['id', 'sender', 'title', 'message', 'link', 'image', 'created_at', 'recipients', 'image_url', "updated_at"]

    def get_image_url(self, obj):
        """Get notification image URL"""
        return get_full_image_url(obj.image) if obj.image else None

    def get_recipients(self, obj):
        """Get all recipients with their read status"""
        recipients = NotificationRecipient.objects.filter(notification=obj).select_related('user')
        serializer = NotificationUserResponseSerializer(
            [recipient.user for recipient in recipients],
            many=True,
            context={'notification_id': obj.id}
        )
        return serializer.data


class NotificationRecipientSerializer(serializers.ModelSerializer):
    """Serializer for NotificationRecipient model"""
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    notification_id = serializers.IntegerField(source='notification.id', read_only=True)
    user_name = serializers.SerializerMethodField()
    notification_title = serializers.CharField(source='notification.title', read_only=True)

    class Meta:
        model = NotificationRecipient
        fields = ['id', 'notification_id', 'user_id', 'user_name', 'notification_title', 'is_read']

    def get_user_name(self, obj):
        """Get user's full name"""
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


# -----------------------------
# 🔹 Specialized Serializers
# -----------------------------

class UserNotificationListSerializer(serializers.ModelSerializer):
    """Serializer for listing notifications for a specific user"""
    notification = NotificationOnlyResponseSerializer(read_only=True)
    sender_name = serializers.SerializerMethodField()
    
    class Meta:
        model = NotificationRecipient
        fields = ['id', 'notification', 'is_read', 'sender_name']

    def get_sender_name(self, obj):
        """Get sender's full name"""
        if obj.notification.sender:
            return f"{obj.notification.sender.first_name} {obj.notification.sender.last_name}".strip()
        return None



