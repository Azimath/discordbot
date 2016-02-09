#TODO: >seen, >getlastmention
#TODO: auth + OP
#TODO: something about usernames that will break the current from-irc highlighting method
#TODO:joined/left irc message? (there is no way to tell if someone has left otherwise, and they will not get messages
#TODO: !later ?
import pydle
import discord
import discord.utils as util
import threading
import json
import asyncio
import time
from enum import Enum


#####
def colorize_nick(nick):  #this uses the hexchat algorithm, colors: http://www.mirc.com/colors.html
    colors = [1, 2, 3, 6, 7, 10, 12]
    index = sum([ord(x) for x in nick]) % len(colors)
    return "\x03%s%s\x031" % (str(colors[index]), nick)


class TransType(Enum):
    irc = 1
    canonical = 2
    discord = 3


#TODO: test this
#though one of the translations requires a channel iterable instance,
#this is a separate function so that the irc client can also use it
def translateChannel(channel, target, channelIterable=None):
    if target is TransType.canonical:
        if isinstance(channel, str):  # IRC(|canonical) -> canonical
            return channel.replace("#%s" % config["IRCPrefix"], "", 1)
        elif isinstance(channel, discord.Channel):  # discordobj -> canonical
            return channel.name
    elif target is TransType.discord:  # (str -> canonical) -> discordobj
        return util.get(channelIterable, name=translateChannel(channel, TransType.canonical))
    elif target is TransType.irc:
        if isinstance(channel, discord.Channel):  # discordobj -> IRC
            return "#%s%s" % (config["IRCPrefix"], channel.name)
        elif isinstance(channel, str):  # canonical(|IRC) -> IRC
            return "#%s%s" % (config["IRCPrefix"], translateChannel(channel, TransType.canonical))
#####
#####


with open('plugins/bridge.json', 'r') as configfile:
    config = json.load(configfile)


#see recvDiscordMsg for the format of msgInternal
class IRCBridge:
    commandDict = {"\\message_with_bot":"recvDiscordMsg", "\\on_channel_update":"updateIrcTopic"}

    def __init__(self, client):
        self.client = client

        self.server = util.get(self.client.servers, id=config["DiscordServerID"])

        self.ircThread = IrcThread(self)  #pass IRCBridge instance so we can access the necessary callbacks
        self.ircThread.start()

    def updateIrcTopic(self, discordChannel):
        self.ircThread.client.eventloop.schedule(self.ircThread.client.updateIrcTopic, discordChannel)

#Discord -> IRC
    def recvDiscordMsg(self, message):
        if isinstance(message.channel, discord.PrivateChannel):
            return  #TODO

        if not message.server.id == config["DiscordServerID"]:
            return  #TODO maybe filter at a higher level? multi server?

        def attMsg(attachments):
            return "".join([
                "Attachment: %s (%s) at %s ||" % (a["filename"], a["size"], a["url"])
                for a in attachments]) #TODO: why is this a list? what is multi?

        msgInternal = {
            "nick": message.author.name,
            "channel": translateChannel(message.channel, TransType.canonical),
            "message": message.content if not message.attachments else attMsg(message.attachments)
            }

        self.sendIrcMsg(msgInternal)

    def sendIrcMsg(self, msgInternal):  #TODO: fails if eventloop doesnt exist yet
        channel = translateChannel(msgInternal["channel"], TransType.irc)

        if channel not in self.ircThread.client.channels:
            print("Message received => unjoined IRC channel; attempting to join:", channel)
            self.ircThread.client.eventloop.schedule(self.ircThread.client.join, channel)
            while channel not in self.ircThread.client.channels:
                time.sleep(0.5)

        msgStr = "%s:\t%s" % (colorize_nick(msgInternal["nick"]),
                              self.translateMsg(msgInternal["message"], TransType.irc))
        self.ircThread.client.eventloop.schedule(self.ircThread.client.message, channel, msgStr)

