import random
import json


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
        with open('phrasebank.json', 'r') as lartfile:
            self.phrasebank = json.loads(lartfile.read())
            
    def lart(self, message):
        lart = self.phrasebank["larts"][random.randrange(self.phrasebank["larts"].__len__())]
        target = message.content[6:]
        if not target:
            target = message.author.name
        lart = lart.replace("$who", target)
        print("Lart: " + lart)
        self.client.send_message(message.channel, lart)
     
    def praise(self, message):
        praise = self.phrasebank["praises"][random.randrange(self.phrasebank["praises"].__len__())]
        target = message.content[8:]
        if not target:
            target = message.author.name
        praise = praise.replace("$who", target)
        print("praise: " + praise)
        self.client.send_message(message.channel, praise)
    
    def buydinner(self, message):
        praise = self.phrasebank["praises"][random.randrange(self.phrasebank["praises"].__len__())]
        target = message.author.name
        praise = praise.replace("$who", target)
        print("praise: " + praise)
        self.client.send_message(message.channel, praise)
        
    def baddragon(self, message):
        dragon = "https://bad-dragon.com/products/" + self.phrasebank["dragons"][random.randrange(self.phrasebank["dragons"].__len__())]
        print("dragon: " + dragon)
        self.client.send_message(message.channel, dragon)
        
    def pal(self, message):
        if random.randrange(100) == 0:
            self.client.send_message(message.channel, "Go fuck yourself " + message.author.name)
        else:
            self.client.send_message(message.channel, "Yes this is pal, yes this is 60 FPS")

    def mango(self, message):
        self.client.send_message(message.channel, "mang0 is in jail for multishining a kangaroo BibleThump")

    def eightball(self, message):
        ball = self.phrasebank["8balls"][random.randrange(self.phrasebank["8balls"].__len__())]
        print("8ball: " + ball)
        self.client.send_message(message.channel, ":8ball: " + ball)
        
    def tests(self, message):
        target = message.author
        self.client.send_message(target, "Take each of the following tests. Save a screenshot of each result.\nMBTI: http://www.humanmetrics.com/cgi-win/jtypes2.asp\nEnneagram: http://www.eclecticenergies.com/enneagram/test.php Take both tests for best results.\nBIG5: http://personality-testing.info/tests/BIG5.php\nTemperaments: http://personality-testing.info/tests/O4TS/")
        # self.client.send_message(target, "MBTI: http://www.humanmetrics.com/cgi-win/jtypes2.asp")
        # self.client.send_message(target, "Enneagram: http://www.eclecticenergies.com/enneagram/test.php")
        # self.client.send_message(target, "Take both tests for best results.")
        # self.client.send_message(target, "BIG5: http://personality-testing.info/tests/BIG5.php")
        # self.client.send_message(target, "Temperaments: http://personality-testing.info/tests/O4TS/")    
    
    def popori(self, message):
        self.client.send_message(message.channel, "https://www.youtube.com/watch?v=gbNN3grTdDk")
    
    def constitution(self, message):
        self.client.send_message(message.channel, "https://docs.google.com/document/d/1XKFRQhzxwhjjtW1RnCc_ZhesRqavvM3F5z1LALfve48/")
        
    def wiki(self, message):
        self.client.send_message(message.channel, "http://iaa.wikia.com")
     
    def application(self, message):
        self.client.send_message(message.channel, "https://docs.google.com/forms/d/1bURXLKIo30XLX3RASg2B8XVLsYpp6GYXn84IT2F9hbM/viewform")
        
    def unflip(self, message):
        self.client.send_message(message.channel, "┬─┬﻿ ノ( ゜-゜ノ)")
        
    def floor(self, message):
        self.client.send_message(message.channel, "http://i.imgur.com/3OYeOxK.jpg")
    
    def sonic(self, message):
        if random.randint(0,1) != 0:
            self.client.send_message(message.channel, "http://archiesonic.wikia.com/wiki/Special:Random")
        else:
            self.client.send_message(message.channel, "http://sonicfanon.wikia.com/wiki/Special:Random")

    def plot(self, message):
        if self.client.user in message.mentions:
            self.client.send_message(message.channel, self.phrasebank["plots"][random.randrange(len(self.phrasebank["plots"]))])

    def addphrase(self, message):
        perms = False
        for role in message.author.roles:
            if role.permissions.can_manage_messages:
                perms = True
                break
        
        banktargetstart = message.content.find(' ') + 1
        banktargetend = message.content.find(' ', banktargetstart)
        phrasebanktarget = message.content[banktargetstart:banktargetend]
        phrase = message.content[banktargetend+1:len(message.content)]
        
        print("splitting message at: " + str(banktargetstart) + " and: " + str(banktargetend))
        print("trying to add phrase: \"" + phrase + "\" to bank " + phrasebanktarget)
        
        if phrasebanktarget is not None and phrasebanktarget in self.phrasebank and phrase is not None and perms:
            self.phrasebank[phrasebanktarget].append(phrase)
            
            with open('phrasebank.json', 'w') as phrasefile:
                phrasefile.write(json.dumps(self.phrasebank, indent=4))
                self.client.send_message(message.channel, "Added phrase " + phrase)
    commandDict = { "!lart":"lart", "!praise":"praise", "!buydinner":"buydinner", "!baddragon":"baddragon",
                    "!pal":"pal", "!mango":"mango", "!mang0":"mango", "!eightball":"eightball", "!8ball":"eightball",
                    "!tests":"tests", "!popori":"popori", "!addphrase":"addphrase", "┻━┻":"unflip", "!floor":"floor",
                    "!wiki":"wiki", "!apply":"application", "!application":"application",
                    "!constitution":"constitution", "!sonic":"sonic", "!sanic":"sonic", "plot":"plot"}
Class = Phrases
