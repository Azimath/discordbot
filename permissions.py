#NOTE: needs to be imported and set to builtin "permissions"
import json
import discord.utils as util


class RoleEnum:
    admin = "admin"
    owner = "owner"
    moderator = "moderator"
    globalroot = None

    items = [admin, owner, moderator]

    def lookUp(role):
        for x in RoleEnum.items:
            if role == x:  #or whatever mapping is appropriate
                return x
        else:
            raise NotImplemented


class ModeEnum:
    discord = "discord"
    internal = "internal"
    disabled = "disabled"

    items = [discord, internal, disabled]

    def lookUp(mode):
        for x in ModeEnum.items:
            if mode == x:  #or whatever mapping is appropriate
                return x
        else:
            raise NotImplemented


#TODO: this is "groups" basically (?)
class ServerRoles:
    def __init__(self, server):
        #if server is not configured, default deny. TODO: this should wok ok like this?
        if server.id not in permissionstree["config"]:
            self.admin, self.owner, self.moderator = (None, None, None)
            self.mode = ModeEnum.disabled
            return

        self.mode = permissionstree["config"][server.id]["permissionsMode"]

        if self.mode == ModeEnum.discord:
            def getRoleID(role):
                return permissionstree["config"][server.id][role]

            self.roles = dict()
            for x in RoleEnum.items:
                self.roles[x] = util.get(server.roles, id=getRoleID(x))

        elif self.mode == ModeEnum.internal:
            self.roles = dict()
            for x in RoleEnum.items:
                self.roles[x] = x
        else:
            raise NotImplemented

    def getRole(self, enumElement):
        if enumElement is not RoleEnum.globalroot:
            return self.roles[enumElement]
        elif enumElement == RoleEnum.globalroot:
            return RoleEnum.globalroot
        else:
            raise NotImplemented  #NOTE: this is unreachable


def load():
    global permissionstree
    with open('permissions.json', 'r') as file:
        permissionstree = json.load(file)


def save():
    with open('permissions.json', 'w') as userfile:
            json.dump(permissionstree, userfile, indent=4)


def reloadConfig():
    print("reloading permissions")
    global serverRolesGlobal
    keys = list(serverRolesGlobal.keys())
    for x in keys:
        del serverRolesGlobal[x]
    load()


def addUser(serverObj, userObj):
    global permissionstree
    checkGlobal(serverObj)

    if not serverRolesGlobal[serverObj].mode == ModeEnum.internal:
        raise NotImplemented

    if serverObj.id not in permissionstree["perms"]:
        permissionstree["perms"][serverObj.id] = dict()

    if userObj.id not in permissionstree["perms"][serverObj.id]:
        permissionstree["perms"][serverObj.id][userObj.id] = {
            "name": userObj.name,  #WARNING: do *NOT* use this field, this is just for config readability
            "roles": list()
            }
        save()
        return True, "User %s has been registered." % userObj.name
    else:
        return False, "User %s is already registered." % userObj.name


def addUserRole(serverObj, userObj, role):
    global permissionstree
    checkGlobal(serverObj)

    if not serverRolesGlobal[serverObj].mode == ModeEnum.internal:
        raise NotImplemented

    if serverObj.id in permissionstree["perms"] and \
            userObj.id in permissionstree["perms"][serverObj.id]:
        if role not in permissionstree["perms"][serverObj.id][userObj.id]["roles"]:
            permissionstree["perms"][serverObj.id][userObj.id]["roles"].append(role)
            save()
            return True, "%s is now (also) a %s" % (userObj.name, role)
        else:
            return False, "%s is already a %s" % (userObj.name, role)
    else:
        raise LookupError


def setPermissionsMode(serverObj, mode):
    global permissionstree

    if serverObj.id not in permissionstree["config"]:
        permissionstree["config"][serverObj.id] = dict()

    permissionstree["config"][serverObj.id]["permissionsMode"] = mode
    if mode == ModeEnum.discord:
        for x in RoleEnum.items:
            if x not in permissionstree["config"][serverObj.id]:
                permissionstree["config"][serverObj.id][x] = ""
    save()
    reloadConfig()


def setPermissionRoleId(serverObj, role, id):
    global permissionstree
    checkGlobal(serverObj)

    if not serverRolesGlobal[serverObj].mode == ModeEnum.internal:
        raise NotImplemented

    permissionstree["config"][serverObj.id][role] = id
    save()
    return True, "%s set to %s" % (role, id)

def checkGlobal(serverObj):
    if serverObj not in serverRolesGlobal:
                serverRolesGlobal[serverObj] = ServerRoles(serverObj)

serverRolesGlobal = dict()
load()


def hasRole(userObj, serverObj, role):
    checkGlobal(serverObj)
    if userObj.id in permissionstree["config"]["globalRoot"]:
        return True
    if serverRolesGlobal[serverObj].mode == ModeEnum.discord:
        return role in userObj.roles
    elif serverRolesGlobal[serverObj].mode == ModeEnum.internal:
        if serverObj.id in permissionstree["perms"] and \
                userObj.id in permissionstree["perms"][serverObj.id]:
            return role in permissionstree["perms"][serverObj.id][userObj.id]["roles"]
        else:
            raise LookupError
    else:
        raise NotImplemented


def needs_role(enumRole):
    def decorator(func):
        def funcproxy(self, remainder, messageObj, *args, **kwargs):
            checkGlobal(messageObj.server)
            role = serverRolesGlobal[messageObj.server].getRole(enumRole)
            if hasRole(messageObj.author, messageObj.server, role):
                return func(self, remainder, messageObj, *args, **kwargs)
            else:
                raise PermissionError
        return funcproxy
    return decorator

