# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from typing import OrderedDict

import ldap3
import ssl
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


def modlist(old, new, ignore_attr_types=[], debug=False):
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
                    print(f"{attr}: {old[attr]} -> {new[attr]}")
                mods[attr] = [(ldap3.MODIFY_REPLACE, new[attr])]
        else:
            # delete
            if debug:
                print(f"{attr}: {old[attr]} -> (none)")
            mods[attr] = [(ldap3.MODIFY_DELETE, [])]
    for attr in new.keys():
        if attr in ignore_attr_types:
            continue
        if attr in old:
            pass
        else:
            # add
            if debug:
                print(f"{attr}: (none) -> {new[attr]}")
            mods[attr] = [(ldap3.MODIFY_ADD, new[attr])]
    return mods


def sync_user(user, dry_run=False):
    if not settings.LDAPSYNC_USERS_BASE_DN:
        return
    dn, entry = serializers.serialize_user(
        user, settings.LDAPSYNC_USERS_BASE_DN, domain_sid=settings.LDAPSYNC_DOMAIN_SID
    )
    server = LDAP(dry_run=dry_run)
    server.sync_entry(dn, entry)
    if settings.LDAPSYNC_POSIX_GROUPS_BASE_DN:
        dn, entry = serializers.serialize_posixuser_group(
            user, settings.LDAPSYNC_POSIX_GROUPS_BASE_DN
        )
        server.sync_entry(dn, entry)


def sync_group(group, dry_run=False):
    if not settings.LDAPSYNC_GROUPS_BASE_DN:
        return
    dn, entry = serializers.serialize_group(
        group,
        settings.LDAPSYNC_GROUPS_BASE_DN,
        users_base_dn=settings.LDAPSYNC_USERS_BASE_DN,
    )
    if settings.LDAPSYNC_POSIX_GROUPS_BASE_DN and group.posix:
        posix_dn, posix_entry = serializers.serialize_posixgroup(
            group, settings.LDAPSYNC_POSIX_GROUPS_BASE_DN
        )
    server = LDAP(dry_run=dry_run)
    server.sync_entry(dn, entry)
    if settings.LDAPSYNC_POSIX_GROUPS_BASE_DN and group.posix:
        server.sync_entry(posix_dn, posix_entry)


def ldap_connection():
    if settings.LDAPSYNC_TLS:
        tls = ldap3.Tls(**settings.LDAPSYNC_TLS)
    else:
        tls = None
    server = ldap3.Server(
        settings.LDAPSYNC_HOST,
        port=settings.LDAPSYNC_PORT,
        use_ssl=settings.LDAPSYNC_USE_SSL,
        tls=tls,
    )
    connection = ldap3.Connection(
        server,
        user=settings.LDAPSYNC_USER,
        password=settings.LDAPSYNC_PASSWORD,
        auto_bind=True,
    )
    return connection


class LDAP:
    def __init__(self, debug=False, dry_run=False):
        self.debug = debug
        self.dry_run = dry_run
        if settings.LDAPSYNC_DRY_RUN:
            self.dry_run = True
        self.connection = ldap_connection()
        self.seen = {}

    def sync_entry(self, dn, entry):
        if self.debug:
            print(f"--- {dn} ---")
            print(entry)
        self.seen[dn] = True
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
                if self.debug:
                    print(f"DELETE {dn}")
                if not self.dry_run:
                    self.connection.delete(dn)
                    if self.debug:
                        print(self.connection.result)
            else:
                mods = modlist(old_entry, normalise_entry(entry), debug=self.debug)
                if mods:
                    if self.debug:
                        print(f"CHANGES {dn} {mods}")
                    if not self.dry_run:
                        self.connection.modify(dn, mods)
                        if self.debug:
                            print(self.connection.result)
                else:
                    if self.debug:
                        print(f"NO CHANGE {dn}")
        else:
            if entry is None:
                if self.debug:
                    print(f"NO CHANGE {dn}")
            else:
                if self.debug:
                    print(f"ADD {dn}")
                if not self.dry_run:
                    self.connection.add(dn, attributes=entry)
                    if self.debug:
                        print(self.connection.result)

    def auto_delete(self, base_dn):
        self.connection.search(
            search_base=base_dn,
            search_filter="(objectClass=*)",
            search_scope=ldap3.SUBTREE,
            attributes=[],
        )
        if len(self.connection.response) > 0:
            for response in self.connection.response:
                dn = response["dn"]
                if dn == base_dn:
                    continue
                if dn in self.seen:
                    continue
                if not self.dry_run:
                    if self.debug:
                        print(f"DELETE {dn}")
                    self.connection.delete(dn)
                    if self.debug:
                        print(self.connection.result)
