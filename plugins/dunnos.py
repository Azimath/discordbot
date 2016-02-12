import json
import random
import asyncio


class Dunno:
    commandDict = {"\\command_not_found":"dunno"}

    def __init__(self, client):
        self.client = client
        with open("plugins/dunnos.json", "r") as dunnofile:
            self.dunnos = json.load(dunnofile)

    def dunno(self, commandName, messageObj):
        try:
            with open("plugins/phrasebank.json", "r") as lartfile:
                larts = json.load(lartfile)["lart"]
            self.dunnos.extend(larts)
        except:
            pass

        danno = random.choice(self.dunnos, 1).replace("$who", "<@%s>" % messageObj.author.id)
        asyncio.ensure_future(self.client.send_message(messageObj.channel, danno))

Class = Dunno

