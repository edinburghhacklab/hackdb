def serialize_user(user, base_dn, domain_sid=None):
    dn = f"uid={user.username},{base_dn}"
    if not user.is_active:
        return dn, None
    entry = {
        "objectClass": ["top", "account", "extensibleObject"],
        "uid": [user.username],
        "mail": [user.email],
    }
    if user.get_full_name():
        entry["cn"] = [user.get_full_name()]
    else:
        entry["cn"] = [user.username]
    if user.posix:
        entry["objectClass"].append("posixAccount")
        entry["gecos"] = [user.get_full_name().encode("ascii", "replace").decode()]
        entry["homeDirectory"] = [f"/home/{user.username}"]
        entry["loginShell"] = [user.posix.shell]
        entry["uidNumber"] = [user.posix.uid]
        entry["gidNumber"] = [user.posix.uid]
        if domain_sid:
            entry["objectClass"].append("sambaSamAccount")
            entry["sambaSID"] = [f"{domain_sid}-{user.posix.uid * 2 + 1000}"]
            entry["sambaAcctFlags"] = ["[U          ]"]
        if len(user.sshkey_set.filter(enabled=True)) > 0:
            entry["objectClass"].append("ldapPublicKey")
            entry["sshPublicKey"] = []
            for sshkey in user.sshkey_set.filter(enabled=True):
                entry["sshPublicKey"].append(sshkey.key.encode())
        if len(user.nfctokens.filter(enabled=True)) > 0:
            entry["ehlabNfcToken"] = []
            for nfctoken in user.nfctokens.filter(enabled=True).order_by("uid"):
                entry["ehlabNfcToken"].append(nfctoken.uid)
        if user.posix.password:
            if user.posix.password.lower().startswith("{ssha}"):
                entry["userPassword"] = [user.posix.password.encode()]
            else:
                entry["userPassword"] = [b"{CRYPT}" + user.posix.password.encode()]
    return dn, entry


def serialize_group(group, base_dn, users_base_dn):
    dn = f"cn={group.name},{base_dn}"
    entry = {
        "objectClass": ["top", "groupOfNames", "extensibleObject"],
        "cn": [group.name],
        "member": [],
    }
    for user in group.user_set.filter(is_active=True).order_by("username"):
        entry["member"].append(f"uid={user.username},{users_base_dn}")
    if len(entry["member"]) == 0:
        return dn, None
    try:
        if group.properties.description:
            entry["description"] = [group.properties.description]
    except:
        pass
    return dn, entry


def serialize_posixgroup(group, base_dn):
    dn = f"cn={group.name},{base_dn}"
    entry = {
        "objectClass": ["top", "posixGroup"],
        "cn": [group.name],
        "gidNumber": [group.posix.gid],
        "memberUid": [],
    }
    for user in group.user_set.filter(is_active=True).order_by("username"):
        entry["memberUid"].append(user.username)
    if len(entry["memberUid"]) == 0:
        return dn, None
    return dn, entry


def serialize_posixuser_group(user, base_dn):
    dn = f"cn={user.username},{base_dn}"
    if not user.is_active:
        return dn, None
    entry = {
        "objectClass": ["top", "posixGroup"],
        "cn": [user.username],
        "gidNumber": [user.posix.uid],
    }
    return dn, entry
