import asyncio
  
class Util:
    legacy = True
    """This is a plugin for developer utilities to aid in programming and debugging.
       !info: pms information about the channel, server, and author"""    
    def __init__(self, client):
        self.client = client
        
    async def info(self, message):
        target = message.author
        if message.mentions.__len__() == 1:
            targetUser = message.mentions[0]
            await self.client.send_message(target, "User name: " + targetUser.name + "\nUser id: " + targetUser.id + "\nUser discriminator: " + targetUser.discriminator)
            # self.client.send_message(target, "User id: " + targetUser.id)
            # self.client.send_message(target, "User discriminator: " + targetUser.discriminator)
            await self.client.delete_message(message)
        else:
            await self.client.send_message(target, "Channel name: " + message.channel.name + "\nChannel id: " + message.channel.id + "\nServer  name: " + message.server.name + "\nServer id: " + message.server.id + "\nAuthor name: " + message.author.name + "\nAuthor id: " + message.author.id)
            # self.client.send_message(target, "Channel id: " + message.channel.id)
            # self.client.send_message(target, "Server  name: " + message.server.name)
            # self.client.send_message(target, "Server id: " + message.server.id)
            # self.client.send_message(target, "Author name: " + message.author.name)
            # self.client.send_message(target, "Author id: " + message.author.id)
              
    async def game(self, message):
    
        class Game:
            name = ""
            def __init__(self, name):
                self.name = name
                
        await self.client.change_status(Game(message.content[6:]))
    
    commandDict = { "!info" : "info", "!game" : "game"}

Class = Util
