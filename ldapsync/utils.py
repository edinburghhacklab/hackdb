# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

import pprint
from typing import OrderedDict

import ldap3
from django.conf import settings

from . import serializers


def normalise_entry(entry):
    if entry is None:
        return None
    output = OrderedDict()
    for k, v in entry.items():
        if isinstance(v, list):
            if len(v) > 0:
                output[k] = v
        else:
            output[k] = [
                v,
            ]
    return output


def modlist(old, new, ignore_attr_types=[], debug=True):
    mods = {}
    seen_attr = {}
    for attr in old.keys():
        seen_attr[attr] = True
        if attr in ignore_attr_types:
            continue
        if attr in new:
            if old[attr] == new[attr]:
                # no change
                pass
            else:
                # modify
                if debug:
                    print(f"attr: {old[attr]} -> {new[attr]}")
                mods[attr] = [(ldap3.MODIFY_REPLACE, new[attr])]
        else:
            # delete
            mods[attr] = [(ldap3.MODIFY_DELETE, [])]
    for attr in new.keys():
        if attr in ignore_attr_types:
            continue
        if attr in old:
            pass
        else:
            # add
            mods[attr] = [(ldap3.MODIFY_ADD, new[attr])]
    return mods


def sync_user(user):
    user_serializer = serializers.UserLDAPSerializer(
        settings.LDAP_USERS_BASE_DN, domain_sid=settings.LDAP_DOMAIN_SID
    )
    dn, entry = user_serializer.serialize(user)
    print(dn, entry)
    server = LDAP()
    server.sync_entry(dn, entry)


def sync_group(group):
    group_serializer = serializers.GroupLDAPSerializer(
        settings.LDAP_GROUPS_BASE_DN, users_base_dn=settings.LDAP_USERS_BASE_DN
    )
    posix_group_serializer = serializers.PosixGroupLDAPSerializer(
        settings.LDAP_POSIX_GROUPS_BASE_DN
    )
    dn, entry = group_serializer.serialize(group)
    print(dn, entry)
    if group.posix:
        posix_dn, posix_entry = posix_group_serializer.serialize(group)
        print(posix_dn, posix_entry)
    server = LDAP()
    server.sync_entry(dn, entry)
    if group.posix:
        server.sync_entry(posix_dn, posix_entry)


class LDAP:
    def __init__(self):
        self.base_dn = settings.LDAP_BASE_DN
        self.server = ldap3.Server(
            settings.LDAP_HOST,
            port=settings.LDAP_PORT,
            use_ssl=settings.LDAP_USE_SSL,
        )
        self.connection = ldap3.Connection(
            self.server,
            user=settings.LDAP_USER,
            password=settings.LDAP_PASSWORD,
            auto_bind=True,
        )

    def sync_entry(self, dn, entry):
        self.connection.search(
            search_base=dn,
            search_filter="(objectClass=*)",
            search_scope=ldap3.BASE,
            attributes="*",
        )
        if len(self.connection.response) == 1:
            old_entry = normalise_entry(self.connection.response[0]["attributes"])
            if entry is None:
                # server entry should be deleted
                print(f"DELETE {dn}")
                self.connection.delete(dn)
                print(self.connection.result)
            else:
                mods = modlist(old_entry, normalise_entry(entry))
                if mods:
                    print(f"CHANGES {dn} {mods}")
                    self.connection.modify(dn, mods)
                    print(self.connection.result)
                else:
                    print(f"NO CHANGE {dn}")
        else:
            if entry is None:
                print(f"NO CHANGE {dn}")
            else:
                print(f"ADD {dn}")
                pprint.pprint(entry)
                self.connection.add(dn, attributes=entry)
                print(self.connection.result)
