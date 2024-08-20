from django.contrib import admin
from .models import *

@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ('group_name', 'group_description', 'owner')
    list_filter = ('group_name', 'owner')
    search_fields = ('group_name', 'owner')

@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ('group', 'type', 'author', 'body', 'file')
    list_filter = ('group', 'type', 'author', 'created')
    search_fields = ('group', 'author', 'created')

    # shortens the body of the message
    def body(self, obj):
        return obj.body[:50] + '...'
