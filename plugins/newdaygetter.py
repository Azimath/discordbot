import threading
import time
import random
import discord
import asyncio

getGet = False
async def TimeCheck(client):
    global getGet
    while not client.is_closed:
        currTime = time.gmtime(time.time())
        if currTime[3] == 5 and currTime[4] == 0 and getGet == False:
            getGet = True
            getWait = random.randrange(60, 300)
            print("Attempting to get get in " + str(getWait) + " seconds")
            startTime = time.time()
            while getGet == True:
                asyncio.sleep(1)
                if time.time() > startTime + getWait:
                    await client.send_message(discord.Object(102981131074297856), "New Day Get")
                    getGet = False
            asyncio.sleep(60)
        asyncio.sleep(10)

class GetGetter:            
    def __init__(self, client):
        self.client = client
        self.client.loop.create_task(TimeCheck(self.client))

    def getStolen(self, message):
        if message.server is not None:
            if message.server.id == "102981131074297856" and message.channel.id == "102981131074297856" and getGet:
                global getGet
                getGet = False
                print("get stolen")
    commandDict = {"\\message" : "getStolen"}
Class = GetGetter
