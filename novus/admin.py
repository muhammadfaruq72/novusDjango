from django.contrib import admin
from .models import CustomUser, Workspace, Members, Channels, ChannelMembers, Chat

# Register your models here.


@admin.register(CustomUser)
class CustomUserModel(admin.ModelAdmin):
    list_display = ["id", "email", "username"]


@admin.register(Workspace)
class WorkspaceUserModel(admin.ModelAdmin):
    list_display = ["id", "created_by", "Name", "space_id", "Image"]


@admin.register(Members)
class MembersUserModel(admin.ModelAdmin):
    list_display = ["id", "Workspace", "User", "is_admin"]


@admin.register(Channels)
class ChannelsUserModel(admin.ModelAdmin):
    list_display = ["id", "Workspace", "Name", "is_public"]


@admin.register(ChannelMembers)
class ChannelMembersUserModel(admin.ModelAdmin):
    list_display = ["id", "Workspace", "Channel"]


@admin.register(Chat)
class ChatUserModel(admin.ModelAdmin):
    list_display = ["id", "Channel", "Username", "Message", "ReplyUsername", "Reply"]
