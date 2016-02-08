import permissions
import asyncio

class Admin:
    legacy = True
    """This is a plugin for a few basic admin functions and the almighty censorship cannon.
       Feared by Jerries everywhere.
       !leave: Tells the bot to leave. Only works if you're Azimath.
       !invite: Invites the bot to a new server. Only works if you're Azimath.
       !delete @Target <channel> numberofmessages : Deletes numberofmessages sent by Target. If no channel is specified assumes channel it was sent in."""    
    def __init__(self, client):
        self.client = client
    
    @permissions.needs_owner    
    async def leave(self, message):
        await self.client.leave_server(message.channel.server)
    
    @permissions.needs_owner
    async def invite(self, message):
        print("Got an invite: " + message.content[8:])
        await self.client.accept_invite(message.content[8:])
    
    async def newsPurge(self, message):
        if message.author.id == "102980090970779648" and message.channel.id != "102984909320110080":
            await self.client.delete_message(message)
    
    async def registerNewUser(self, message):  
        if message.mentions.__len__() == 0:
            id = message.author.id
            name = message.author.name
            if permissions.register(permissions.User(id, name, ["base"]), message):
                await self.client.send_message(message.channel, "User id " + message.author.id + " has been registered")
            else:
                await self.client.send_message(message.channel, "User id " + message.author.id + " is already registered")
        else:
            id = message.mentions[0].id
            name = message.mentions[0].name
            if permissions.register(permissions.User(id, name, ["base"]), message):
                await self.client.send_message(message.channel, "User id " + id + " has been registered")
            else:
                await self.client.send_message(message.channel, "User id " + id + " is already registered")
    
    @permissions.needs_moderator
    async def delete(self, message):
                #find out if the sender has delete permissions
                victim = None
                channel = None
                command = message.content.split() #probably the best way to do this, right?
                if len(command) > 1: #parse the fuck out of it
                    if len(message.mentions) == 0:
                        victim = None
                    elif len(message.mentions) > 1:
                        channel = None
                    else:
                        victim = message.mentions[0]
                    
                    if len(command) > 2:
                        for n in range(1, command.__len__()):
                            try:
                                number = int(command[n])
                                break
                            except:
                                number = 1
                    
                    if len(message.channel_mentions) == 0:
                        channel = message.channel
                    elif len(message.channel_mentions) > 1:
                        channel = None
                    else:
                        channel = message.channel_mentions[0]
                #actually do the stuff
                
                    if victim is not None and channel is not None:
                        print("authorized, channel is " + channel.name + " target is " + victim.name)
                        print("deleting " + str(number) + " messages")
                        deleted = 0
                        for x in reversed(self.client.messages):
                            if x.author == victim and x.channel == channel and deleted < number:
                                await self.client.delete_message(x)
                                deleted = deleted + 1
                                print("deleted " + str(deleted))
                            if deleted >= number:
                                await self.client.send_message(channel, "Removed " + str(deleted) + " messages belonging to " + victim.name)
                                break
                        print("messages remaining: " + str(number-deleted))
                    else:
                        print("Invalid victim or channel")
                        print(victim == None)
                        print(channel == None)
                    
                    
    commandDict = { "!invite" : "invite", "!leave" : "leave", "!delete" : "delete", "!add" : "registerNewUser", "!register" : "registerNewUser", "a.msn.com" : "newsPurge" }

Class = Admin
