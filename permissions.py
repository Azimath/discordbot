import json
import asyncio

class User:
    def __init__(self, id, name, permissions):
        self.data = {}
        self.data['id'] = id
        self.data['name'] = name
        self.data['permissions'] = permissions
    
    def hasPermission(self, perm):
        for i in self.data['permissions']:
            if perm == i:
                return true
        return false
    def __json__(self):
        return self.data
        
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__json__'):
            return obj.__json__()
        return json.JSONEncoder.default(self, obj)

class CustomDecoder(json.JSONDecoder):
    def decode(self, JSON_string):
        datas = super(CustomDecoder, self).decode(JSON_string)
        objs = []
        for data in datas:
            objs.append(User(data['id'], data['name'], data['permissions']))
        return objs
        
userbank = []
 
with open('permissions.json', 'r') as userfile:
    userbank = json.loads(userfile.read(), cls=CustomDecoder)
    
def addPermission(userObject, permission):
    user = next(x for x in userbank if x.data['id'] == userObject.id) 
    if user is not None:
        user.data['permissions'].append(permission)
        with open('permissions.json', 'w') as userfile:
            userfile.write(json.dumps(userbank, indent=4, cls=CustomEncoder))
        return True
    else:
        return False
         
def hasPermission(userObject, permission):
    user = next(x for x in userbank if x.data['id'] == userObject.id)
    if user is not None:
        return permission in user.data['permissions']
    else:
        return False

def needs_admin(func):
    async def command(triggerMessage):
        if hasPermission(triggerMessage.author, "admin"):
            await func(triggerMessage)
    return command

def needs_owner(func):
    async def command(triggerMessage):
        if hasPermission(triggerMessage.author, "owner"):
            await func(triggerMessage)
    return command

def needs_moderator(func):
    async def command(triggerMessage):
        if hasPermission(triggerMessage.author, "moderator"):
            await func(triggerMessage)
    return command
    
def needs_base(func):
    async def command(triggerMessage):
        if hasPermission(triggerMessage.author, "base"):
            await func(triggerMessage)
    return command    
    
def needs_permissionsManager(func):
    async def command(triggerMessage):
        if hasPermission(triggerMessage.author, "manager"):
            await func(triggerMessage)
    return command
    
def register(user, triggerMessage):
    new = True
    for i in userbank:
        if i.data['id'] == user.data['id']:
            new = False
            return False
    if new:
        user.data['permissions'].append("base")
        userbank.append(user)
        with open('permissions.json', 'w') as userfile:
            userfile.write(json.dumps(userbank, indent=4, cls=CustomEncoder))
        return True