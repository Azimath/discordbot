import commands
import permissions
import discord
import requests
import random
import time

BOORUCD = 10 #this is to avoid spamming discord, and the APIs
SUPPORTED = ["e621", "gelbooru"]
client = None

def gelbooru(tags):
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

@commands.registerEventHander(name="booru")
async def booru(triggerMessage):
    await client.send_typing(triggerMessage.channel)
    global BOORUCD # currently nothing else uses this, but maybe something will
    #TODO: Actually implement cooldown
    global SUPPORTED
    tokens = triggerMessage.contents.split()
    if (len(tokens) == 1 or tokens[1].tolower() == "help"):
        await client.send_message(triggerMessage.channel, "Syntax is `!booru booru_name tag0...`\n Currently supported boorus: " + str(SUPPORTED))
        return
    functionMap = {"e621":e621, "gelbooru":gelbooru}
    try:
        out = functionMap[tokens[1]](tokens[2:])
    except Exception as e:
        await client.send_message(triggerMessage.channel, "Oopsie woopsie Uwu. One of many possible disasters has occured. Try `!booru help`")
        print(e) #hopefully this does something useful
        return
    
    #out should be the file name of the file we want to send assuming nothing went terribly wrong
    
    with open(out, "rb") as image:
        await client.send_file(triggerMessage.channel, image, filename=out)
        
    return
