import re
import discord
import permissions

class Sudo:
    """A plugin to make the bot say things in channels. Mods only.
    !sudo channel1:channel2:etc stuff : says stuff in channel"""
    def __init__(self, client):
        self.client = client

    @permissions.needs_permission(permissions.Permissions.moderator)
    def sudo(self, remainder, messageObj):
        if len(remainder.split()) < 2:
            self.client.send_message(messageObj.channel, "Not enough args")
            return

        partitiond = remainder.lstrip().partition(" ")
        channelids = [re.match("<#([0-9]+)>", s).group(1) for s in partitiond[0].split(":")]
        #is there even a point to multichannel?
        channels = [discord.Object(i) for i in channelids]
        message = partitiond[2]

        for target in channels:
            self.client.send_message(target, message)

        self.client.send_message(messageObj.channel, "message%s sent" % ("s" if len(channels) - 1 else ""))

    commandDict = {"!sudo": "sudo"}
Class = Sudo
