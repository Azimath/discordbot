import json
import random
import asyncio


class Dunno:
    commandDict = {"\\command_not_found":"dunno"}

    def __init__(self, client):
        self.client = client
        with open("plugins/dunnos.json", "r") as dunnofile:
            self.dunnos = json.load(dunnofile)

    def dunno(self, commandName, message):
        danno = random.sample(self.dunnos, 1)[0]
        asyncio.ensure_future(self.client.send_message(message.channel, danno))

Class = Dunno

