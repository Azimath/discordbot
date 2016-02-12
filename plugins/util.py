import asyncio


class Util:
    """This is a plugin for developer utilities to aid in programming and debugging.
       !info: pms information about the channel, server, and author"""    
    def __init__(self, client):
        self.client = client
        
    def info(self, remainder, messageObj):
        target = messageObj.author
        if len(messageObj.mentions) == 1:
            targetUser = messageObj.mentions[0]
            asyncio.ensure_future(
                self.client.send_message(target, "User name: %s\nUser id: %s\nUser discriminator: %s" %
                                         (targetUser.name, targetUser.id, targetUser.discriminator)))
            asyncio.ensure_future(self.client.delete_message(messageObj))
        else:
            asyncio.ensure_future(
                self.client.send_message(target,
                                         "Channel name: %s\nChannel id: %s\nServer  name: %s\nServer id: %s\nAuthor name: %s\nAuthor id: %s" %
                                         (messageObj.channel.name, messageObj.channel.id, messageObj.server.name,
                                          messageObj.server.id, messageObj.author.name, messageObj.author.id)))
    
    commandDict = {"!info": "info"}

Class = Util
