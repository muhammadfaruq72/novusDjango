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
    PaginatedChat,
    queryChannelMembers,
    PaginatedqueryChannelMembers,
    deleteChannel,
    PaginatedSpaceMembersAddQuery,
    SpaceMembersAddQuery,
    Tasks,
    PaginatedTasks

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
from django.db.models import Value, BooleanField
import numpy
from PIL import Image
import urllib.request
from novusDjango.settings import BASE_DIR


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

def addSpacePeople(space_id: str, email: str):
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
    def RegisterCustom(self, info: Info, email: str, password: str, image: str) -> str:
        a = models.CustomUser.objects.create(email=email, password=password)
        urllib.request.urlretrieve(image, f"{BASE_DIR}/static/Users/{a.username}.png")
        return "Registered"

    @gql.django.field
    def Workspace(self, info: Info, email: str, Name: str, isClient: Optional[bool] = False ) -> Workspace | None:
        try:
            models.Workspace.objects.create(created_by_id=email, Name=Name, isClient=isClient)
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

            return Workspace(id=space.id, created_by=space.created_by, Name=space.Name, space_id=space.space_id, Image=space.Image, isClient=space.isClient)
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
        self, info: Info, space_id: str, ChannelName: str, WorkSpaceMemberUsername:Optional[str] = None, Delete: Optional[bool] = None, Leave: Optional[bool] = None, Public: Optional[bool] = None ) -> deleteChannel | None:
        try:
            if Delete == True:
                 models.Channels.objects.filter(Name=ChannelName, Workspace=space_id).delete()
                 return deleteChannel(space_id=space_id, ChannelName=ChannelName, operation="Deleted")
            if Public != None:
                models.Channels.objects.filter(Name=ChannelName, Workspace=space_id).update(is_public=Public)
                return deleteChannel(space_id=space_id, ChannelName=ChannelName, operation=f"Public {Public}")
                
            if Leave == True:
                CustomUser_id = models.CustomUser.objects.filter(username=WorkSpaceMemberUsername).values()[0]["id"]
                channel_id = models.Channels.objects.filter(Name=ChannelName, Workspace_id=space_id).values()[0]["id"]
                id = models.ChannelMembers.objects.filter(Workspace_id=space_id, Channel_id=channel_id).values()[0]['id']

                if models.Members.objects.filter(Workspace_id=space_id, User_id__username=WorkSpaceMemberUsername).first().is_admin == True:
                    CountAdmin = models.Members.objects.filter(Workspace_id=space_id,is_admin=True).values().count()
                    if CountAdmin > 1:
                        models.ChannelMembers.objects.get(id=id).Member.remove(CustomUser_id)
                    else: return None
                else: models.ChannelMembers.objects.get(id=id).Member.remove(CustomUser_id)
                return deleteChannel(space_id=space_id, ChannelName=ChannelName, operation="Leave")


            
        except Exception as e:
            print(e)
            return None

    @gql.django.field
    def AddChannelMember(
        self, info: Info, space_id: str, ChannelName: str, WorkSpaceMemberUsername: str, Add: bool
    ) -> Response:
        try:
            CustomUser_id = models.CustomUser.objects.filter(username=WorkSpaceMemberUsername).values()[0]["id"]
            channel_id = models.Channels.objects.filter(Name=ChannelName, Workspace_id=space_id).values()[0]["id"]
            id = models.ChannelMembers.objects.filter(Workspace_id=space_id, Channel_id=channel_id).values()[0]['id']
            if Add == True:
                models.ChannelMembers.objects.get(id=id).Member.add(CustomUser_id)
                print(Add, ChannelName, WorkSpaceMemberUsername)
            if Add == False:
                models.ChannelMembers.objects.get(id=id).Member.remove(CustomUser_id)
                print(Add, ChannelName, WorkSpaceMemberUsername)

            return Response(message=WorkSpaceMemberUsername)
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
    def Task(
        self, info: Info, option: str, space_id: str, ChannelName: str, task: str, ExpiryDate: Optional[str] = None, Status: Optional[str] = None, id: Optional[int] = None) -> str | None:
        try:
            if option == "add":
                channel_id = models.Channels.objects.filter(Name=ChannelName, Workspace_id=space_id).values()[0]["id"]
                a = models.Tasks.objects.create(Workspace_id=space_id, Channel_id=channel_id, task=task, ExpiryDate=datetime.datetime.strptime(ExpiryDate, "%Y-%m-%d").date(), CreatedOnDate=datetime.date.today())
                return str(a.id)
            
            if option == "status":
                print(Status, id)
                models.Tasks.objects.filter(id=id).update(Status=Status)
                return "status"
            if option == "delete":
                models.Tasks.objects.filter(id=id).delete()
                return "delete"
            
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
                    addSpacePeople(space_id, email)
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

    @gql.django.field
    def AddPeople(
        self, info: Info, space_id: str, people: List[str]) -> str:
        try:
            print(people, space_id)
            for username in people:
                email = models.CustomUser.objects.filter(username=username).first().email
                addSpacePeople(space_id, email)

            return "Success"
        except Exception as e:
            print(e)
            return "Success"


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
    def Tasks(self, page: int, per_page: int, space_id: str, ChannelName: str) -> PaginatedTasks:
        channel_id = models.Channels.objects.filter(Name=ChannelName, Workspace_id=space_id).values()[0]["id"]
        p = Paginator(models.Tasks.objects.filter(Workspace_id=space_id, Channel_id=channel_id).order_by("id"), per_page)
        paginated_page = p.page(page)
        paginated_page.object_list = list(paginated_page.object_list)
        return PaginatedTasks(
            items=[Tasks(id=recents.id, Workspace=recents.Workspace, Channel=recents.Channel, task=recents.task, CreatedOnDate=recents.CreatedOnDate, ExpiryDate=recents.ExpiryDate, Status=recents.Status,)
                   for recents in paginated_page],
                   has_next_page=paginated_page.has_next(),)
    @gql.django.field
    def ProgressTasks(self, space_id: str) -> int:
        Total = models.Tasks.objects.filter(Workspace_id=space_id).count()
        Completed = models.Tasks.objects.filter(Workspace_id=space_id, Status="Completed").count()
        Cancelled = models.Tasks.objects.filter(Workspace_id=space_id, Status="Cancelled").count()
        percentage = ((Completed+ Cancelled) / Total) * 100
        return int(percentage)

    @gql.django.field
    def recentlyOpenedSpaceAddMembers(self, page: int, per_page: int, FilterUser_id: str, SpaceContains: Optional[str] = None) -> PaginatedRecentlyOpenedSpace:
        try:
            if SpaceContains != None:
                p = Paginator(models.RecentlyOpenedSpace.objects.filter(User_id=FilterUser_id, workspace__Name__icontains=SpaceContains).order_by('-LastOpened'), per_page)
            else:
                p = Paginator(models.RecentlyOpenedSpace.objects.filter(User_id=FilterUser_id).order_by('-LastOpened'), per_page)

            paginated_page = p.page(page)
            paginated_page.object_list = list(paginated_page.object_list)

            Items = [RecentlyOpenedSpace(id=recents.id, workspace=recents.workspace, User=recents.User, LastOpened=recents.LastOpened, count=recents.count,)
                    for recents in paginated_page if recents.workspace.isClient == False]

            return PaginatedRecentlyOpenedSpace(
                items=Items, has_next_page=paginated_page.has_next(),)
        except Exception as e:
            print(e)
            return None
    
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

            def Percentage(ChannelName: str):
                try:
                    channel_id = models.Channels.objects.filter(Name=ChannelName, Workspace_id=space_id).values()[0]["id"]
                    Total = models.Tasks.objects.filter(Workspace_id=space_id, Channel_id=channel_id ).count()
                    Completed = models.Tasks.objects.filter(Workspace_id=space_id, Channel_id=channel_id, Status="Completed").count()
                    Cancelled = models.Tasks.objects.filter(Workspace_id=space_id, Channel_id=channel_id, Status="Cancelled").count()
                    percentage = ((Completed+ Cancelled) / Total) * 100
                    return int(percentage)
                except: return 0
                
            
            return PaginatedChannelMembers(
            items=[ChannelMembers(id=channel.id, Channel=channel.Channel, Member=channel.Member, memberCount=channel.Member.all().count(), progress=Percentage(channel.Channel.Name),)
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
    def SpaceMembersAddQuery(self, page: int, per_page: int, space_id: str, SelectedSpace: str, UserContains: Optional[str] = None) -> PaginatedSpaceMembersAddQuery | None:
        try:
            if UserContains != None:
                q1 = models.Members.objects.filter(Workspace_id=space_id, User__username__icontains=UserContains).values("User__id", "User__username")
                q2 = models.Members.objects.filter(Workspace_id=SelectedSpace, User__username__icontains=UserContains).values("User__id", "User__username")
            else:
                q1 = models.Members.objects.filter(Workspace_id=space_id).values("User__id", "User__username")
                q2 = models.Members.objects.filter(Workspace_id=SelectedSpace).values("User__id", "User__username")

            print(q2.difference(q1).order_by('User__id').count(), q1.count(), q2.count())

            p = Paginator(q2.difference(q1).order_by('User__id'), per_page)
            paginated_page = p.page(page)
            paginated_page.object_list = list(paginated_page.object_list)
            
            return PaginatedSpaceMembersAddQuery(
            items=[SpaceMembersAddQuery(id=space['User__id'], User=models.Members.objects.filter(Workspace_id=SelectedSpace, User__username=space['User__username']).first().User, isChecked=False)
                   for space in paginated_page],
                   has_next_page=paginated_page.has_next())
        
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

            for member in paginated_page:
                print(member.User)
            
            return PaginatedMembers(
            items=[Members(id=member.id, Workspace=member.Workspace, User=member.User, is_admin=member.is_admin)
                   for member in paginated_page],
                   has_next_page=paginated_page.has_next(), memberCount=memberCount)
        
        except Exception as e:
            print(e)
            return None
        
    @gql.django.field
    def QueryChannelMembers(self, page: int, per_page: int, space_id: str, channelName: str, ChMember: bool, UserContains: Optional[str] = None) -> PaginatedqueryChannelMembers | None:
        try:
            channel_id = models.Channels.objects.filter(Name=channelName, Workspace_id=space_id).values()[0]["id"]
            id = models.ChannelMembers.objects.filter(Workspace_id=space_id, Channel_id=channel_id).first().id

            if UserContains != None:
                # p = Paginator(models.Members.objects.filter(Workspace_id=space_id, User__username__icontains=UserContains).order_by('id'), per_page)
                qs2 = models.ChannelMembers.objects.get(id=id).Member.filter(username__icontains=UserContains).values("id", "email")
                qs1 = models.Members.objects.filter(Workspace_id=space_id, User__username__icontains=UserContains).values("User__id", "User_id")
                Intersection = []
                Difference = []
                try:
                    p = Paginator( qs1.intersection(qs2).order_by('User__id'), per_page)
                    paginated_page = p.page(page)
                    paginated_page.object_list = list(paginated_page.object_list)
                    Intersection = [{"User__id": i["User__id"], "User_id": i["User_id"], "isAdded": True} for i in list(paginated_page.object_list)]
                except:
                    Intersection = []

                try:
                    p = Paginator( qs1.difference(qs2).order_by('User__id'), per_page)
                    paginated_page = p.page(page)
                    paginated_page.object_list = list(paginated_page.object_list)
                    Difference = [{"User__id": i["User__id"], "User_id": i["User_id"], "isAdded": False} for i in list(paginated_page.object_list)]
                except:
                    Difference = []
                
                Intersection = numpy.concatenate((Intersection, Difference), axis = 0)
                Intersection = []
                Difference = []
                return PaginatedqueryChannelMembers(
                items=[queryChannelMembers(id=member['User__id'], User=models.Members.objects.filter(Workspace_id=space_id, User__email=member['User_id']).first().User, isAdded=member['isAdded'])
                    for member in Intersection],
                    has_next_page=paginated_page.has_next())

            else:
                isAdded = None
                qs2 = models.ChannelMembers.objects.get(id=id).Member.values("id", "email")
                qs1 = models.Members.objects.filter(Workspace_id=space_id).values("User__id", "User_id")
                if ChMember == True:
                    qs3 = qs1.intersection(qs2).order_by('User__id')
                    p = Paginator( qs3, per_page)
                    paginated_page = p.page(page)
                    paginated_page.object_list = list(paginated_page.object_list)
                    isAdded = True
                if ChMember == False:
                    qs3 = qs1.difference(qs2).order_by('User__id')
                    p = Paginator( qs3, per_page)
                    paginated_page = p.page(page)
                    paginated_page.object_list = list(paginated_page.object_list)
                    isAdded = False
                    
            
            return PaginatedqueryChannelMembers(
            items=[queryChannelMembers(id=member['User__id'], User=models.Members.objects.filter(Workspace_id=space_id, User__email=member['User_id']).first().User, isAdded=isAdded)
                   for member in paginated_page],
                   has_next_page=paginated_page.has_next())
        
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
            items=[Chat(id=chat.id, Workspace=chat.Workspace, Channel=chat.Channel, Username=chat.Username, Message=chat.Message, ReplyUsername=chat.ReplyUsername, Reply=chat.Reply, attachment=chat.attachment, ReplyAttachment=chat.ReplyAttachment, isClient=chat.isClient)
                   for chat in paginated_page],
                   has_next_page=paginated_page.has_next())
        
        except Exception as e:
            print(e)
            return None

    @gql.django.field
    def FileSpace(self, page: int, per_page: int, ChannelName: str, space_id: str, AfterID: Optional[int] | Optional[None] = None) -> PaginatedChat | None:
        try:
            ChannelName_id = models.Channels.objects.filter(Name=ChannelName, Workspace_id=space_id).values()[0]["id"]
            if AfterID == None:
                print(AfterID)
                p = Paginator(models.Chat.objects.filter(Workspace_id=space_id, Channel_id=ChannelName_id, isClient=True).order_by('-id'), per_page)
            if AfterID != None:
                print(AfterID)
                p = Paginator(models.Chat.objects.filter(id__lt=AfterID, Workspace_id=space_id, Channel_id=ChannelName_id, isClient=True).order_by('-id'), per_page)

            paginated_page = p.page(page)
            paginated_page.object_list = list(paginated_page.object_list)
            
            return PaginatedChat(
            items=[Chat(id=chat.id, Workspace=chat.Workspace, Channel=chat.Channel, Username=chat.Username, Message=chat.Message, ReplyUsername=chat.ReplyUsername, Reply=chat.Reply, attachment=chat.attachment, ReplyAttachment=chat.ReplyAttachment, isClient=chat.isClient)
                   for chat in paginated_page],
                   has_next_page=paginated_page.has_next())
        
        except Exception as e:
            print(e)
            return None
    
    @gql.django.field
    def TestApi(self) -> str:
        return "Working..."


    # workspace: List[Workspace] = strawberry.django.field()
    # members: List[Members] = strawberry.django.field()
    # channels: List[Channels] = strawberry.django.field()
    # channelMembers: List[ChannelMembers] = strawberry.django.field()
    # chat: List[Chat] = strawberry.django.field()



schema = JwtSchema(
    query=Query, mutation=Mutation, extensions=[SchemaDirectiveExtension]
)