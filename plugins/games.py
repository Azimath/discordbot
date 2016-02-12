import asyncio
import random


class Games:
    """This is a plugin for fun things you can use to play with [^_^].
       !flip, !coin: Flips a coin
       !trick: Does a super cool magic trick"""    
    def __init__(self, client):
        self.client = client
        
    def flip(self, remainder, messageObj):
        target = messageObj.channel
        result = "Tails" if random.randint(0, 1) else "Heads"
        asyncio.ensure_future(self.client.send_message(target, result))
    
    def trick(self, remainder, messageObj):
        target = messageObj.channel
        suits = [":hearts:", ":clubs:", ":diamonds:", ":spades:"]
        values = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Jack", "Queen", "King"]
        suit = random.choice(suits)
        value = random.choice(values)

        story = """This is your card. Remember it, but don't tell me what it is. %s %s
            *shuffles*
            *shuffles*
            *shuffles*
            *cuts*
            Is this your card? %s %s""" % (suit, value, suit, value)

        asyncio.ensure_future(self.orderedMessage(target, story))

    async def orderedMessage(self, channel, multiMessage):
        for line in multiMessage.split("\n"):
            await self.client.send_message(channel, line.strip())

    def roll(self, remainder, messageObj):
        target = messageObj.channel

        arg = remainder.strip().split()[0]
        p1 = arg.partition("d")
        dNum = p1[0]

        if "+" in p1[2]:
            dSize, _, mod = tuple(p1[2].partition("+"))
        elif "-" in p1[2]:
            dSize, _, mod = tuple(p1[2].partition("-"))
        else:
            dSize = p1[2]
            mod = 0

        dSize = int(dSize)
        dNum = int(dNum)
        mod = int(mod)

        if dNum > 100000:
            asyncio.ensure_future(self.client.send_message(target, "Fuck off"))
            return

        result = sum([random.randint(1, dSize) for d in range(0, dNum)]) + mod

        if "∞" in remainder:
            result = "∞"

        asyncio.ensure_future(self.client.send_message(target, "Rolled %sd%s%s: **%s**" % (dNum, dSize, mod if mod else "", result)))

    commandDict = {"!coin": "flip", "!flip": "flip", "!trick": "trick", "!roll": "roll"}

Class = Games
