import random

class Games:
    legacy = True
    """This is a plugin for fun things you can use to play with [^_^].
       !flip, !coin: Flips a coin
       !trick: Does a super cool magic trick"""    
    def __init__(self, client):
        self.client = client
        
    async def flip(self, message):
        target = message.channel
        if random.randint(0,1) == 0:
            toSend = "Tails"
        else:
            toSend = "Heads"
        
        await self.client.send_message(target, toSend)
    
    async def trick(self, message):
        target = message.channel
        suits = [":hearts:", ":clubs:", ":diamonds:", ":spades:"]
        values = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Jack", "Queen", "King"]
        suit = random.choice(suits)
        value = random.choice(values)
        await self.client.send_message(target, "This is your card. Remember it, but don't tell me what it is. " + suit + " " + value)
        await self.client.send_message(target, "*shuffles*")
        await self.client.send_message(target, "*shuffles*")
        await self.client.send_message(target, "*shuffles*")
        await self.client.send_message(target, "*cuts*")
        await self.client.send_message(target, "Is this your card? " + suit + " " + value)
        
    async def roll(self, message):
        target = message.channel
        toParse = message.content[5:]
        if "∞" in toParse:
            result = "∞"
            await self.client.send_message(target, "Rolled " + toParse + ": " + "∞")

        else:    
            rolls = int(toParse[1:toParse.index('d')])
            toParse = toParse[toParse.index('d'):]
            index = toParse.find('+')
            if index == -1:
                index = toParse.find('-')
            if index == -1:
                size = int(toParse[toParse.index('d')+1:])
                mod = 0
            else:
                size = int(toParse[1:index])
                mod = int(int(toParse[index:]))
            
            result = 0
            
            if rolls > 100000:
                await self.client.send_message(target, "Fuck off")
            else:
                for i in range(0, rolls):
                    result = result + random.randrange(1, size+1)
                
                result = result + mod
                await self.client.send_message(target, "Rolled " + str(rolls) + "d" + str(size) + "+" + str(mod) + ": " + "**" + str(result) + "**")
        
    commandDict = { "!coin" : "flip", "!flip" : "flip", "!trick" : "trick", "!roll" : "roll" }

Class = Games
