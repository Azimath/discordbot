import json
from enum import Enum

#class User(dict):
#    def hasPermission(self, perm):
#        return perm in self['permissions']


class Permissions(Enum):
    admin = 1
    owner = 2
    moderator = 3


def load():
    global userbank
    with open('permissions.json', 'r') as userfile:
        #a dictionary of users: {id:{id: , name: , permissions:[Permissions...]}} indexed by user.id
        userbank = json.load(userfile)


def save():
    with open('permissions.json', 'w') as userfile:
            json.dump(userbank, userfile, indent=4)


def register(userObj):
    def toDict(userObj):
        return {"id": userObj.id,
                "name": userObj.name,
                "permissions": list()}

    uo = toDict(userObj)
    isNew = uo["id"] in userbank
    if isNew:
        userbank[userObj.id] = uo
        save()
    return isNew


def addPerm(userObj, perm):
    userbank[userObj.id]["permissions"].append(perm)
    save()


def hasPermission(userObj, permission):
    return permission in userbank[userObj.id]["permissions"]


def needs_permission(permission):
    def decorator(func):
        def proxy(remainder, messageObj,*args, **kwargs):
            if hasPermission(messageObj.author, permission):
                func(remainder, messageObj, *args, **kwargs)
        return proxy
    return decorator

def needs_permission_legacy(permission):
    def decorator(func):
        def proxy(messageObj,*args, **kwargs):
            if hasPermission(messageObj.author, permission):
                func(messageObj, *args, **kwargs)
        return proxy
    return decorator

