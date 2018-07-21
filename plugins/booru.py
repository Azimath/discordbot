import commands
import permissions
import discord
import requests
import random
import time
from json import JSONDecodeError

BOORUCD = 10 #this is to avoid spamming discord, and the APIs
SUPPORTED = ["e621", "gelbooru"]
headers = {"user-agent":"[^_^]/1.0"}
client = None
busy = False

def gelbooru(tags):
    global headers
    t = tags.pop(0)
    for x in tags:
        t+="+"+x
    session = requests.Session()
    session.headers.update(headers)
    
    response = session.get("http://gelbooru.com/index.php?page=dapi&limit=10&s=post&&q=index&json=1&tags=" + t)
    
    j = response.json()
    
    target = j[random.randint(0, len(j))]['file_url']
    file_response = session.get(target)
    file_extension = target[target.rfind(".")+1:]
    print(file_extension)
    
    #https://stackoverflow.com/a/39217788
    data = file_response.content
    print(len(data))
    with open("out."+file_extension, 'wb') as f:
        f.write(data)
        f.close()
        
    return "out."+file_extension

#tags should be a list of desired tags
def e621(tags):
    global headers
    t = tags.pop(0)
    for x in tags:
        t+="+"+x
    session = requests.Session()
    session.headers.update(headers)
    
    response = session.get("http://e621.net/post/index.json?limit=10&tags=" + t)
    
    j = response.json()
    
    target = j[random.randint(0, len(j))]['file_url']
    file_response = session.get(target)
    file_extension = target[target.rfind(".")+1:]
    print(file_extension)
    
    #https://stackoverflow.com/a/39217788
    data = file_response.content
    print(len(data))
    with open("out."+file_extension, 'wb') as f:
        f.write(data)
        f.close()
        
    return "out."+file_extension

@commands.registerEventHandler(name="booru", exclusivity="global")
async def booru(triggerMessage):
    await client.send_typing(triggerMessage.channel)
    global BOORUCD # currently nothing else uses this, but maybe something will
    #TODO: Actually implement cooldown
    global SUPPORTED
    tokens = triggerMessage.content.split()
    #if (len(tokens) == 1 or tokens[1].lower() == "help"):
    if (len(tokens) <= 2):
        await client.send_message(triggerMessage.channel, "Syntax is `!booru booru_name tag0 ...`\nCurrently supported boorus: " + str(SUPPORTED))
        return
    functionMap = {"e621":e621, "gelbooru":gelbooru}
    try:
        out = functionMap[tokens[1]](tokens[2:])
        #out should be the file name of the file we want to send assuming nothing went terribly wrong
    
        with open(out, "rb") as image:
            await client.send_file(triggerMessage.channel, image, filename=out)
    except IndexError:
        await client.send_message(triggerMessage.channel, "Oopsie woopsie Uwu. " + tokens[1] + " returned no search results.")
    except KeyError:
        await client.send_message(triggerMessage.channel, "Oopsie woopsie. " + tokens[1] + " is not supported.\nSupported boorus: "+str(SUPPORTED))
    except JSONDecodeError:
        await client.send_message(triggerMessage.channel, "Oopsie Woopsie. Failed to decode json. " + tokens[1] + " returned an empty response, or something weird")
    except Exception as e:
        await client.send_message(triggerMessage.channel, "Oopsie woopsie Uwu. One of many possible disasters has occured. Try `!booru help`\nException: " + type(e).__name__)
        print(e) #hopefully this does something useful
        
    return    
    
@commands.registerEventHandler(name="unbusy")
async def unbusy(triggerMessage):
    global busy
    busy = False

class BooruGame:
    def __init__(self, tagValues):
        self.userScores = {}
        self.tagValues = tagValues
        self.previousGuesses = []
    
    def wasguessed(self, guess):
        return guess in self.previousGuesses
        
    def guess(self, guess, user):
        if user not in self.userScores:
            self.userScores[user] = 0
            
        if guess in self.previousGuesses:
            return guess + " was already guessed."
        
        if guess in self.tagValues:
            value = self.tagValues[guess]
            self.userScores[user] += value
            self.previousGuesses.append(guess)
            del self.tagValues[guess]
            return guess + ": Correct! " + str(value) + " points"
        else:    
            return guess + ": Nope!"
            

gameInstances = {}

def lookup_tag(tag):
    global headers
    session = requests.Session()
    session.headers.update(headers)
    response = session.get("http://e621.net/tag/index.json?name=" + tag)
    j = response.json()
    if (len(j) == 0):
        return 0
    else:
        return j[0]["count"]

