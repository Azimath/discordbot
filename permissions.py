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
    
def hasPermission(userObject, permission):
    user = next(x for x in userbank if x.data['id'] == userObject.id)
    if user is not None:
        return permission in user.data['permissions']
    else:
        return False

def needs_admin(func):
    async def command(self, message):
        if hasPermission(message.author, "admin"):
            await func(self, message)
    return command

def needs_owner(func):
    async def command(self, message):
        if hasPermission(message.author, "owner"):
            await func(self, message)
    return command

def needs_moderator(func):
    async def command(self, message):
        if hasPermission(message.author, "moderator"):
            await func(self, message)
    return command
    
def register(user, message):
    new = True
    for i in userbank:
        if i.data['id'] == user.data['id']:
            new = False
            return False
    if new:
        userbank.append(user)
        with open('permissions.json', 'w') as userfile:
            userfile.write(json.dumps(userbank, indent=4, cls=CustomEncoder))
        return True