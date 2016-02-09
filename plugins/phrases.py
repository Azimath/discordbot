import random
import json
import asyncio


#TODO: move static data to json file
class Phrases:
    legacy = True
    """A plugin for giving various kinds of random phrases.
       !lart user : uses the LART on the given user.
       !praise user : praises the user.
       !pal : is this pal?
       !mango : where is mang0?
       !eightball : Ask the magic eightball a question. Satisfaction not guarunteed.
       !addphrase phrasebank phrase : adds phrase to the given phrasebank.
          The phrasebank for a given command is generally the plural of the command.
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
        methods = ['sonic', 'praise', 'popori', 'unflip', 'eightball', 'pal', 'sonic', 'wiki', 'constitution',
                   'eightball', 'lart', 'tests', 'baddragon', 'application', 'mango', 'application', 'mango',
                   'plot', 'floor', 'addphrase', 'buydinner']

        if item in methods:
            command = item
        else:
            raise AttributeError

        directmap = {
            "popori": "https://www.youtube.com/watch?v=gbNN3grTdDk",
            "constitution": "https://docs.google.com/document/d/1XKFRQhzxwhjjtW1RnCc_ZhesRqavvM3F5z1LALfve48/",
            "wiki": "http://iaa.wikia.com",
            "application": "https://docs.google.com/forms/d/1bURXLKIo30XLX3RASg2B8XVLsYpp6GYXn84IT2F9hbM/viewform",
            "unflip": "┬─┬﻿ ノ( ゜-゜ノ)",
            "floor": "http://i.imgur.com/3OYeOxK.jpg",
            "mango": "mang0 is in jail for multishining a kangaroo BibleThump"
            }

        if command in ["praise", "lart", "buydinner"]:
            return lambda messageObj, remainder: self.at_sender(command, messageObj, remainder)
        elif command in directmap:
            msg = directmap[item]
            return lambda messageObj, _: self.literal(command, messageObj, msg)
        elif command == "tests":
            msg = "Take each of the following tests. Save a screenshot of each result.\n" \
                  "MBTI: http://www.humanmetrics.com/cgi-win/jtypes2.asp\n" \
                  "Enneagram: http://www.eclecticenergies.com/enneagram/test.php Take both tests for best results.\n" \
                  "BIG5: http://personality-testing.info/tests/BIG5.php\n" \
                  "Temperaments: http://personality-testing.info/tests/O4TS/"
            return lambda messageObj, _: self.literal_pm(command, messageObj, msg)
        elif command == "baddragon":
            msg = "https://bad-dragon.com/products/" + random.sample(self.phrasebank["dragons"])[0]
            return lambda messageObj, _: self.literal(command, messageObj, msg)
        elif command == "pal":
            return lambda messageObj, _: self.at_sender(command, messageObj, None)
        elif command == "eightball":
            msg = ":8ball: %s" % random.sample(self.phrasebank["8balls"])[0]
            return lambda messageObj, _: self.literal(command, messageObj, msg)
        elif command == "sonic":
            msg = "http://%s.wikia.com/wiki/Special:Random" % ("archiesonic" if random.randint(0, 1) else "sonicfanon")
            return lambda messageObj, _: self.literal(command, messageObj, msg)
        elif command == "plot":
            msg = random.sample(self.phrasebank["plots"])
            return lambda messageObj, _: self.literal(command, messageObj, msg) if self.client.id in messageObj.mentions else None

    #TODO: called using commandname and remainder, in caller: if not target, target = author
    #praises, larts, buydinner(target is always author) => praises
    def at_sender(self, command, messageObj, remainder):
        args = remainder.split()
        channel = messageObj.channel
        if command in ["praise", "lart"]:
            phrasetype = command + "s"
            mention = args[0] #TODO: reverse lookup
        elif command in ["buydinner"]:
            phrasetype = "praises"
            mention = messageObj.author.id
        elif command == "pal":
            mention = messageObj.author.id

        if command == "pal":
            msg = "Go fuck yourself $who" if random.randrange(100) else "Yes this is pal, yes this is 60 FPS"
        else:
            msg = random.sample(self.phrasebank[phrasetype])[0]

        msg.replace("$who", "<@%s>" % mention)
        print("%s: %s" % (command, msg))
        asyncio.ensure_future(self.client.send_message(channel, msg))

    def literal(self, command, messageObj, msg):
        print("%s: %s" % (command, msg))
        asyncio.ensure_future(self.client.send_message(messageObj.channel, msg))

    def literal_pm(self, command, messageObj, msg):
        print("%s: %s" % command)
        asyncio.ensure_future(self.client.send_message(messageObj.author, msg))

    def addphrase(self, remainder, messageObj):
        if len(remainder.split()) < 2:
            raise Exception  #TODO

        partitiond = remainder.lstrip().partition(" ")[0]
        phrasebanktarget = partitiond[0]
        phrase = partitiond[2]

        print("trying to add phrase: \"" + phrase + "\" to bank " + phrasebanktarget)
        
        if phrasebanktarget in self.phrasebank:
            self.phrasebank[phrasebanktarget].append(phrase)
        else:
            self.phrasebank[phrasebanktarget] = list()  #TODO: defaultdict with list() instead of this?
            self.phrasebank[phrasebanktarget].append(phrase)
        with open('phrasebank.json', 'w') as phrasefile:
            phrasefile.write(json.dumps(self.phrasebank, indent=4))
            self.client.send_message(messageObj.channel, "Added phrase " + phrase)

    commandDict = { "!lart": "lart",
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
                    "┻━┻": "unflip",
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
