class UserLDAPSerializer:
    def __init__(self, base_dn, domain_sid=None):
        self.base_dn = base_dn
        self.domain_sid = domain_sid

    def serialize(self, user):
        dn = f"uid={user.username},{self.base_dn}"
        entry = {
            "objectClass": ["top", "account", "extensibleObject"],
            "uid": user.username,
            "cn": user.get_full_name(),
            "mail": user.email,
        }
        if user.posix:
            entry["objectClass"].append("posixAccount")
            entry["gecos"] = user.get_full_name()
            entry["homeDirectory"] = f"/home/{user.username}"
            entry["loginShell"] = user.posix.shell
            entry["uidNumber"] = user.posix.uid
            entry["gidNumber"] = user.posix.uid
            if self.domain_sid:
                entry["objectClass"].append("sambaSamAccount")
                entry["sambaSID"] = f"{self.domain_sid}-{user.posix.uid * 2 + 1000}"
                entry["sambaAcctFlags"] = "[U          ]"
            if len(user.sshkey_set.filter(enabled=True)) > 0:
                entry["objectClass"].append("ldapPublicKey")
                for sshkey in user.sshkey_set.filter(enabled=True):
                    entry["sshPublicKey"] = sshkey.key.encode()
            if user.posix.password:
                entry["userPassword"] = b"{CRYPT}" + user.posix.password.encode()
        return dn, entry


class GroupLDAPSerializer:
    def __init__(self, base_dn, users_base_dn):
        self.base_dn = base_dn
        self.users_base_dn = users_base_dn

    def serialize(self, group):
        dn = f"cn={group.name},{self.base_dn}"
        entry = {
            "objectClass": ["top", "groupOfNames"],
            "cn": group.name,
            "member": [],
        }
        for user in group.user_set.all():
            entry["member"].append(f"uid={user.username},{self.users_base_dn}")
        if len(entry["member"]) == 0:
            return dn, None
        return dn, entry


class PosixGroupLDAPSerializer:
    def __init__(self, base_dn):
        self.base_dn = base_dn

    def serialize(self, group):
        dn = f"cn={group.name},{self.base_dn}"
        entry = {
            "objectClass": ["top", "posixGroup"],
            "cn": group.name,
            "gidNumber": group.posix.gid,
            "memberUid": [],
        }
        for user in group.user_set.all():
            entry["memberUid"].append(user.username)
        return dn, entry
