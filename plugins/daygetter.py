import discord
import asyncio
import permissions
import commands
from datetime import datetime, date, time
import tzlocal
import random


client = None
nextDelay = random.randrange(10, 60)
tz=tzlocal.get_localzone()

@commands.registerEventHandler(triggerType="\\timeTick", name="dayget")
async def checkDay():
    if time(minute = 1, second = 10) < datetime.now().time():
        return
    
    if datetime.now().time() < time(second = nextDelay):
        return
        
    midnight = datetime.combine(date.today(), time.min.replace(tzinfo=tz)) #Get an offset aware datetime representing the previous midnight
    
    channel = discord.Object("102981131074297856") #IAA genearl
    
    async for m in client.logs_from(channel, limit=2):
        if tz.localize(m.timestamp) > midnight:
            return
    
    await channel.send( "New Day Get")
    #if discord.utils.find(lambda m: m.timestamp > midnight, list(client.logs_from(channel, limit=2))) is None:
        #await channel.send( "New Day Get")