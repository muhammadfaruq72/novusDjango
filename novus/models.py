from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
import django
import uuid
from gradient_generator import generate_gradient
from PIL import Image
from io import BytesIO
import base64
from novusDjango.settings import BASE_DIR
import re
import uuid

# Create your models here.
class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        if not password:
            raise ValueError("The given password must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):

    email = models.EmailField(
        blank=False, max_length=254, verbose_name="email address", unique=True
    )
    username = models.CharField(
        error_messages={"unique": "A user with that username already exists."},
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
        max_length=150,
        unique=True,
        validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
        verbose_name="username",
        blank=True, null=True
    )
    Image = models.ImageField(upload_to="static/Users", default="static/Users/gradient.png", unique=True)
    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Workspace(models.Model):
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.DO_NOTHING, to_field="email"
    )
    Name = models.CharField(max_length=255, unique=True)
    space_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    Image = models.ImageField(upload_to="static/Workspace", default="static/Workspace/gradient.png", unique=True)

    def __str__(self):
        return self.space_id

    class Meta:
        unique_together = ("created_by", "Name")
        verbose_name = "Workspace"
        verbose_name_plural = "Workspaces"
        # constraints = [
        # models.UniqueConstraint(fields=['Name', 'space_id'], name='unique Name for each Workspace')

    # ]


class Members(models.Model):
    Workspace = models.ForeignKey(
        Workspace, to_field="space_id", on_delete=models.DO_NOTHING
    )
    User = models.ForeignKey(
        CustomUser, to_field="email", on_delete=models.DO_NOTHING, default=""
    )
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return str(self.User)

    class Meta:
        unique_together = ("Workspace", "User")
        verbose_name = "Member"
        verbose_name_plural = "Members"


class Channels(models.Model):
    Workspace = models.ForeignKey(
        Workspace, to_field="space_id", on_delete=models.DO_NOTHING
    )
    Name = models.CharField(max_length=255)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.Name

    class Meta:
        unique_together = ("Workspace", "Name")
        verbose_name = "Channel"
        verbose_name_plural = "Channels"


class ChannelMembers(models.Model):
    Workspace = models.ForeignKey(Workspace, to_field="space_id", on_delete=models.DO_NOTHING, default="")
    Channel = models.ForeignKey(Channels, on_delete=models.DO_NOTHING)
    Member = models.ManyToManyField(CustomUser, related_name='chMembers')

    def __str__(self):
        return str(self.Channel)

    class Meta:
        unique_together = ("Workspace", "Channel")
        verbose_name = "ChannelMember"
        verbose_name_plural = "ChannelMembers"


class Chat(models.Model):
    Workspace = models.ForeignKey(Workspace, to_field="space_id", on_delete=models.DO_NOTHING, default="")
    Channel = models.ForeignKey(Channels, on_delete=models.DO_NOTHING)
    Username = models.ForeignKey(
        CustomUser,
        on_delete=models.DO_NOTHING,
        to_field="username",
        related_name="MessageSender",
    )
    # DpUsername = models.ForeignKey(CustomUser, to_field="Image", on_delete=models.DO_NOTHING, related_name="ImageUsername")
    Message = models.TextField(default=None, blank=True, null=True)
    ReplyUsername = models.ForeignKey(
        CustomUser,
        on_delete=models.DO_NOTHING,
        to_field="username",
        related_name="RepliedTo",
        blank=True, null=True
    )
    Reply = models.TextField(default=None, blank=True, null=True)
    # DpReplyUsername = models.ForeignKey(CustomUser, to_field="Image", on_delete=models.DO_NOTHING, related_name="ImageDpReplyUsername", blank=True, null=True)

    def __str__(self):
        return str(self.Message)

    class Meta:
        verbose_name = "Chat"
        verbose_name_plural = "Chat"

class InviteLink(models.Model):
    Workspace = models.ForeignKey(Workspace, to_field="space_id", on_delete=models.DO_NOTHING)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    TotalPeople = models.IntegerField(default=1, blank=True, null=True)
    PeopleAdded = models.IntegerField(default=0, blank=True, null=True)

class RecentlyOpenedSpace(models.Model):
    workspace = models.ForeignKey(Workspace, to_field="space_id", on_delete=models.DO_NOTHING, related_name="Workspaceid")
    # Name = models.ForeignKey(Workspace, to_field="Name", on_delete=models.DO_NOTHING, related_name="WorkspaceName")
    # Image = models.ForeignKey(Workspace, to_field="Image", on_delete=models.DO_NOTHING, related_name="WorkspaceImage")
    User = models.ForeignKey(CustomUser, to_field="email", on_delete=models.DO_NOTHING, related_name="CustomUserName")
    LastOpened = models.DateTimeField(auto_now_add=True)
    count = models.IntegerField(default=1, blank=True, null=True)
    
    

    class Meta:
        unique_together = ("workspace", "User")
        verbose_name = "RecentlyOpened"
        verbose_name_plural = "RecentlyOpened"
        


def GenerateImg(Folder: str, Foreground: str, instance, Mode: str):
    image = generate_gradient(200, 200)
    output_path = f"{BASE_DIR}/static/{Folder}/"
    with open(output_path + "gradient.png", "wb") as f:
        f.write(image.getbuffer())

    background = Image.open(output_path + "gradient.png")
    foreground = Image.open(output_path + Foreground)

    background.paste(foreground, (0, 0), foreground)

    if Mode == "Workspace":
        background.save(f"static/{Folder}/{instance}.png")
        instance.Image = f"static/{Folder}/{instance.space_id}.png"
    else:
        background.save(f"static/{Folder}/{instance.username}.png")
        instance.Image = f"static/{Folder}/{instance.username}.png"

# def preSave_Space_id(sender, instance, **kwargs):
#     if not instance.space_id:
#         instance.space_id = instance.Name + "Team" + str(instance.id)
# models.signals.pre_save.connect(preSave_Space_id, sender=Workspace)


def postSave_Workspace(sender, instance, created, **kwargs):
    if created:
        instance.space_id = (instance.Name + "Team" + str(instance.id)).replace(" ", "")
        pattern = r"[^A-Za-z0-9]+"
        instance.space_id = re.sub(pattern, "", instance.space_id)
        GenerateImg("Workspace", "cube.png", instance, "Workspace")
        instance.save()
models.signals.post_save.connect(postSave_Workspace, sender=Workspace)

def postSave_CustomUser(sender, instance, created, **kwargs):
    if created:
        email = instance.email
        email = email.split('@')[0]
        instance.username = (email + str(instance.id))
        GenerateImg("Users", "User.png", instance, "CustomUser")
        instance.save()
models.signals.post_save.connect(postSave_CustomUser, sender=CustomUser)

def postSave_RecentlyOpenedSpace(sender, instance, created, **kwargs):
    if created:
        
        count = RecentlyOpenedSpace.objects.filter(workspace_id=instance.workspace).count()
        instance.count = count
        if count > 0:
            RecentlyOpenedSpace.objects.filter(workspace_id=instance.workspace).update(count = count)
        
        instance.save()
models.signals.post_save.connect(postSave_RecentlyOpenedSpace, sender=RecentlyOpenedSpace)