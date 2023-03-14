from novus.models import Workspace, CustomUser, ChannelMembers, Members, Channels, InviteLink, RecentlyOpenedSpace, Chat

# @strawberry.field
# def fruits(pagination: OffsetPaginationInput) -> List[RecentlyOpenedSpace]:
#     queryset =models.RecentlyOpenedSpace.objects.all()
#     return strawberry_django.pagination.apply(pagination, queryset)

# from gqlauth.jwt.types_ import TokenType

# a =TokenType.from_token("")
# print(a)
 

Workspace.objects.all()
Workspace.objects.all().delete()
Workspace.objects.all().values()
Workspace.objects.create(created_by_id=1, Name="# Brand Marketing")
Workspace.objects.filter(email="admin@gmail.com")
CustomUser.objects.filter(email="admin@gmail.com").values()[0]["id"]
Members.objects.filter(Workspace="DataScienceTeam1", User="admin@gmail.com").values()

Members.objects.create(User_id="admin@gmail.com", Workspace_id="DataScienceTeam1")

from django.db.models import Value, BooleanField
Members.objects.filter(Workspace_id="AIRobotsDiscussionTeam19", User__username__icontains="user10").values("User__id", "User_id").annotate(isAdded=Value(True, output_field=BooleanField()))

for i in ChannelMembers.objects.all():
    print(i.id)

ChannelMembers.objects.get(id=1).Member.add(1)
ChannelMembers.objects.get(id=1).Member.remove(1)
ChannelMembers.objects.get(id=1).Member.all().values()
ChannelMembers.objects.get(id=7).Member.all().values("email")

qs2 = ChannelMembers.objects.get(id=7).Member.values("id", "email")
qs1 = Members.objects.filter(Workspace_id="AIRobotsDiscussionTeam19").values("User__id", "User_id")
qs3 = qs1.intersection(qs2).order_by('User__id')
qs3 = qs1.difference(qs2).order_by('User__id')
qs3.union(qs1.difference(qs2)).order_by('User__id')

Members.objects.filter(Workspace_id="TestingClientspaceClient39").values("User__id", "User_id")
Members.objects.filter(Workspace_id="AIRobotsDiscussionTeam19").values("User__id", "User_id")

Array = []
for i in qs1.intersection(qs2).order_by('User__id'):
    Array.append({"User__id": i["User__id"], "User_id": i["User_id"], "isAdded": True})
print(Array)

print([{"User__id": i["User__id"], "User_id": i["User_id"], "isAdded": True} for i in qs1.intersection(qs2).order_by('User__id')])

# combine = qs1.intersection(qs2).order_by('User_id') | qs1.difference(qs2).order_by('User_id')

from itertools import chain
from operator import attrgetter

result_list = list(chain(qs1, qs2))

result_list = sorted(list(chain(qs1, qs2)),key=attrgetter('email'))


CustomUser.objects.create(email="Novususer1@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer2@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer3@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer4@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer5@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer6@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer7@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer8@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer9@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer10@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer11@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer12@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer13@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer14@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer15@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer16@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer17@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer18@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer19@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer21@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer22@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer20@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer23@gmail.com", password="123456")
CustomUser.objects.create(email="Novususer24@gmail.com", password="123456")

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

InviteLink.objects.create(Workspace="space_id")

RecentlyOpenedSpace.objects.filter(User_id="admin@gmail.com").order_by('-LastOpened').values()

from django.db.models import Count

Members.objects.all().annotate(Count('Workspace'), distinct=True)

categories = Members.objects.all().order_by('id').values('Workspace__space_id').annotate(count=Count('Workspace__space_id'))

import datetime as dt
RecentlyOpenedSpace.objects.create(workspace_id="ChemistryTeam2", Name_id="Chemistry", Image_id="static/Workspace/ChemistryTeam2.png", User_id="admin@gmail.com", LastOpened=dt.date.today())

