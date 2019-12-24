import json
import random
import asyncio
import commands

client = None

with open("plugins/dunnos.json","r") as dunnofile:
    config = json.load(dunnofile)
            
@commands.registerEventHandler(triggerType="\\commandNotFound", name="dunno") 
async def dunno(triggerMessage):
    if triggerMessage.channel.id in config["channels"]:
    	await triggerMessage.channel.send( random.sample(config["dunnos"], 1)[0])
    	
@commands.registerEventHandler(triggerType="\\command", name="dunnos.enable") 
async def enable(triggerMessage):
	if triggerMessage.channel.id in config["channels"]:
		await triggerMessage.channel.send( "Dunnos already enabled here")
	else:
		config["channels"].append(triggerMessage.channel.id)
		with open("plugins/dunnos.json", "w") as dunnofile:
			json.dump(config, dunnofile, indent=4)
		await triggerMessage.channel.send( "Dunnos enabled for this channel")
		
@commands.registerEventHandler(triggerType="\\command", name="dunnos.disable") 
async def disable(triggerMessage):
	if triggerMessage.channel.id not in config["channels"]:
		await triggerMessage.channel.send( "Dunnos already disabled here")
	else:
		config["channels"] = list(filter(lambda a: a != triggerMessage.channel.id, config["channels"]))
		with open("plugins/dunnos.json", "w") as dunnofile:
			json.dump(config, dunnofile, indent=4)
		await triggerMessage.channel.send( "Dunnos disabled for this channel")