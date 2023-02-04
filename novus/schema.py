from typing import AsyncGenerator, Union, List, cast, Optional, Iterable, Union
import strawberry
from django.db import connection
from gqlauth.core.middlewares import JwtSchema
from gqlauth.core.utils import get_user
from gqlauth.user import arg_mutations
from gqlauth.user.arg_mutations import Captcha
from gqlauth.user.queries import UserQueries
from strawberry.types import Info
from strawberry.schema.types.scalar import DEFAULT_SCALAR_REGISTRY
from strawberry_django_plus import gql
from strawberry_django_plus.directives import SchemaDirectiveExtension
from strawberry_django_plus.permissions import IsAuthenticated
from .types import (
    Workspace,
    WorkspaceInput,
    Members,
    Channels,
    ChannelsInput,
    ChannelMembers,
    Chat,
    Response,
)
from strawberry_django import mutations
from typing_extensions import Annotated
import decimal
from . import models


def CreateChannel(space_id: str, ChannelName: str, CreatorEmail: str):
    models.Members.objects.filter(Workspace=space_id, User=CreatorEmail).values()[
        0
    ]  # Check if Member exists in Workspace
    models.Channels.objects.create(Workspace_id=space_id, Name=ChannelName)
    ChannelName_id = models.Channels.objects.filter(Name=ChannelName, Workspace=space_id).values()[0]["id"]
    cursor = connection.cursor()
    cursor.execute(
        f"""INSERT INTO "novus_channelmembers"("Channel_id", "Workspace_id") VALUES ('{ChannelName_id}', '{space_id}');"""
    )

    channelmembers_id = models.ChannelMembers.objects.filter(Channel=ChannelName_id, Workspace=space_id).values()[0]["id"]

    CustomUser_id = models.CustomUser.objects.filter(email=CreatorEmail).values()[0][
        "id"
    ]
    cursor.execute(
        f"""INSERT INTO "novus_channelmembers_Member"("channelmembers_id", "customuser_id") VALUES ('{channelmembers_id}', '{CustomUser_id}');"""
    )


@strawberry.type
class AuthMutation:
    verify_token = arg_mutations.VerifyToken.field
    update_account = arg_mutations.UpdateAccount.field
    archive_account = arg_mutations.ArchiveAccount.field
    delete_account = arg_mutations.DeleteAccount.field
    password_change = arg_mutations.PasswordChange.field


