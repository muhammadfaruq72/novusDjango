# types.py
import strawberry
from strawberry import auto
from typing import List, Optional
from . import models
from strawberry_django_plus import gql
from strawberry_django_plus.gql import relay
from django.db.models import Count


@strawberry.django.type(models.CustomUser)
class CustomUser:
    id: auto
    email: auto
    username: auto
    Image: auto


# @strawberry.django.filters.filter(models.Workspace)
# class WorkspaceFilter:
#     # space_id: str
#     created_by_id: str

#     def filter(self, queryset):
#         return queryset.filter(created_by_id=self.created_by_id)
        

@strawberry.django.type(models.Workspace)
class Workspace:
    id: auto
    created_by: "CustomUser"
    Name: auto
    space_id: auto
    Image: auto
    isClient: auto


@strawberry.django.type(models.Members)
class Members:
    id: auto
    Workspace: "Workspace"
    User: "CustomUser"
    is_admin: auto

@strawberry.type
class PaginatedMembers:
    items: List[Members]
    has_next_page: bool
    memberCount: int

# @strawberry.django.type(models.Members)
# class MembersCount:
#     id: auto
#     Workspace: "Workspace"
#     User: "CustomUser"
#     is_admin: auto


#     @classmethod
#     def get_queryset(cls, queryset, info):
#         return queryset.all().order_by('id').values('Workspace__space_id').annotate(count=Count('Workspace__space_id'))


@strawberry.django.type(models.Channels)
class Channels:
    id: auto
    Workspace: "Workspace"
    Name: auto
    is_public: auto


@strawberry.django.type(models.Channels)
class ChannelsInput:
    id: auto
    Workspace: "Workspace"
    Name: auto


@strawberry.django.type(models.ChannelMembers)
class ChannelMembers:
    id: auto
    Channel: "Channels"
    Member: List[CustomUser]  # ManyToManyField
    memberCount: int
    channelCount: int
    message: str

@strawberry.type
class PaginatedChannelMembers:
    items: List[ChannelMembers]
    has_next_page: bool
    channelCount: int

@strawberry.django.type(models.Members)
class queryChannelMembers:
    id: auto
    User: "CustomUser"
    isAdded: bool
    is_admin: auto

@strawberry.type
class deleteChannel:
    space_id: str
    ChannelName: str
    operation: str

@strawberry.type
class PaginatedqueryChannelMembers:
    items: List[queryChannelMembers]
    has_next_page: bool
    # hasNextchannelMember: bool

@strawberry.django.type(models.Chat)
class Chat:
    id: auto
    Workspace: "Workspace"
    Channel: "Channels"
    Username: "CustomUser"
    Message: auto
    ReplyUsername: "CustomUser"
    Reply: auto
    attachment: auto
    ReplyAttachment: auto
    isClient: auto

@strawberry.type
class PaginatedChat:
    items: List[Chat]
    has_next_page: bool


@strawberry.type
class Response:
    message: str

@gql.django.type(models.InviteLink)
class InviteLink(relay.Node):
    Workspace: "Workspace"
    uuid: gql.auto
    CreatedOn: gql.auto
    TotalPeople: gql.auto
    PeopleAdded: gql.auto

@gql.django.type(models.Tasks)
class Tasks(relay.Node):
    id_: int
    id: gql.auto
    Workspace: "Workspace"
    Channel: "Channels"
    task: gql.auto
    CreatedOnDate: gql.auto
    ExpiryDate: gql.auto
    Status: gql.auto
    

# @strawberry.django.filters.filter(models.RecentlyOpenedSpace)
# class RecentlyOpenedSpaceFilter:
#     User_id: str
#     def filter(self, queryset):
#         return queryset.filter(User_id=self.User_id).order_by('LastOpened')

@strawberry.django.type(models.RecentlyOpenedSpace)
class RecentlyOpenedSpace:
    id: auto
    workspace: "Workspace"
    User: "CustomUser"
    LastOpened: auto
    count: auto

@strawberry.type
class PaginatedRecentlyOpenedSpace:
    items: List[RecentlyOpenedSpace]
    has_next_page: bool

@strawberry.django.type(models.Members)
class SpaceMembersAddQuery:
    id: int
    User: "CustomUser"
    isChecked: bool

@strawberry.type
class PaginatedSpaceMembersAddQuery:
    items: List[SpaceMembersAddQuery]
    has_next_page: bool