@commands.registerEventHandler(name="bgs")
@commands.registerEventHandler(name="boorugamestart")
async def startBooruGame(triggerMessage):
    if triggerMessage.channel in gameInstances:
        await client.send_message(triggerMessage.channel, "A game is already in progress in this channel")
    else:
        tagValues = {}
        tags = []
        try:    
            global headers
            session = requests.Session()
            session.headers.update(headers)
            response = session.get("http://e621.net/post/index.json?limit=10&tags=order:random")
            j = response.json()
            
            target = -1
            for i in range(0, len(j)): # look for a suitable post
                file_ext = j[i]["file_ext"]
                if (file_ext != 'png' and file_ext != 'jpg'):
                    continue
                if (len(j[i]["tags"]) <= 5):
                    continue
                target = i
                break
            if (target == -1):
                #print("Error: Failed to find suitable post. Try again?")
                await client.send_message(triggerMessage.channel, "Oopsie woopsie Uwu. Couldn't find a suitable post. Try again?")
                return
            tags = j[target]["tags"].split(" ")
            target = j[target]["file_url"]
            
            file_response = session.get(target)
            file_extension = target[target.rfind(".")+1:]
            print(file_extension)
            
            #https://stackoverflow.com/a/39217788
            data = file_response.content
            print(len(data))
            with open("out."+file_extension, 'wb') as f:
                f.write(data)
                f.close()
            
            with open("out."+file_extension, "rb") as image:
                await client.send_file(triggerMessage.channel, image, filename="out."+file_extension)
                
        except JSONDecodeError:
            await client.send_message(triggerMessage.channel, "Oopsie Woopsie. Failed to decode json.")
            return
        except Exception as e:
            await client.send_message(triggerMessage.channel, "Oopsie woopsie Uwu. One of many possible disasters has occured. Try `!booru help`\nException: " + type(e).__name__)
            print(e) #hopefully this does something useful
            return
        
        print(tags)
        for tag in tags:
            tagValues[tag] = 1
        
        gameInstances[triggerMessage.channel] = BooruGame(tagValues)
        await client.send_message(triggerMessage.channel, "Game started. The post has " + str(len(tags)) + " tags to guess.")


async def stopBooruGame(triggerMessage):
    if triggerMessage.channel in gameInstances:
        await client.send_message(triggerMessage.channel, "Unguessed tags were: " + str(list([triggerMessage.channel].tagValues.keys())))
        del gameInstances[triggerMessage.channel]
        await client.send_message(triggerMessage.channel, "Game stopped")
    else:
        await client.send_message(triggerMessage.channel, "No game in progress here")

@commands.registerEventHandler(name="boorugamestop")
@commands.registerEventHandler(name="boorugamequit")
@commands.registerEventHandler(name="bgq")
async def endBooruGame(triggerMessage):
    await client.send_message(triggerMessage.channel, "Game Complete!")
    await client.send_message(triggerMessage.channel, "Unguessed tags were: `" + str(list(gameInstances[triggerMessage.channel].tagValues.keys()))+"`")
    await client.send_message(triggerMessage.channel, "Guessed tags were: `" + str(gameInstances[triggerMessage.channel].tags) + "`")
    scoreDict = gameInstances[triggerMessage.channel].userScores
    scores = [(k, scoreDict[k]) for k in sorted(scoreDict, key=scoreDict.get, reverse=True)]
    scoreString = ""
    for id, score in scores:
        member = discord.utils.find(lambda m: m.id == id, triggerMessage.server.members)
        name = member.name
        if member.nick is not None:
            name = member.nick
        scoreString += "User " + str(name) + " scored " + str(score) + "\n"
    
    member = discord.utils.find(lambda m: m.id == scores[0][0], triggerMessage.server.members)
    name = member.name
    if member.nick is not None:
        name = member.nick
    await client.send_message(triggerMessage.channel, scoreString)
    await client.send_message(triggerMessage.channel, str(name) + " wins!")
    
    del gameInstances[triggerMessage.channel]

@commands.registerEventHandler(name="bg")
@commands.registerEventHandler(name="booruguess")
async def booruGameGuess(triggerMessage):
    args = triggerMessage.content.split()
    for arg in args[1:]:
        await client.send_message(triggerMessage.channel, gameInstances[triggerMessage.channel].guess(str(arg), triggerMessage.author.id))
        
    if len(gameInstances[triggerMessage.channel].tagValues) == 0:
        await endBooruGame(triggerMessage)
