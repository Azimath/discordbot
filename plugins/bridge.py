#TODO: >seen, >getlastmention
#TODO: solve the channel joined/not joined but want to set topic somehow, peoperly. i.e. not with .sleep
#TODO: auth + OP
#TODO: something about usernames that will break the current from-irc highlighting method
#TODO:joined/left irc message? (there is no way to tell if someone has left otherwise, and they will not get messages
#TODO: !later ?
import pydle
import discord
import discord.utils as util
import threading
import time
import re

#see recvDiscordMsg for the format of msgInternal
class IRCBridge:
	commandDict = {"\\message":"recvDiscordMsg","\\on_channel_update":"updateIrcTopic"}

	def __init__(self, client):
		self.client = client

		self.server = util.find(lambda s: s.name == "IAA-Official", self.client.servers)

		self.ircThread = IrcThread(self)#pass IRCBridge instance so we can access the recvIrcMsg callback
		self.ircThread.start()

		while not self.ircThread.isRunning:
			time.sleep(0.1)
		self.joinChannelsOnIrc(
			["#IAA-" + c.name for c in client.get_all_channels()
				if c.type == "text" and c.server.id == "102981131074297856"])#iaa server

	def joinChannelsOnIrc(self, channelList):
		#this looping is for working around the race condition where a channel is not joined yet but we try to set the topic
		outerList = list(channelList)#copy channelList
		while outerList:
			innerList = outerList
			for c in innerList:
				self.ircThread.client.eventloop.schedule(self.ircThread.client.join, c)
				time.sleep(0.5)
				if self.ircThread.client.in_channel(c):
					outerList.remove(c)
		for c in channelList:
			self.updateIrcTopic(util.find(lambda a: a.name == c.replace("#IAA-","",1), self.server.channels))

	def updateIrcTopic(self, channel):
		print("update: %s" % channel)
		if channel.topic:
			self.ircThread.client.eventloop.schedule(
				self.ircThread.client.set_topic,
				"#IAA-"+channel.name,
				channel.topic.replace("\n",""))

#Discord -> IRC
	def recvDiscordMsg(self, message):
		if isinstance(message.channel, discord.PrivateChannel):
			return#TODO

		msgInternal = {
			"nick":message.author.name,
			"channel":"#IAA-"+message.channel.name,
			"message":message.content
			#message.embeds?
			}

		if message.channel.type == "text" and message.channel.server.id == "102981131074297856" and msgInternal["channel"] not in self.ircThread.client.channels.keys():
			print("Attempting to join IRC channel:", msgInternal["channel"])
			self.joinChannelsOnIrc([msgInternal["channel"]])
			
		if message.attachments:
			for a in message.attachments:
				msgTemp = msgInternal
				msgTemp["message"] = "Attachment: %s (%s) at %s" % (a["filename"],a["size"],a["url"]) 
				self.sendIrcMsg(msgTemp)
		else:
			self.sendIrcMsg(msgInternal)

	def sendIrcMsg(self, msgInternal):
		msgStr = "%s:\t%s" % (self.colorize(msgInternal["nick"]), self.decodeMsg(msgInternal["message"]))
		self.ircThread.client.eventloop.schedule(self.ircThread.client.message, msgInternal["channel"], msgStr)

	def colorize(self, nick): #this uses the hexchat algorithm, colors: http://www.mirc.com/colors.html
		colors = [1,2,3,6,7,10,12]
		index = sum([ord(x) for x in nick]) % len(colors)
		return "\x03"+str(colors[index])+nick+"\x031"

#IRC -> Discord
	def recvIrcMsg(self, msgInternal):
		self.sendDiscordMsg(msgInternal)

	def recvIrcAction(self, actionInternal):
		actionInternal["message"] = actionInternal["action"]
		del actionInternal["action"]
		self.sendDiscordMsg(actionInternal, separator="")

	def sendDiscordMsg(self, msgInternal, separator=":"):
		msgStr = "%s%s %s" % (msgInternal["nick"], separator, self.encodeMsg(msgInternal["message"]))
		channelId = [c.id for c in self.client.get_all_channels()
			if c.name == msgInternal["channel"]][0]
		if not channelId:
			print("Message '%s' ignored, no such channel: %s" %
				(msgInternal["message"], msgInternal["channel"]))
			return
		self.client.send_message(discord.Object(channelId), msgStr)

	def encodeMsg(self, message):
		unames = {x.name:str(x.id) for x in self.server.members}
		channels = {x.name:str(x.id) for x in self.server.channels}
		temp = message
		for uname,uid in unames.items():
			temp = temp.replace(uname, "<@"+uid+">")
		for cname,cid in channels.items():
			temp = temp.replace("#"+cname, "<#"+cid+">")
		return temp

	def decodeMsg(self, message):
		unames = {x.name:str(x.id) for x in self.server.members}
		channels = {x.name:str(x.id) for x in self.server.channels}
		temp = message
		for uname,uid in unames.items():
			temp = temp.replace("<@"+uid+">", uname)
		for cname,cid in channels.items():
			temp = temp.replace("<#"+cid+">", "#"+cname)
		return temp

	def getOnlineList(self):
		return [x.name for x in self.server.members if x.status == "online"]

Class = IRCBridge

class IrcClient(pydle.MinimalClient):
	def __init__(self):
		super().__init__("o")

	@pydle.coroutine#may or may not be necessary
	def on_message(self, target, source, message):
		super().on_message(target, source, message)

		if message == ">list":
			self.message(target, ",".join(self.callbackdict["getOnlineList"]()) )
			return
		
		msgInternal = {
			"nick":source,
			"channel":target.replace("#IAA-","",1),
			"message":message
			#message.embeds?
			}
		self.callbackdict["onMessage"](msgInternal)
	
	def on_ctcp_action(self, by, target, contents):
		actionInternal = {
			"nick":by,
			"channel":target.replace("#IAA-","",1),
			"action":contents
			}
		self.callbackdict["onCtcpAction"](actionInternal)


#IMPORTANT: .eventloop only gets set when .connect is run, hence the synchronisation by .isRunning
class IrcThread(threading.Thread):
	def __init__(self, ircBridgeInstance):
		self.isRunning = False
		super().__init__()
		self.daemon = True #does this work like this?
		self.client = IrcClient()
		self.client.callbackdict = {
			"onMessage":ircBridgeInstance.recvIrcMsg,
			"onCtcpAction":ircBridgeInstance.recvIrcAction,
			"getOnlineList":ircBridgeInstance.getOnlineList
			}

	def run(self):
		self.client.connect("127.0.0.1", 6667)
		self.isRunning = True
		self.client.handle_forever()