@strawberry.type
class Mutation:
    @gql.django.field(directives=[IsAuthenticated()])
    def auth_entry(self) -> AuthMutation:
        return AuthMutation()

    captcha = Captcha.field
    token_auth = arg_mutations.ObtainJSONWebToken.field
    register = arg_mutations.Register.field
    verify_account = arg_mutations.VerifyAccount.field
    resend_activation_email = arg_mutations.ResendActivationEmail.field
    send_password_reset_email = arg_mutations.SendPasswordResetEmail.field
    password_reset = arg_mutations.PasswordReset.field
    password_set = arg_mutations.PasswordSet.field
    refresh_token = arg_mutations.RefreshToken.field
    revoke_token = arg_mutations.RevokeToken.field

    @gql.django.field
    def Workspace(self, info: Info, email: str, Name: str) -> Response:
        try:
            models.Workspace.objects.create(created_by_id=email, Name=Name)
            space_id = models.Workspace.objects.filter(Name=Name).values()[0][
                "space_id"
            ]
            models.Members.objects.create(
                Workspace_id=space_id, User_id=email, is_admin=True
            )
            CreateChannel(space_id, "# General", email)
            return Response(message="Success")
        except Exception as e:
            print(e)
            return Response(message="Failed")

    @gql.django.field
    def Member(self, info: Info, space_id: str, email: str) -> Response:
        try:
            models.Members.objects.create(Workspace_id=space_id, User_id=email)
            for i in models.Channels.objects.filter(Workspace_id=space_id, is_public=True).values():
                CustomUser_id = models.CustomUser.objects.filter(email=email).values()[0]["id"]
                channel_id = models.Channels.objects.filter(Name=i["Name"]).values()[0]["id"]
                id = models.ChannelMembers.objects.filter(Workspace_id=i["Workspace_id"], Channel_id=channel_id).values()[0]['id']
                models.ChannelMembers.objects.get(id=id).Member.add(CustomUser_id)
                print(i["Workspace_id"], i["Name"])
            
            return Response(message="Success")
        except Exception as e:
            print(e)
            return Response(message="Failed")

    @gql.django.field
    def DeleteMember(self, info: Info, space_id: str, email: str) -> Response:
        try:
            for i in models.ChannelMembers.objects.filter(
                Workspace_id=space_id
            ).values():
                Workspace_member_id = models.Members.objects.filter(
                    User=email
                ).values()[0]["id"]
                models.ChannelMembers.objects.get(id=i["id"]).Member.remove(
                    Workspace_member_id
                )
                print(i["id"])

            models.Members.objects.filter(Workspace_id=space_id, User_id=email).delete()
            return Response(message="Success")
        except Exception as e:
            print(e)
            return Response(message="Failed")

    @gql.django.field
    def Channel(
        self, info: Info, space_id: str, ChannelName: str, CreatorEmail: str
    ) -> Response:
        try:
            CreateChannel(space_id, ChannelName, CreatorEmail)
            return Response(message="Success")
        except Exception as e:
            print(e)
            return Response(message="Failed")
        
    @gql.django.field
    def DeleteChannel(
        self, info: Info, space_id: str, ChannelName: str
    ) -> Response:
        try:
            ChannelName_id = models.Channels.objects.filter(Name=ChannelName, Workspace=space_id).values()[0]["id"]
            models.ChannelMembers.objects.filter(Channel=ChannelName_id, Workspace=space_id).delete()
            models.Channels.objects.filter(Name=ChannelName, Workspace=space_id).delete()

            return Response(message="Success")
        except Exception as e:
            print(e)
            return Response(message="Failed")

    @gql.django.field
    def AddChannelMember(
        self, info: Info, space_id: str, ChannelName: str, WorkSpaceMemberEmail: str
    ) -> Response:
        try:
            models.Members.objects.filter(Workspace=space_id, User=WorkSpaceMemberEmail).values()[0]  # Check if Member exists in Workspace
            ChannelName_id = models.Channels.objects.filter(Name=ChannelName, Workspace=space_id).values()[0]["id"]
            channelmembers_id = models.ChannelMembers.objects.filter(Channel=ChannelName_id, Workspace=space_id).values()[0]["id"]
            CustomUser_id = models.CustomUser.objects.filter(email=WorkSpaceMemberEmail).values()[0]["id"]
            cursor = connection.cursor()
            cursor.execute(f"""INSERT INTO "novus_channelmembers_Member"(channelmembers_id, customuser_id) VALUES ({channelmembers_id}, {CustomUser_id});""")

            return Response(message="Success")
        except Exception as e:
            print(e)
            return Response(message="Failed")
        
    @gql.django.field
    def RemoveChannelMember(
        self, info: Info, space_id: str, ChannelName: str, WorkSpaceMemberEmail: str
    ) -> Response:
        try:
            ChannelName_id = models.Channels.objects.filter(Name=ChannelName, Workspace=space_id).values()[0]["id"]
            channelmembers_id = models.ChannelMembers.objects.filter(Channel=ChannelName_id, Workspace=space_id).values()[0]["id"]
            CustomUser_id = models.CustomUser.objects.filter(email=WorkSpaceMemberEmail).values()[0]["id"]
            cursor = connection.cursor()
            cursor.execute(f"""DELETE FROM "novus_channelmembers_Member" WHERE channelmembers_id='{channelmembers_id}' AND CustomUser_id='{CustomUser_id}';""")

            return Response(message="Success")
        except Exception as e:
            print(e)
            return Response(message="Failed")


@strawberry.type
class Query(UserQueries):
    @gql.django.field(
        directives=[
            IsAuthenticated(),
        ]
    )
    def whatsMyUserName(self, info: Info) -> str:
        return get_user(info).username

    # workspace: List[Workspace] = strawberry.django.field()
    # members: List[Members] = strawberry.django.field()
    # channels: List[Channels] = strawberry.django.field()
    # channelMembers: List[ChannelMembers] = strawberry.django.field()
    # chat: List[Chat] = strawberry.django.field()


# from gqlauth.jwt.types_ import TokenType

# a =TokenType.from_token("")
# print(a)

schema = JwtSchema(
    query=Query, mutation=Mutation, extensions=[SchemaDirectiveExtension]
)