#IRC -> Discord
    def recvIrcMsg(self, msgInternal):
        self.sendDiscordMsg(msgInternal)

    def recvIrcAction(self, actionInternal):
        actionInternal["message"] = actionInternal["action"]
        del actionInternal["action"]
        self.sendDiscordMsg(actionInternal, separator="")

    def sendDiscordMsg(self, msgInternal, separator=":"):
        msgStr = "%s%s %s" % (msgInternal["nick"], separator,
                              self.translateMsg(msgInternal["message"], TransType.discord))
        channel = translateChannel(msgInternal["channel"], TransType.discord, self.server.channels)
        if not channel:
            print("Message '%s' ignored, no such channel: %s , trans: %s" %
                  (msgInternal["message"], msgInternal["channel"], channel))
            return
        asyncio.ensure_future(self.client.send_message(channel, msgStr), loop=self.client.loop)

    def getOnlineList(self):
        return [x.name for x in self.server.members if x.status == discord.Status.online]

    def translateMsg(self, message, target):
        unames = {x.name:str(x.id) for x in self.server.members}
        channels = {x.name:str(x.id) for x in self.server.channels}
        temp = message
        for uname, uid in unames.items():
            nametranslator = ["<@%s>" % uid, uname]
            temp = temp.replace(*(nametranslator if target is TransType.irc else reversed(nametranslator)))
        for cname, cid in channels.items():
            chantranslator = ["<#%s>" % cid, "#%s" % cname]
            temp = temp.replace(*(chantranslator if target is TransType.irc else reversed(chantranslator)))
        return temp

Class = IRCBridge


class IrcClient(pydle.MinimalClient):
    def __init__(self, callbackdict):
        super().__init__(config["BotNick"])
        self.callbackdict = callbackdict

    #@pydle.coroutine  #may or may not be necessary
    def on_message(self, target, source, message):
        super().on_message(target, source, message)
        print([target, source, message])
        if message == ">list":
            self.message(target, ", ".join(self.callbackdict["getOnlineList"]()))
            self.message(target, ", ".join([translateChannel(c, TransType.irc) for c in self.callbackdict["getChannelList"]()
                                            if c.type == discord.ChannelType.text and c.server.id == config["DiscordServerID"]]))
            return

        msgInternal = {
            "nick": source,
            "channel": translateChannel(target, TransType.canonical),
            "message": message
            }
        self.callbackdict["onMessage"](msgInternal)

    def on_connect(self):
        super().on_connect()
        channels = [translateChannel(c, TransType.irc) for c in self.callbackdict["getChannelList"]()
                    if c.type == discord.ChannelType.text and c.server.id == config["DiscordServerID"]]  #TODO
        for c in channels:
            self.join(c)

    def on_join(self, channel, user):
        super().on_join(channel, user)
        if user == self.nickname:
            self.updateIrcTopic(translateChannel(channel, TransType.discord, self.callbackdict["getChannelList"]()))

    def on_ctcp_action(self, by, target, contents):
        super().on_ctcp_action(by, target, contents)

        actionInternal = {
            "nick": by,
            "channel": translateChannel(target, TransType.canonical),
            "action": contents
            }
        self.callbackdict["onCtcpAction"](actionInternal)

    def updateIrcTopic(self, discordChannel):
        print("update: %s" % discordChannel)
        if discordChannel.topic:
            self.set_topic(translateChannel(discordChannel, TransType.irc),
                           discordChannel.topic.replace("\n", ""))  #character is invalid in IRC protocol (?) TODO


#IMPORTANT: .eventloop only gets set when .connect is run, hence the synchronisation by .isRunning
class IrcThread(threading.Thread):
    def __init__(self, ircBridgeInstance):
        self.isRunning = False
        super().__init__(daemon=True)
        callbackdict = {
            "onMessage": ircBridgeInstance.recvIrcMsg,
            "onCtcpAction": ircBridgeInstance.recvIrcAction,
            "getOnlineList": ircBridgeInstance.getOnlineList,
            "getChannelList": ircBridgeInstance.client.get_all_channels
            }
        self.client = IrcClient(callbackdict)

    def run(self):
        self.client.connect(config["ServerIP"], config["ServerPort"])
        self.client.handle_forever()