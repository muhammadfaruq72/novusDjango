# types.py
import strawberry
from strawberry import auto
from typing import List, Optional
from . import models


@strawberry.django.type(models.CustomUser)
class CustomUser:
    id: auto
    email: auto
    username: auto


@strawberry.django.type(models.Workspace)
class Workspace:
    id: auto
    created_by: "CustomUser"
    Name: auto
    space_id: auto
    Image: auto


@strawberry.django.type(models.Workspace)
class WorkspaceInput:
    id: auto
    created_by: "CustomUser"
    Name: auto


@strawberry.django.type(models.Members)
class Members:
    id: auto
    Workspace: "Workspace"
    User: "CustomUser"
    is_admin: auto


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
    User: List[Members]  # ManyToManyField


@strawberry.django.type(models.Chat)
class Chat:
    id: auto
    Channel: "Channels"
    Username: "CustomUser"
    Message: auto
    ReplyUsername: auto
    Reply: auto


@strawberry.type
class Response:
    message: str
