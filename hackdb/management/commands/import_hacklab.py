# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

import datetime
import json

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from allauth.account.models import EmailAddress

from discorduser.models import DiscordUser
from membership.models import Member, MembershipTerm
from mailman2.models import ChangeOfAddress, MailingList, GroupPolicy
from groupadmin.models import GroupOwnership, GroupProperties
from posixusers.models import SSHKey
from nfctokens.models import NFCToken, NFCTokenLog


class Command(BaseCommand):
    help = "Imports data from the previous Hacklab CRM application"

    def add_arguments(self, parser):
        parser.add_argument("filename", nargs=1, type=str)
        parser.add_argument("--yes", action="store_true")

    def handle(self, *args, **options):
        if not options["yes"]:
            print("This operation will delete existing data.")
            print("Run with --yes flag to confirm.")
            return

        with open(options["filename"][0], "r") as fh:
            data = json.load(fh)

        # new objects referenced by old IDs
        users = {}
        hacklabgroups = {}
        tokens = {}
        mailing_lists = {}

        # delete the existing model data
        Group.objects.all().delete()
        ChangeOfAddress.objects.all().delete()
        MembershipTerm.objects.all().delete()
        Member.objects.all().delete()
        get_user_model().objects.all().delete()
        NFCToken.objects.all().delete()
        NFCTokenLog.objects.all().delete()
        MailingList.objects.all().delete()

        for record in data:
            if record["model"] == "hacklabusers.group":
                # print(record)
                group = Group(name=record["fields"]["name"])
                group.save()
                hacklabgroups[record["pk"]] = group
                if record["fields"]["description"]:
                    group.properties = GroupProperties(
                        group=group, description=record["fields"]["description"]
                    )
                    group.properties.save()
                if record["fields"]["posix_gid"]:
                    group.posix.gid = record["fields"]["posix_gid"]
                    group.posix.save()
                hacklabgroups[record["pk"]] = group

        sharealike = Group.objects.create(name="sharealike")
        GroupProperties.objects.create(
            group=sharealike,
            description="Users in this group are sharing their door access events with MQTT. Use the privacy setting in your profile to change this.",
            self_service=False,
        )

        for record in data:
            if record["model"] == "auth.user":
                # print(record)
                user = get_user_model()()
                for field in [
                    "username",
                    "password",
                    "first_name",
                    "last_name",
                    "is_superuser",
                    "is_staff",
                    "is_active",
                    "date_joined",
                    "last_login",
                    "email",
                ]:
                    setattr(user, field, record["fields"][field])
                user.save()
                if record["fields"]["email"]:
                    EmailAddress.objects.create(
                        user=user, email=record["fields"]["email"]
                    )
                users[record["pk"]] = user

        for record in data:
            if record["model"] == "hacklabusers.profile":
                # print(record)
                user = users[record["fields"]["user"]]
                member = Member()
                member.user = user
                member.uuid = record["fields"]["uuid"]
                member.real_name = record["fields"]["legal_name"]
                member.display_name = record["fields"]["display_name"]
                member.address_street1 = record["fields"]["address_street1"]
                member.address_street2 = record["fields"]["address_street2"]
                member.address_street3 = record["fields"]["address_street3"]
                member.address_locality = record["fields"]["address_locality"]
                member.address_state = record["fields"]["address_state"]
                member.address_postalcode = record["fields"]["address_postalcode"]
                member.address_country = record["fields"]["address_country"]
                member.phone = record["fields"]["phone"]
                member.xero_uuid = record["fields"]["xero_uuid"]
                member.notes = record["fields"]["notes"]
                member.membership_number = record["fields"]["membership_number"]
                member.membership_suspended = record["fields"]["membership_suspended"]
                member.membership_status = record["fields"]["membership_status"]
                member.privacy = record["fields"]["privacy"]
                member.save()
                user.first_name = member.display_name or member.real_name
                user.save()
                if record["fields"]["posix_uid"]:
                    user.posix.uid = record["fields"]["posix_uid"]
                    if record["fields"]["password_ldap"].upper().startswith("{CRYPT}"):
                        user.posix.password = record["fields"]["password_ldap"][7:]
                    elif record["fields"]["password_ldap"].upper().startswith("{SSHA}"):
                        user.posix.password = record["fields"]["password_ldap"]
                    user.posix.save()
                if (
                    record["fields"]["verified_email"]
                    and record["fields"]["verified_email"].lower() == user.email.lower()
                ):
                    address = EmailAddress.objects.get(user=user, email=user.email)
                    address.verified = True
                    address.primary = True
                    address.save()

        for record in data:
            if record["model"] == "discorduser.discorduser":
                # print(record)
                user = users[record["fields"]["user"]]
                DiscordUser.objects.create(
                    user=user,
                    discord_id=record["fields"]["discord_id"],
                    discord_username=record["fields"]["discord_username"],
                )

        for record in data:
            if record["model"] == "hacklabusers.groupmembership":
                # print(record)
                user = users[record["fields"]["user"]]
                group = hacklabgroups[record["fields"]["group"]]
                user.groups.add(group)
                if record["fields"]["owner"]:
                    GroupOwnership.objects.create(
                        group=group,
                        user=user,
                    )

        for record in data:
            if record["model"] == "hacklabusers.membershipterm":
                # print(record)
                user = users[record["fields"]["user"]]
                mt = MembershipTerm()
                mt.user = user
                mt.start = datetime.date.fromisoformat(record["fields"]["start"])
                mt.mtype = record["fields"]["mtype"]
                if record["fields"]["end"]:
                    mt.end = datetime.date.fromisoformat(record["fields"]["end"])
                mt.save()

        for record in data:
            if record["model"] == "hacklabusers.sshkey":
                # print(record)
                user = users[record["fields"]["user"]]
                SSHKey.objects.create(
                    user=user,
                    key=record["fields"]["key"],
                    comment=record["fields"]["comment"],
                    enabled=record["fields"]["enabled"],
                )

        for record in data:
            if record["model"] == "hacklabusers.token":
                # print(record)
                user = users.get(record["fields"]["user"])
                nfctoken = NFCToken()
                nfctoken.user = user
                nfctoken.uid = record["fields"]["uid"]
                nfctoken.description = record["fields"]["description"]
                nfctoken.enabled = record["fields"]["enabled"]
                nfctoken.last_location = record["fields"]["last_location"]
                nfctoken.last_seen = record["fields"]["last_seen"]
                nfctoken.save()
                tokens[record["pk"]] = nfctoken

        for record in data:
            if record["model"] == "hacklabusers.tokenlog":
                # print(record)
                user = users.get(record["fields"]["user"])
                token = tokens.get(record["fields"]["token"])
                log = NFCTokenLog()
                log.user = user
                log.token = token
                log.timestamp = record["fields"]["timestamp"]
                log.location = record["fields"]["location"]
                log.uid = record["fields"]["uid"]
                log.name = record["fields"]["name"]
                log.token_description = record["fields"]["token_description"]
                log.authorized = record["fields"]["authorized"]
                log.ltype = record["fields"]["ltype"]
                log.save()

        for record in data:
            if record["model"] == "mailman2.mailinglist":
                # print(record)
                mailing_list = MailingList()
                for field in [
                    "name",
                    "description",
                    "info",
                    "advertised",
                    "subscribe_policy",
                    "archive_private",
                    "subscribe_auto_approval",
                    "auto_unsubscribe",
                ]:
                    setattr(mailing_list, field, record["fields"][field])
                mailing_list.save()
                mailing_lists[record["pk"]] = mailing_list

        for record in data:
            if record["model"] == "mailman2.grouppolicy":
                # print(record)
                mailing_list = mailing_lists[record["fields"]["mailing_list"]]
                group = hacklabgroups[record["fields"]["group"]]
                GroupPolicy.objects.create(
                    mailing_list=mailing_list,
                    group=group,
                    policy=record["fields"]["policy"],
                    prompt=record["fields"]["prompt"],
                )
