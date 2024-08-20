from django.urls import path
from .views.adminsorownerviews import (
    create_groupchat,
    chatroom_edit_view,
    chatroom_delete_view,
    add_users_to_chatroom,
    add_user_to_chatroom,
    remove_members_from_chatroom,
    remove_member_from_chatroom,
    add_admins_to_chatroom,
    add_admin_to_chatroom,
    remove_admins_from_chatroom,
    remove_admin_from_chatroom,
)

from .views.usersviews import (
    chat_list_view,
    chat_view,
)

urlpatterns = [
    # Chat group creation, editing, and deletion
    path('chatrooms/<int:user_id>/create/', create_groupchat, name='create_groupchat'),
    path('chatrooms/<int:chatroom_id>/<int:user_id>/edit/', chatroom_edit_view, name='edit_chatroom'),
    path('chatrooms/<int:chatroom_id>/<int:user_id>/delete/', chatroom_delete_view, name='delete_chatroom'),

    # Adding and removing users from chat groups
    path('chatrooms/<int:chatroom_id>/<int:admin_id>/add-users/', add_users_to_chatroom, name='add_users_to_chatroom'),
    path('chatrooms/<int:chatroom_id>/<int:admin_id>/add-user/', add_user_to_chatroom, name='add_user_to_chatroom'),
    path('chatrooms/<int:chatroom_id>/<int:admin_id>/remove-members/', remove_members_from_chatroom, name='remove_members_from_chatroom'),
    path('chatrooms/<int:chatroom_id>/<int:admin_id>/remove-member/', remove_member_from_chatroom, name='remove_member_from_chatroom'),

    # Adding and removing admins from chat groups
    path('chatrooms/<int:chatroom_id>/<int:owner_id>/add-admins/', add_admins_to_chatroom, name='add_admins_to_chatroom'),
    path('chatrooms/<int:chatroom_id>/<int:owner_id>/add-admin/', add_admin_to_chatroom, name='add_admin_to_chatroom'),
    path('chatrooms/<int:chatroom_id>/<int:owner_id>/remove-admins/', remove_admins_from_chatroom, name='remove_admins_from_chatroom'),
    path('chatrooms/<int:chatroom_id>/<int:owner_id>/remove-admin/', remove_admin_from_chatroom, name='remove_admin_from_chatroom'),

    # New endpoints for retrieving chat groups
    path('chatrooms/<int:organization_id>/list/', chat_list_view, name='list_chatrooms_by_organization'),
    path('chatrooms/<int:organization_id>/<int:user_id>/list/', chat_list_view, name='list_chatrooms_by_user'),
    path('chatrooms/<int:chatroom_id>/<int:user_id>/view/', chat_view, name='view_chatroom'),
]
