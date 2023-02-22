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
    Members,
    Channels,
    ChannelsInput,
    ChannelMembers,
    Chat,
    Response,
    InviteLink,
    RecentlyOpenedSpace,
    PaginatedRecentlyOpenedSpace,
    CustomUser,
    PaginatedChannelMembers,
    PaginatedMembers,
    PaginatedChat

)
from strawberry_django import mutations
from typing_extensions import Annotated
import decimal
from . import models
from django.db.models import Count
from strawberry_django.pagination import OffsetPaginationInput
import strawberry_django
from django.core.paginator import Page, Paginator
from asgiref.sync import sync_to_async
from django.db.models import Q
import datetime
from django.utils import timezone


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
    def Workspace(self, info: Info, email: str, Name: str) -> Workspace | None:
        try:
            models.Workspace.objects.create(created_by_id=email, Name=Name)
            space = models.Workspace.objects.filter(Name=Name, created_by_id=email).first()
            space_id = space.space_id
            # Image = models.Workspace.objects.filter(Name=Name, created_by_id=email).values()[0][
            #     "Image"
            # ]
            # name = models.Workspace.objects.filter(Name=Name, created_by_id=email).values()[0][
            #     "Name"
            # ]
            models.Members.objects.create(
                Workspace_id=space_id, User_id=email, is_admin=True
            )
            CreateChannel(space_id, "General", email)

            models.RecentlyOpenedSpace.objects.create(workspace_id=space_id, User_id=email, LastOpened=datetime.datetime.now())

            return Workspace(id=space.id, created_by=space.created_by, Name=space.Name, space_id=space.space_id, Image=space.Image)
        except Exception as e:
            print(e)
            return None

        

    @gql.django.field
    def Member(self, info: Info, space_id: str, email: str) -> Response:
        try:
            models.Members.objects.create(Workspace_id=space_id, User_id=email)
            for i in models.Channels.objects.filter(Workspace_id=space_id, is_public=True).values():
                print(i)
                CustomUser_id = models.CustomUser.objects.filter(email=email).values()[0]["id"]
                channel_id = models.Channels.objects.filter(Name=i["Name"], Workspace_id=i["Workspace_id"]).values()[0]["id"]
                id = models.ChannelMembers.objects.filter(Workspace_id=i["Workspace_id"], Channel_id=channel_id).values()[0]['id']
                models.ChannelMembers.objects.get(id=id).Member.add(CustomUser_id)
                print(i["Workspace_id"], i["Name"])

            try: models.RecentlyOpenedSpace.objects.create(workspace_id=space_id, User_id=email, LastOpened=datetime.datetime.now())
            except Exception as e: print(e)
                
            return Response(message="Success")
        except Exception as e:
            print(e)
            return Response(message="Failed")
    
    @gql.django.field
    def UpdateMemberIsAdmin(self, info: Info, space_id: str, email: str, is_admin: bool) -> Response:
        try:
            models.Members.objects.filter(Workspace_id=space_id, User_id=email).update(is_admin = is_admin)
            return Response(message="Success")
        except Exception as e:
            print(e)
            return Response(message="Failed")

    @gql.django.field
    def DeleteMember(self, info: Info, space_id: str, username: str, setAdmin: Optional[bool] = None) -> Response:
        email = models.CustomUser.objects.filter(username=username).first().email
        try:
            if setAdmin == None:
                print(setAdmin)
                for i in models.Channels.objects.filter(Workspace_id=space_id).values():
                    try:
                        CustomUser_id = models.CustomUser.objects.filter(email=email).values()[0]["id"]
                        channel_id = models.Channels.objects.filter(Name=i["Name"], Workspace_id=i["Workspace_id"]).values()[0]["id"]
                        id = models.ChannelMembers.objects.filter(Workspace_id=i["Workspace_id"], Channel_id=channel_id).values()[0]['id']
                        models.ChannelMembers.objects.get(id=id).Member.remove(CustomUser_id)
                    except Exception as e: print(e)

                models.Members.objects.filter(Workspace_id=space_id, User_id=email).delete()
                try: models.RecentlyOpenedSpace.objects.filter(workspace_id=space_id, User_id=email).delete()
                except Exception as e: print(e)

                return Response(message="Delete Success")
            if setAdmin != None:
                count = models.Members.objects.filter(Workspace_id=space_id, is_admin= True).count()
                print(count)
                if setAdmin == True:
                    a = models.Members.objects.filter(Workspace_id=space_id, User_id=email).update(is_admin = setAdmin)
                    return Response(message="setAdmin Success")
                if count > 1 and setAdmin == False:
                    a = models.Members.objects.filter(Workspace_id=space_id, User_id=email).update(is_admin = setAdmin)
                    return Response(message="setAdmin Success")
                if count <= 1 and setAdmin == False:
                    return Response(message="setAdmin Failed")

                
                
            
        except Exception as e:
            print(e)
            return Response(message="Failed")

    @gql.django.field
    def Channel(
        self, info: Info, space_id: str, ChannelName: str, CreatorEmail: str
    ) -> ChannelMembers | None:
        try:
            CreateChannel(space_id, ChannelName, CreatorEmail)
            channelCount = models.ChannelMembers.objects.filter(Workspace_id=space_id, Member__email=CreatorEmail).count()
            p = models.ChannelMembers.objects.filter(Workspace_id=space_id, Member__email=CreatorEmail, Channel__Name=ChannelName).first()
            print(p)
            return ChannelMembers(id=p.id, Channel=p.Channel, Member=p.Member, memberCount=p.Member.all().count(), channelCount=channelCount)
        except Exception as e:
            print(e)
            return None
        
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
        
    @gql.django.field
    def CreateInviteLink(
        self, info: Info, space_id: str, TotalPeople: int) -> InviteLink | None:
        try:
            return cast(InviteLink, models.InviteLink.objects.create(Workspace_id=space_id, TotalPeople=TotalPeople))
        except Exception as e:
            print(e)
            return None

    @gql.django.field
    def addMemberThroughInviteLink(
        self, info: Info, space_id: str, uuid: str, email: str) -> str | None:
        try:
            invitelink = models.InviteLink.objects.filter(Workspace_id=space_id, uuid=uuid).first()

            if invitelink.PeopleAdded <= invitelink.TotalPeople:
                date = invitelink.CreatedOn

                print(timezone.now(), date + datetime.timedelta(days=3))
                if timezone.now() <= date + datetime.timedelta(days=3):

                    models.Members.objects.create(Workspace_id=space_id, User_id=email)
                    for i in models.Channels.objects.filter(Workspace_id=space_id, is_public=True).values():
                        print(i)
                        CustomUser_id = models.CustomUser.objects.filter(email=email).values()[0]["id"]
                        channel_id = models.Channels.objects.filter(Name=i["Name"], Workspace_id=i["Workspace_id"]).values()[0]["id"]
                        id = models.ChannelMembers.objects.filter(Workspace_id=i["Workspace_id"], Channel_id=channel_id).values()[0]['id']
                        models.ChannelMembers.objects.get(id=id).Member.add(CustomUser_id)
                        print(i["Workspace_id"], i["Name"])

                        try: models.RecentlyOpenedSpace.objects.create(workspace_id=space_id, User_id=email, LastOpened=datetime.datetime.now())
                        except Exception as e: print(e)

                    models.InviteLink.objects.filter(Workspace_id=space_id, uuid=uuid).update(PeopleAdded = invitelink.PeopleAdded+1)

                    return "Added"
                else:
                    return None
        except Exception as e:
            print(e)
            return None
        
    @gql.django.field
    def UpdateLastOpened(
        self, info: Info, space_id: str, email: str) -> Response:
        try:
            models.RecentlyOpenedSpace.objects.filter(workspace_id=space_id, User_id=email).update(LastOpened=datetime.datetime.now())
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

    @gql.django.field
    def recentlyOpenedSpace(self, page: int, per_page: int, FilterUser_id: str) -> PaginatedRecentlyOpenedSpace:
        p = Paginator(models.RecentlyOpenedSpace.objects.filter(User_id=FilterUser_id).order_by('-LastOpened'), per_page)
        paginated_page = p.page(page)
        paginated_page.object_list = list(paginated_page.object_list)
        return PaginatedRecentlyOpenedSpace(
            items=[RecentlyOpenedSpace(id=recents.id, workspace=recents.workspace, User=recents.User, LastOpened=recents.LastOpened, count=recents.count,)
                   for recents in paginated_page],
                   has_next_page=paginated_page.has_next(),)
    
    @gql.django.field
    def customUsers(self, Useremail: str) -> CustomUser:
        user = models.CustomUser.objects.filter(email=Useremail).first()
        return CustomUser(
                id=user.id,
                email=user.email,
                username=user.username,
                Image=user.Image
            )

    @gql.django.field
    def checkMember(self, Useremail: str, space_id: str) -> Members | None:
        try: 
            member = models.Members.objects.filter(Workspace_id=space_id, User_id=Useremail).first()
            return Members(
                    id=member.id,
                    Workspace=member.Workspace,
                    User=member.User,
                    is_admin=member.is_admin,
                )
        except Exception as e:
            print(e)
            return None

    @gql.django.field
    def channelMembers(self, page: int, per_page: int, Useremail: str, space_id: str) -> PaginatedChannelMembers | None:
        try:
            p = Paginator(models.ChannelMembers.objects.filter(Workspace_id=space_id, Member__email=Useremail).order_by('id'), per_page)
            paginated_page = p.page(page)
            paginated_page.object_list = list(paginated_page.object_list)

            channelCount = models.ChannelMembers.objects.filter(Workspace_id=space_id, Member__email=Useremail).count()
            
            return PaginatedChannelMembers(
            items=[ChannelMembers(id=channel.id, Channel=channel.Channel, Member=channel.Member, memberCount=channel.Member.all().count())
                   for channel in paginated_page],
                   has_next_page=paginated_page.has_next(), channelCount=channelCount)
        
        except Exception as e:
            print(e)
            return None
        
    @gql.django.field
    def SpaceMembers(self, page: int, per_page: int, space_id: str) -> PaginatedMembers | None:
        try:
            # p = Paginator(models.Members.objects.filter(Workspace_id=space_id).exclude(User_id="admin@gmail.com").order_by('id'), per_page)
            p = Paginator(models.Members.objects.filter(Workspace_id=space_id).order_by('id'), per_page)
            paginated_page = p.page(page)
            paginated_page.object_list = list(paginated_page.object_list)

            memberCount = models.Members.objects.filter(Workspace_id=space_id).count()
            
            return PaginatedMembers(
            items=[Members(id=member.id, Workspace=member.Workspace, User=member.User, is_admin=member.is_admin)
                   for member in paginated_page],
                   has_next_page=paginated_page.has_next(), memberCount=memberCount)
        
        except Exception as e:
            print(e)
            return None
        
    @gql.django.field
    def QuerySpaceMembers(self, page: int, per_page: int, space_id: str, UserContains: Optional[str] = None) -> PaginatedMembers | None:
        try:
            # p = Paginator(models.Members.objects.filter(Workspace_id=space_id).exclude(User_id="admin@gmail.com").order_by('id'), per_page)
            if UserContains != None:
                p = Paginator(models.Members.objects.filter(Workspace_id=space_id, User__username__icontains=UserContains).order_by('id'), per_page)
            else:
                p = Paginator(models.Members.objects.filter(Workspace_id=space_id).order_by('id'), per_page)

            paginated_page = p.page(page)
            paginated_page.object_list = list(paginated_page.object_list)

            memberCount = models.Members.objects.filter(Workspace_id=space_id).count()
            
            return PaginatedMembers(
            items=[Members(id=member.id, Workspace=member.Workspace, User=member.User, is_admin=member.is_admin)
                   for member in paginated_page],
                   has_next_page=paginated_page.has_next(), memberCount=memberCount)
        
        except Exception as e:
            print(e)
            return None

    @gql.django.field
    def Chat(self, page: int, per_page: int, ChannelName: str, space_id: str, AfterID: Optional[int] | Optional[None] = None) -> PaginatedChat | None:
        try:
            ChannelName_id = models.Channels.objects.filter(Name=ChannelName, Workspace_id=space_id).values()[0]["id"]
            if AfterID == None:
                print(AfterID)
                p = Paginator(models.Chat.objects.filter(Workspace_id=space_id, Channel_id=ChannelName_id).order_by('-id'), per_page)
            if AfterID != None:
                print(AfterID)
                p = Paginator(models.Chat.objects.filter(id__lt=AfterID, Workspace_id=space_id, Channel_id=ChannelName_id).order_by('-id'), per_page)

            paginated_page = p.page(page)
            paginated_page.object_list = list(paginated_page.object_list)
            
            return PaginatedChat(
            items=[Chat(id=chat.id, Workspace=chat.Workspace, Channel=chat.Channel, Username=chat.Username, Message=chat.Message, ReplyUsername=chat.ReplyUsername, Reply=chat.Reply)
                   for chat in paginated_page],
                   has_next_page=paginated_page.has_next())
        
        except Exception as e:
            print(e)
            return None


    # workspace: List[Workspace] = strawberry.django.field()
    # members: List[Members] = strawberry.django.field()
    # channels: List[Channels] = strawberry.django.field()
    # channelMembers: List[ChannelMembers] = strawberry.django.field()
    # chat: List[Chat] = strawberry.django.field()



schema = JwtSchema(
    query=Query, mutation=Mutation, extensions=[SchemaDirectiveExtension]
)