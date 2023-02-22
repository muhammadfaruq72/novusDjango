# Generated by Django 4.1.5 on 2023-02-10 10:54

from django.conf import settings
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import novus.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('username', models.CharField(blank=True, error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, null=True, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('Image', models.ImageField(default='static/Users/gradient.png', unique=True, upload_to='static/Users')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
            managers=[
                ('objects', novus.models.CustomUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Channels',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=255)),
                ('is_public', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Channel',
                'verbose_name_plural': 'Channels',
            },
        ),
        migrations.CreateModel(
            name='Workspace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=255, unique=True)),
                ('space_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('Image', models.ImageField(default='static/Workspace/gradient.png', unique=True, upload_to='static/Workspace')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, to_field='email')),
            ],
            options={
                'verbose_name': 'Workspace',
                'verbose_name_plural': 'Workspaces',
                'unique_together': {('created_by', 'Name')},
            },
        ),
        migrations.CreateModel(
            name='InviteLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('CreatedOn', models.DateField(auto_now_add=True)),
                ('Workspace', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='novus.workspace', to_field='space_id')),
            ],
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Message', models.TextField(blank=True, default='none', null=True)),
                ('Reply', models.TextField(blank=True, default='none', null=True)),
                ('Channel', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='novus.channels')),
                ('DpReplyUsername', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='ImageDpReplyUsername', to=settings.AUTH_USER_MODEL, to_field='Image')),
                ('DpUsername', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='ImageUsername', to=settings.AUTH_USER_MODEL, to_field='Image')),
                ('ReplyUsername', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='RepliedTo', to=settings.AUTH_USER_MODEL, to_field='username')),
                ('Username', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='MessageSender', to=settings.AUTH_USER_MODEL, to_field='username')),
                ('Workspace', models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='novus.workspace', to_field='space_id')),
            ],
            options={
                'verbose_name': 'Chat',
                'verbose_name_plural': 'Chat',
            },
        ),
        migrations.AddField(
            model_name='channels',
            name='Workspace',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='novus.workspace', to_field='space_id'),
        ),
        migrations.CreateModel(
            name='RecentlyOpenedSpace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('LastOpened', models.DateField(auto_now_add=True)),
                ('count', models.IntegerField(blank=True, default=1, null=True)),
                ('Image', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='WorkspaceImage', to='novus.workspace', to_field='Image')),
                ('Name', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='WorkspaceName', to='novus.workspace', to_field='Name')),
                ('User', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='CustomUserName', to=settings.AUTH_USER_MODEL, to_field='email')),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='Workspaceid', to='novus.workspace', to_field='space_id')),
            ],
            options={
                'verbose_name': 'RecentlyOpened',
                'verbose_name_plural': 'RecentlyOpened',
                'unique_together': {('workspace', 'User')},
            },
        ),
        migrations.CreateModel(
            name='Members',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_admin', models.BooleanField(default=False)),
                ('User', models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, to_field='email')),
                ('Workspace', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='novus.workspace', to_field='space_id')),
            ],
            options={
                'verbose_name': 'Member',
                'verbose_name_plural': 'Members',
                'unique_together': {('Workspace', 'User')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='channels',
            unique_together={('Workspace', 'Name')},
        ),
        migrations.CreateModel(
            name='ChannelMembers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Channel', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='novus.channels')),
                ('Member', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('Workspace', models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='novus.workspace', to_field='space_id')),
            ],
            options={
                'verbose_name': 'ChannelMember',
                'verbose_name_plural': 'ChannelMembers',
                'unique_together': {('Workspace', 'Channel')},
            },
        ),
    ]
