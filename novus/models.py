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
    )
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
    Image = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.space_id

    class Meta:
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
    Workspace = models.ForeignKey(
        Workspace, to_field="space_id", on_delete=models.DO_NOTHING, default=""
    )
    Channel = models.ForeignKey(Channels, on_delete=models.DO_NOTHING)
    Member = models.ManyToManyField(CustomUser)

    def __str__(self):
        return str(self.Channel)

    class Meta:
        unique_together = ("Workspace", "Channel")
        verbose_name = "ChannelMember"
        verbose_name_plural = "ChannelMembers"


class Chat(models.Model):
    Channel = models.ForeignKey(Channels, on_delete=models.DO_NOTHING)
    Username = models.ForeignKey(
        CustomUser,
        on_delete=models.DO_NOTHING,
        to_field="username",
        related_name="MessageSender",
    )
    Message = models.TextField(default="none")
    ReplyUsername = models.ForeignKey(
        CustomUser,
        on_delete=models.DO_NOTHING,
        to_field="username",
        related_name="RepliedTo",
    )
    Reply = models.TextField(default="none")

    def __str__(self):
        return str(self.Message)

    class Meta:
        verbose_name = "Chat"
        verbose_name_plural = "Chat"


def preSave_Space_id(sender, instance, **kwargs):
    if not instance.space_id:
        instance.space_id = instance.Name + "Team" + str(instance.id)


models.signals.pre_save.connect(preSave_Space_id, sender=Workspace)


def postSave_Space_id(sender, instance, created, **kwargs):
    if created:
        instance.space_id = (instance.Name + "Team" + str(instance.id)).replace(" ", "")
        pattern = r"[^A-Za-z0-9]+"
        instance.space_id = re.sub(pattern, "", instance.space_id)

        image = generate_gradient(200, 200)
        output_path = f"{BASE_DIR}/static/media/"
        with open(output_path + "gradient.png", "wb") as f:
            f.write(image.getbuffer())

        background = Image.open(output_path + "gradient.png")
        foreground = Image.open(output_path + "cube.png")

        background.paste(foreground, (0, 0), foreground)

        bytesIO = BytesIO()
        background.save(bytesIO, format="png")
        im_bytes = bytesIO.getvalue()
        background = base64.b64encode(im_bytes)
        background = background.decode("utf-8")

        instance.Image = background

        instance.save()


models.signals.post_save.connect(postSave_Space_id, sender=Workspace)
