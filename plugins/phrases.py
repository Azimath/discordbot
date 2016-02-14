import random
import json
import asyncio
from discord import utils as util


#there are: mention+keword replies, comand replies:[static, random]
#TODO: move static data to json file
#TODO: this is way too complicated
class Phrases:
    """A plugin for giving various kinds of random phrases.
       !lart user : uses the LART on the given user.
       !praise user : praises the user.
       !pal : is this pal?
       !mango : where is mang0?
       !eightball : Ask the magic eightball a question. Satisfaction not guarunteed.
       !addphrase phrasebank phrase : adds phrase to the given phrasebank.
          The phrasebank for a given command is generally the name of the command.
       !baddragon : give me some sugah, baby
       !wiki : links to the iaa wiki
       !apply : links to the membership application
       !tests : PMs the user links to all required membership tests
       !constitution : links to the constitution
       !sonic : links to a random page on either the archie sonic wiki or the sonic fanon wiki"""    
    def __init__(self, client):
        self.client = client
        
        self.phrasebank = {}
        with open('plugins/phrasebank.json', 'r') as phrasefile:
            self.phrasebank = json.load(phrasefile)

    def __getattr__(self, item):
        command = item

        #commands, literal, commands that use db with other name
        if command in self.phrasebank or command in self.phrasebank["directmap"] or command in ["buydinner"]:
            return self.reply(command)

        #on fallthrough
        raise AttributeError

    #praises, larts, buydinner(target is always author) => praises
    def reply(self, command):
        def func(remainder, messageObj):
            channelType = None
            if command in ["plot"]:
                if self.client.user not in messageObj.mentions:
                    return

            if command == "buydinner":
                phrasetype = "praise"
            else:
                phrasetype = command

            if command == "pal":
                selector = int(not bool(random.randrange(100)))
            else:
                selector = random.randrange(len(self.phrasebank[phrasetype]))

            if command in ["pal", "buydinner"]:
                mention = messageObj.author
            elif command in ["praise", "lart"]:
                remainder = remainder.strip()
                if remainder:
                    found = util.get(messageObj.server.members, name=remainder)  #TODO: reverse lookup
                    if found:
                        mention = found
                    else:
                        mention = remainder
                else:
                    mention = messageObj.author
            else:
                pass

            if command in self.phrasebank["directmap"]:
                msg = self.phrasebank["directmap"][command]
            elif command == "baddragon":
                msg = "https://bad-dragon.com/products/%s" % self.phrasebank[phrasetype][selector]
            elif command == "eightball":
                msg = ":8bal:" % self.phrasebank[phrasetype][selector]
            elif command in ["praise", "lart", "pal", "buydinner"]:
                try:  #discord
                    msg = self.phrasebank[phrasetype][selector].replace("$who", "<@%s>" % mention.id)
                except AttributeError:  #string
                    msg = self.phrasebank[phrasetype][selector].replace("$who", mention)
            else:
                msg = self.phrasebank[phrasetype][selector]

            if command in ["tests"]:
                channelType = "pm"

            print("%s: %s" % (command, msg))
            channel = messageObj.author if channelType == "pm" else messageObj.channel
            asyncio.ensure_future(self.client.send_message(channel, msg))

        return func

    #TODO: WARNING: not all phrasebank items are lists now, this will break if used with an item of the wrong type
    @permissions.needs_role(permissions.RoleEnum.moderator)  #TODO: idk what level is needed
    def addphrase(self, remainder, messageObj):
        if len(remainder.split()) < 2:
            raise Exception  #TODO

        partitiond = remainder.lstrip().partition(" ")
        phrasebanktarget = partitiond[0]
        phrase = partitiond[2]

        print("trying to add phrase: \"" + phrase + "\" to bank " + phrasebanktarget)
        
        if phrasebanktarget in self.phrasebank:
            if not isinstance(self.phrasebank[phrasebanktarget], list):
                raise NotImplemented  #TODO
            self.phrasebank[phrasebanktarget].append(phrase)
        else:
            self.phrasebank[phrasebanktarget] = list()  #TODO: defaultdict with list() instead of this?
            self.phrasebank[phrasebanktarget].append(phrase)
        with open('phrasebank.json', 'w') as phrasefile:
            phrasefile.write(json.dumps(self.phrasebank, indent=4))
            self.client.send_message(messageObj.channel, "Added phrase " + phrase)

    commandDict = {"!lart": "lart",
                   "!praise": "praise",
                   "!buydinner": "buydinner",
                   "!baddragon": "baddragon",
                   "!pal": "pal",
                   "!mango": "mango",
                   "!mang0": "mango",
                   "!eightball": "eightball",
                   "!8ball": "eightball",
                   "!tests": "tests",
                   "!popori": "popori",
                   "!addphrase": "addphrase",
                   "┻": "unflip",
                   "!floor": "floor",
                   "!wiki": "wiki",
                   "!apply": "application",
                   "!application": "application",
                   "!constitution": "constitution",
                   "!sonic": "sonic",
                   "!sanic": "sonic",
                   "plot": "plot"
                   }
Class = Phrases
