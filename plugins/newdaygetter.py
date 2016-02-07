import threading
import time
import random
import discord

getGet = False
def TimeCheck(client):
    global getGet
    while True:
        currTime = time.gmtime(time.time())
        if currTime[3] == 5 and currTime[4] == 0 and getGet == False:
            getGet = True
            getWait = random.randrange(60, 300)
            print("Attempting to get get in " + str(getWait) + " seconds")
            startTime = time.time()
            while getGet == True:
                time.sleep(1)
                if time.time() > startTime + getWait:
                    client.send_message(discord.Object(102981131074297856), "New Day Get")
                    getGet = False
            time.sleep(60)
        time.sleep(10)

class GetGetter:            
    def __init__(self, client):
        self.client = client
        self.timeCheckerThread = threading.Thread(target=TimeCheck, kwargs={"client" : client})
        self.timeCheckerThread.daemon = True
        self.timeCheckerThread.start()


    def getStolen(self, message):
        if message.server is not None:
            if message.server.id == "102981131074297856" and message.channel.id == "102981131074297856" and getGet:
                global getGet
                getGet = False
                print("get stolen")
    commandDict = {"\\" : "getStolen"}
Class = GetGetter
