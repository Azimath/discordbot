class Util:
    legacy = True
    """This is a plugin for developer utilities to aid in programming and debugging.
       !info: pms information about the channel, server, and author"""    
    def __init__(self, client):
        self.client = client
        
    def info(self, message):
        target = message.author
        if len(message.mentions) == 1:
            targetUser = message.mentions[0]
            self.client.send_message(target, "User name: %s\nUser id: %s\nUser discriminator: %s" %
                                     (targetUser.name, targetUser.id, targetUser.discriminator))
            self.client.delete_message(message)
        else:
            self.client.send_message(target, "Channel name: %s\nChannel id: %s\nServer  name: %s\nServer id: %s\nAuthor name: %s\nAuthor id: %s" %
                                     (message.channel.name, message.channel.id, message.server.name,
                                      message.server.id, message.author.name, message.author.id))

    def game(self, message):
    
        class Game:
            name = ""
            def __init__(self, name):
                self.name = name
                
        self.client.change_status(Game(message.content[6:]))
    
    commandDict = {"!info":"info", "!game":"game"}

Class = Util
