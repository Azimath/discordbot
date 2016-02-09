import re
import discord
import asyncio

class Sudo:
    """A plugin to make the bot say things in channels. Mods only.
    !sudo channel1:channel2:etc stuff : says stuff in channel"""
    def __init__(self, client):
        self.client = client

    @permissions.needs_role(permissions.RoleEnum.moderator)
    def sudo(self, remainder, messageObj):
        if len(remainder.split()) < 2:
            asyncio.ensure_future(self.client.send_message(messageObj.channel, "Not enough args"))
            return

        partitiond = remainder.lstrip().partition(" ")
        channelids = [re.match("<#([0-9]+)>", s).group(1) for s in partitiond[0].split(":")]
        #is there even a point to multichannel?
        channels = [discord.Object(i) for i in channelids]
        message = partitiond[2]

        for target in channels:
            asyncio.ensure_future(self.client.send_message(target, message))

        asyncio.ensure_future(self.client.send_message(messageObj.channel, "message%s sent" % ("s" if len(channels) - 1 else "")))

    commandDict = {"!sudo": "sudo"}
Class = Sudo
