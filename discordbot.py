import discord
import time
import pkgutil
import sys
import json
import random

####Helper stuff
def loadPlugins():
    global commandObjects
    global plugins

    def load_all_modules_from_dir(dirname): #modded from: http://stackoverflow.com/questions/1057431/loading-all-modules-in-a-folder-in-python/8556471#8556471
        modules = []
        for importer, package_name, _ in pkgutil.iter_modules([dirname]):
            full_package_name = '%s.%s' % (dirname, package_name)
            if full_package_name not in sys.modules:
                mod = importer.find_module(package_name).load_module(full_package_name)
                modules.append(mod)
                print(mod)
        return modules
    
    plugins = load_all_modules_from_dir("plugins")
    commandObjects = [plugin.Class(client) for plugin in plugins]

    callEvents("\\set_root_context_on_load", commandObjects, [locals(), globals()])
    print(str(commandObjects.__len__()) + " plugins loaded")

class COCallablesIterator():#co = commandobjects
    def __init__(self, commandObjects, name):
        self.commandObjects = commandObjects
        self.name = name
    def __iter__(self):
        for commandObject in self.commandObjects:
            for key, funcName in commandObject.commandDict.items():
                if key == self.name:
                    thing = getattr(commandObject, funcName)
                    if callable(getattr(commandObject, funcName)):
                        yield thing

def callEvents(eventName, commandObjects, *args, **kwargs):
    calledCount = 0
    for method in COCallablesIterator(commandObjects, eventName):
        method(*args, **kwargs)
        calledCount += 1
    return calledCount

#TODO: what if?: !command is defined multiple times
def callCommand(commandObjects, commandName, remainder, messageObj, *args, **kwargs):
    for method in COCallablesIterator(commandObjects, commandName):
        if commandObject.legacy:
            getattr(commandObject, funcName)(messageObj)
        else:
            getattr(commandObject, funcName)(messageObj, remainder, *args, **kwargs)
        return True#TODO: continue or not? => if yes, return counter instead of bool
    return False

#####
#####

if __name__ == "__main__":
    with open('config.json', 'r') as configfile:
        config = json.loads(configfile.read())

    client = discord.Client()
    client.login(config["DiscordEmail"], config["DiscordPassword"])

    def listen():
        @client.event
        def on_message(message):
            global commandObjects
            global plugins

            callEvents("\\message_with_bot", commandObjects, message)

            if message.author.id != client.user.id:#we ignore our own messages
                callEvents("\\message", commandObjects, message)#shorthand for message_no_bot: should we even allow implicit?
                callEvents("\\message_no_bot", commandObjects, message)
                    
                #elif message.content.startswith("!reload"):
                    #client.send_message(message.channel, "Reloading plugins")
                    #print("Reload started")
                    #commandObjects = []
                    #plugins = load_all_modules_from_dir("plugins")
                    #for plugin in plugins:
                        #commandObjects.append(plugin.Class(client))
                    #client.send_message(message.channel, "Plugins reloaded")

                #commands
                if message.content.startswith("!"):
                    if message.content.startswith("!help"):
                        args = message.content.replace("!help","",1).split()
                        if len(args) == 0:
                            for plugin in commandObjects:
                                client.send_message(message.author, "%s\n%s" % (str(plugin.__module__), str(plugin.__doc__)) )
                        return
                    commandName = message.content.split()[0]
                    remainder = message.content.replace(commandName, "", 1)
                    found = callCommand(commandObjects, commandName, remainder, message)
                    if not found:
                        client.send_message(message.channel, dunnos[random.randrange(dunnos.__len__())])
                    return

                #"keyword events"
                for commandObject in commandObjects:
                    for key, funcName in commandObject.commandDict.items():
                        if key[0] != '!' and key[0:2] != "\\" and key in message.content:#if not command and not event then run keyword command
                            if callable(getattr(commandObject, funcName)):
                                getattr(commandObject, funcName)(message)
                                break
                return

        @client.event
        def on_channel_update(channel):
            global commandObjects
            callEvents("\\on_channel_update", commandObjects, channel)

        @client.event
        def on_ready():
            global commandObjects
            global plugins

            print("Logged in as")
            print(client.user.name)
            print(client.user.id)
            print("------")
    
            loadPlugins()
    
        client.run()

    listen()#hey, listen,
