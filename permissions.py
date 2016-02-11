import json
import discord.utils as util


class RoleEnum:
    admin = "admin"
    owner = "owner"
    moderator = "moderator"

class ModeEnum:
    discord = "discordRoles"
    internal = "internal"

#TODO: this is "groups" basically (?)
class ServerRoles:
    def __init__(self, server, permissionmode):
        #if server is not configured, default deny. TODO: this should wok ok like this?
        if server.id not in permissionstree["config"]:
            self.admin, self.owner, self.moderator = (None, None, None)
            return

        self.mode = permissionstree["config"][server.id]["permissionsMode"]

        if self.mode == ModeEnum.discord:
            def getRoleID(role):
                return permissionstree["config"][server.id][role]

            self.admin = util.get(server.roles, id=getRoleID(RoleEnum.admin))
            self.owner = util.get(server.roles, id=getRoleID(RoleEnum.owner))
            self.moderator = util.get(server.roles, id=getRoleID(RoleEnum.moderator))

        elif permissionmode == ModeEnum.internal:
            self.admin = RoleEnum.admin
            self.owner = RoleEnum.owner
            self.moderator = RoleEnum.moderator
        else:
            raise NotImplemented

    def getRole(self, enumElement):
        if enumElement == RoleEnum.admin:
            return self.admin
        elif enumElement == RoleEnum.owner:
            return self.owner
        elif enumElement == RoleEnum.moderator:
            return self.moderator
        else:
            raise NotImplemented


def load():
    global permissionstree
    with open('permissions.json', 'r') as file:
        permissionstree = json.load(file)


def save():
    with open('permissions.json', 'w') as userfile:
            json.dump(permissionstree, userfile, indent=4)


serverRolesGlobal = dict()
load()

#def register(userObj):
#    if permissionsMode == "discord":
#        raise NotImplemented
#    else:
#        def toDict(userObj):
#            return {"id": userObj.id,
#                    "name": userObj.name,
#                    "roles": list()}
#
#        uo = toDict(userObj)
#        isNew = uo["id"] in userbank
#        if isNew:
#            userbank[userObj.id] = uo
#            save()
#        return isNew


#def addPerm(userObj, perm):
#    if permissionsMode == "discord":
#        raise NotImplemented
#    else:
#        userbank[userObj.id]["permissions"].append(perm)
#        save()


def hasRole(userObj, serverObj, role):
    if serverRolesGlobal[serverObj].mode == ModeEnum.discord:
        return role in userObj.roles
    elif serverRolesGlobal[serverObj].mode == ModeEnum.internal:
        return role in permissionstree["perms"][serverObj.id][userObj.id]["roles"]
    else:
        raise NotImplemented


def needs_role(enumRole):
    def decorator(func):
        def funcproxy(self, remainder, messageObj, *args, **kwargs):
            if messageObj.server not in serverRolesGlobal:
                serverRolesGlobal[messageObj.server] = ServerRoles(messageObj.server)
            role = serverRolesGlobal[messageObj.server].getRole(enumRole)
            if hasRole(messageObj.author, messageObj.server, role):
                return func(self, remainder, messageObj, *args, **kwargs)
            else:
                raise PermissionError
        return funcproxy
    return decorator


def needs_role_legacy(enumRole):
    def decorator(func):
        def proxy(self, messageObj, *args, **kwargs):
            if messageObj.server not in serverRolesGlobal:
                serverRolesGlobal[messageObj.server] = ServerRoles(messageObj.server)
            role = serverRolesGlobal[messageObj.server].getRole(enumRole)
            if hasRole(messageObj.author, messageObj.server, role):
                return func(self, messageObj, *args, **kwargs)
            else:
                raise PermissionError
        return proxy
    return decorator

