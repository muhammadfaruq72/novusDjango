from django.contrib import admin
from .models import CustomUser, Workspace, Members, Channels, ChannelMembers, Chat, InviteLink, RecentlyOpenedSpace, Tasks

# Register your models here.


@admin.register(CustomUser)
class CustomUserModel(admin.ModelAdmin):
    list_display = ["id", "email", "username", "Image"]


@admin.register(Workspace)
class WorkspaceUserModel(admin.ModelAdmin):
    list_display = ["id", "created_by", "Name", "space_id", "Image", "isClient"]


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
    list_display = ["id", "Workspace", "Channel", "Username", "Message", "ReplyUsername", "Reply", "attachment", "isClient"]

@admin.register(InviteLink)
class InviteLinkUserModel(admin.ModelAdmin):
    list_display = ["Workspace", "uuid", "CreatedOn", "TotalPeople", "PeopleAdded"]

@admin.register(RecentlyOpenedSpace)
class RecentlyOpenedSpace(admin.ModelAdmin):
    list_display = ["workspace", "User", "LastOpened", 'count']

@admin.register(Tasks)
class Tasks(admin.ModelAdmin):
    list_display = ["id","Workspace", "Channel", "task", 'CreatedOnDate', 'ExpiryDate', 'Status']