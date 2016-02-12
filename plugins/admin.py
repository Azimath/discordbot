#NOTE: this code uses "permissions", it needs to be imported by a namespace that
#sets the "permissions" builtin to the imported permissions module.
import asyncio
import discord.utils as util
import json

global permissions#to make pycharm happy about it existing

with open('plugins/admin.json', 'r') as configfile:
    config = json.load(configfile)


class Admin:
    """This is a plugin for a few basic admin functions and the almighty censorship cannon.
       Feared by Jerries everywhere.
       !leave: Tells the bot to leave. Only works if you're Azimath.
       !invite: Invites the bot to a new server. Only works if you're Azimath.
       !delete @Target <channel> numberofmessages : Deletes numberofmessages sent by Target.
            If no channel is specified assumes channel it was sent in."""
    def __init__(self, client):
        self.client = client
    
    @permissions.needs_role(permissions.RoleEnum.owner)
    def leave(self, remainder, messageObj):
        asyncio.ensure_future(self.client.leave_server(messageObj.channel.server))
    
    @permissions.needs_role(permissions.RoleEnum.owner)
    def invite(self, remainder, messageObj):
        print("Got an invite: " + remainder)
        asyncio.ensure_future(self.client.accept_invite(remainder))
    
    def newsPurge(self, messageObj):
        permittedChannelId = config["newsChannelId"]
        permittedChannel = util.get(messageObj.server.channels, id=permittedChannelId)
        serverId = config["serverId"]

        if messageObj.channel != permittedChannel and messageObj.server.id == serverId:
            asyncio.ensure_future(self.client.delete_message(messageObj))
            asyncio.ensure_future(self.client.send_message(
                permittedChannel, "moved message from %s: %s" % (messageObj.author.name, messageObj.content))
                )

    def registerNewUser(self, remainder, messageObj):

        if messageObj.mentions:
            status = permissions.addUser(messageObj.server, messageObj.mentions[0])
        elif not remainder.strip():
            status = permissions.addUser(messageObj.server, messageObj.author)
        else:
            raise NotImplemented
        asyncio.ensure_future(self.client.send_message(messageObj.channel, status[1]))

    @permissions.needs_role(permissions.RoleEnum.owner)
    def addUserRole(self, remainder, messageObj):
        args = remainder.split()
        if len(args) != 2 and not len(messageObj.mentions):
            raise Exception

        role = permissions.RoleEnum.lookUp(args[1])
        status = permissions.addUserRole(messageObj.server, messageObj.mentions[0], role)
        asyncio.ensure_future(self.client.send_message(messageObj.channel, status[1]))

    @permissions.needs_role(permissions.RoleEnum.owner)  #WARNING: TODO: does this get run in the correct context?
    def reloadPermissionsConfig(self, remainder, messageObj):
        permissions.reloadConfig()

    @permissions.needs_role(permissions.RoleEnum.globalroot)
    def setPermissionsMode(self, remainder, messageObj):
        args = remainder.split()
        if len(args) != 1:
            raise Exception

        mode = permissions.ModeEnum.lookUp(args[0])
        permissions.setPermissionsMode(messageObj.server, mode)

    @permissions.needs_role(permissions.RoleEnum.owner)
    def setPermissionsRoleId(self, remainder, messageObj):
        if len(remainder.split()) < 2:
            raise Exception  #TODO

        partitiond = remainder.lstrip().partition(" ")
        rolestr = partitiond[0]
        groupstr = partitiond[2]

        gid = util.get(messageObj.server.roles, name=groupstr).id
        role = permissions.RoleEnum.lookUp(rolestr)
        status = permissions.setPermissionRoleId(messageObj.server, role, gid)
        asyncio.ensure_future(self.client.send_message(messageObj.channel, status[1]))

    @permissions.needs_role(permissions.RoleEnum.moderator)
    def delete(self, remainder, messageObj):
        args = remainder.split()
        if len(args) not in [1, 2, 3] and not len(messageObj.mentions):
            raise Exception

        if len(args) == 1:
            number = int(args[0])
            targetUser = messageObj.author
            targetChannel = messageObj.channel
        elif len(args) == 2:
            number = int(args[1])
            targetUser = messageObj.mentions[0]
            targetChannel = messageObj.channel
        else:
            number = int(args[2])
            targetUser = messageObj.mentions[1]
            targetChannel = messageObj.channel_mentions[0]

        print("deleting %s messages channel is %s target is %s" % (number, targetChannel, targetUser))
        asyncio.ensure_future(self.asyncDeleteMessages(targetChannel, targetUser, number, messageObj))

    async def asyncDeleteMessages(self, targetChannel, targetUser, number, messageObj):
        count = 0
        while count < number:
            async for msg in self.client.logs_from(targetChannel, limit=20, before=messageObj):
                if count < number and msg.author == targetUser:
                    await self.client.delete_message(msg)
                    count += 1
                    print("-", end="")
        await self.client.delete_message(messageObj)

    commandDict = {"!invite": "invite",
                   "!leave": "leave",
                   "!delete": "delete",
                   "!add": "registerNewUser",
                   "!addrole": "addUserRole",
                   "!register": "registerNewUser",
                   "!reloadpermissionsconfig": "reloadPermissionsConfig",
                   "a.msn.com": "newsPurge",
                   "!setpmode": "setPermissionsMode",
                   "!setrolegroup": "setPermissionsRoleId"
                   }
Class = Admin
