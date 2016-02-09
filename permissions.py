import json
import discord.utils as util


class RoleEnum:
    admin = "admin"
    owner = "owner"
    moderator = "moderator"


#TODO: this is "groups" basically (?)
class ServerRoles:
    def __init__(self, server):
        #if server is not configured, default deny. TODO: this should be ok?
        if server.id not in permissionstree["config"]:
            self.admin, self.owner, self.moderator = (None, None, None)
            return

        def getRoleID(role):
            return permissionstree["config"][server.id][role]

        self.admin = util.get(server.roles, id=getRoleID(RoleEnum.admin))
        self.owner = util.get(server.roles, id=getRoleID(RoleEnum.owner))
        self.moderator = util.get(server.roles, id=getRoleID(RoleEnum.moderator))

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


def hasRole(userObj, role):
    return role in userObj.roles


def needs_role(enumRole):
    def decorator(func):
        def proxy(self, remainder, messageObj, *args, **kwargs):
            if messageObj.server not in serverRolesGlobal:
                serverRolesGlobal[messageObj.server] = ServerRoles(messageObj.server)
            role = serverRolesGlobal[messageObj.server].getRole(enumRole)
            if hasRole(messageObj.author, role):
                func(self, remainder, messageObj, *args, **kwargs)
        return proxy
    return decorator


def needs_role_legacy(enumRole):
    def decorator(func):
        def proxy(self, messageObj, *args, **kwargs):
            if messageObj.server not in serverRolesGlobal:
                serverRolesGlobal[messageObj.server] = ServerRoles(messageObj.server)
            role = serverRolesGlobal[messageObj.server].getRole(enumRole)
            if hasRole(messageObj.author, role):
                func(messageObj, *args, **kwargs)
        return proxy
    return decorator

