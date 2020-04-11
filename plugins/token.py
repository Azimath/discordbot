# TOP SECRET DO NOT LOOK

import commands
import base64
import utilities

client = None

keys = {"01":0xBADC0DE600DC0DE}

def encode(n, ver = "01"):
    m = ~n^keys[ver]
    mb = bytes(ver + str(m), "utf-8")
    m64 = base64.b85encode(mb)
    return str(m64, "utf-8")
    
def decode(mbs):
    m64 = bytes(mbs, "utf-8")
    mb = base64.b85decode(m64)
    t = str(mb, "utf-8")
    ver = t[0:2]
    m = int(t[2:])
    n = ~(m^(keys[ver]))
    return n

@commands.registerEventHandler(name="token")
async def getToken(triggerMessage):
    token = encode(triggerMessage.author.id, "01")
    await triggerMessage.author.send( "Your Cryptographically Secure LocusToken is: " + token)
    
@commands.registerEventHandler(name="alltokens")
async def getAllTokens(triggerMessage):
    if triggerMessage.author.id != 102979541458235392: # "Robust permission system"
        await triggerMessage.channel.send("[object Object]") # that'll throw off the hackers
    else:
        s = ""
        for mem in triggerMessage.guild.members:
            s += str(mem) + "," + encode(mem.id) + ";"
        await utilities.big_send(triggerMessage.author, "```" + s + "```")
        
