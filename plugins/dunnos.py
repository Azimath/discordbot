import json
import random

class Dunno:
	commandDict = {"\\command_not_found":"dunno"}
	def __init__(self, client):
		self.client = client
		with open("plugins/dunnos.json","r") as dunnofile:
			self.dunnos = json.load(dunnofile)

	def dunno(self, commandName, message):
		self.client.send_message(message.channel, random.sample(self.dunnos, 1)[0])
Class = Dunno

