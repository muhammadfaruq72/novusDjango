from novus.models import Workspace, CustomUser, ChannelMembers, Members, Channels

Workspace.objects.all()
Workspace.objects.all().delete()
Workspace.objects.all().values()
Workspace.objects.create(created_by_id=1, Name="# Brand Marketing")
Workspace.objects.filter(email="admin@gmail.com")
CustomUser.objects.filter(email="admin@gmail.com").values()[0]["id"]
Members.objects.filter(Workspace="DataScienceTeam1", User="admin@gmail.com").values()

Members.objects.create(User_id="admin@gmail.com", Workspace_id="DataScienceTeam1")


for i in ChannelMembers.objects.all():
    print(i.id)

ChannelMembers.objects.get(id=1).Member.add(1)
ChannelMembers.objects.get(id=1).Member.remove(1)
ChannelMembers.objects.get(id=1).Member.all().values()


CustomUser.objects.create(email="user1@gmail.com", username="user1", password="123456")
CustomUser.objects.create(email="user2@gmail.com", username="user2", password="123456")
CustomUser.objects.create(email="user3@gmail.com", username="user3", password="123456")
CustomUser.objects.create(email="user4@gmail.com", username="user4", password="123456")
CustomUser.objects.create(email="user5@gmail.com", username="user5", password="123456")
CustomUser.objects.create(email="user6@gmail.com", username="user6", password="123456")

Workspace.objects.create(created_by_id="admin@gmail.com", Name="Digital Marketing")
Workspace.objects.create(created_by_id="user1@gmail.com", Name="Data Science")
Workspace.objects.create(created_by_id="user2@gmail.com", Name="Programming")

Members.objects.create(Workspace_id="DigitalMarketingTeam1", User_id="user1@gmail.com")
Members.objects.create(Workspace_id="DigitalMarketingTeam1", User_id="user2@gmail.com")
Members.objects.create(Workspace_id="DigitalMarketingTeam1", User_id="user3@gmail.com")
Members.objects.create(Workspace_id="DigitalMarketingTeam1", User_id="user4@gmail.com")
Members.objects.create(Workspace_id="DigitalMarketingTeam1", User_id="user5@gmail.com")
Members.objects.create(Workspace_id="DataScienceTeam4", User_id="user1@gmail.com")
Members.objects.create(Workspace_id="DataScienceTeam4", User_id="user2@gmail.com")
Members.objects.create(Workspace_id="DataScienceTeam4", User_id="user3@gmail.com")
Members.objects.create(Workspace_id="DataScienceTeam4", User_id="user4@gmail.com")
Members.objects.create(Workspace_id="DataScienceTeam4", User_id="user5@gmail.com")

Channels.objects.create(Workspace_id="DigitalMarketingTeam1", Name="# Email Marketing")

from django.db import connection

cursor = connection.cursor()
cursor.execute(
    f"""INSERT INTO "novus_channelmembers_Member"(channelmembers_id, members_id) VALUES ({1}, {2});"""
)
print(cursor.fetchone())

"""INSERT INTO "novus_channelmembers"(Channel_id) VALUES (1);"""

CustomUser.objects.filter(email="admin@gmail.com").values()[0]["id"]

Members.objects.create(
    Workspace_id="DigitalMarketingTeam1", User_id="user1@gmail.com", is_admin=True
)