ChannelMembers.objects.filter(Workspace_id="AIRobotsDiscussionTeam19", Member__email="Useremail").order_by('id')

Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=8, Username_id = "admin1", Message="Dont have metal so stage manager wont work")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="Hi I bought a used mac mini 2011 today and wanted to upgrade to ventura, but I’ve made it to the end of the installation only to get this… Did I totally brick this mac? I only have PCs otherwise so I’m not sure how I could download Monterey instead… or even what the issue is with this installation")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="I’m not able to boot it with my previous OS now of course… it was running on catelina when I bought it")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="amazing news I’ll try this in the morning! Thank you 🙏🙏")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="Perhaps format the drive HFS+ (macOS Extended Journaled)")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="I had this error on my 2011 MacBook Air (4,2)")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="just formatted the drive with HFS+ (macOS Extended Journaled)")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="this is the same error on my Mac like a few weeks ago")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="Hello, I am trying to install Monterey on my Mac mini 3.1 but EFI boot is stuck on this point. What should I do?")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="I finally gave it a try and installed without a problem. Thank you for your reply")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="I finally gave it a try and installed smoothly (execpt the first usb I used was old and maybe 1.1 ? I changed hub and everything semmes to be okay. Thanks for your support")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="reboot with PRAM reset and retry.")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="I tried it but it didn’t work.")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="Unfortunately the only way to clear that mess would be a new installation. Since stage manager will not run on non-metal you might reconsider Monterey or Big Sur. Ventura installation can be a mess.")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="I was trying to install Monterey so it should not be a problem. I will  use a different USB and I will reset the SMC and PRAM. If this error still occurs then I don't know what to do.")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="Okay, the broken USB problems can only be solved by getting a good one. In times of fake Apple AirPods you may get crappy hardware very often")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="Hi , quick question , with OCLP v0.6.1 the AirPlay works on iMac late 2013 and weather app didn’t crash ?")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="Sorry, you need to check the ChangeLog or the lastest OCLP yourself, I do not have any Kepler based systems to confirm this.")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="I can't install OpenCore to disk. I tried like 5 times, restart, see the popup, install and be sad in the same loop. Now i'll try to download OCLP from GitHub again and install OpenCore to disk again. If it doesn't work any ideas why?")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="I was asking of you tried to write OC from safe mode boot? It would not work!")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="You can try to mount disk0s1 in advance using sudo diskutil mount disk0s1")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="they just said trying it from macOS safe mode won't work")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="I am trying to patch a MacPro4,1 with Ventura installed. Ventura installed fine but the post install root patch keeps failing, and asking to install the patches with each boot. It looks like it is looking for a 12.6.2 folder inside Universal-Binaries.zip but there are only 12.5 versions.  See the attached screenshots.")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="Looks like 0.6.1 is downloading the wrong version of the Universal-Binaries.zip, the one from the 25th of January has the 12.6.2 folder, but the app is pulling a January 23rd version which is missing it.")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="Quite possibly, would have to see the log of the root patching to see if that is the same problem. ")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=9, Username_id = "admin1", Message="Assuming I turn on verbose boot and OCLP debug... Where do I find the log file to upload?")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=8, Username_id = "admin1", Message="If yours has something similar it might be the same issue....")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=8, Username_id = "admin1", Message="Been trying to build an updated version to see if it works, but this python garbage is a mess.")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=8, Username_id = "admin1", Message="Ye, still wanted to try tho")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=8, Username_id = "admin1", Message="I had no errors with the actual root patching - it just hangs on the boot after patching")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=8, Username_id = "admin1", Message="Then probably not the same issue... I mean, it could still be using the wrong binary package that is causing you problems, but mine is legit skipping half of the patch because the files are not in the zip")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=8, Username_id = "admin1", Message="Indeed. Not the end of the world as my system is usable. I'll wait for some dev input and try and generate a log file to help.")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=8, Username_id = "admin1", Message="Mine is just limping along with no acceleration, but I also have Monterey and Big Sur partitions which work fine. So this isn't the end of the world for me either, I just wanted to try to get this machine up and running as a build server  for my software projects.  Monterey will do for now if I can't get this sorted though.")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=8, Username_id = "admin1", Message="I did, what now")
Chat.objects.create(Workspace_id="AIRobotsDiscussionTeam19", Channel_id=8, Username_id = "admin1", Message="Do all recent OCLP version automatically download Universal-Binaries..zip as part of the root patcghing process?")
