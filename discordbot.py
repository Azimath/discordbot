import discord
import time
import pkgutil
import sys
import json
import random

with open('config.json', 'r') as configfile:
    config = json.loads(configfile.read())
    
client = discord.Client()
client.login(config["DiscordEmail"], config["DiscordPassword"])

def listen():
    @client.event
    def on_message(message):
        global commandObjects
        global plugins
        if message.content.startswith("!help"):
            args = message.content.split()
            if args.__len__() == 1:
                for plugin in commandObjects:
                    client.send_message(message.author, str(plugin.__module__) + "\n" + str(plugin.__doc__))
                    
        #elif message.content.startswith("!reload"):
            #client.send_message(message.channel, "Reloading plugins")
            #print("Reload started")
            #commandObjects = []
            #plugins = load_all_modules_from_dir("plugins")
            #for plugin in plugins:
                #commandObjects.append(plugin.Class(client))
            #client.send_message(message.channel, "Plugins reloaded")
            
        elif message.author.id != client.user.id:
            found = False
            
            for commandObject in commandObjects:
                for key, funcName in commandObject.commandDict.items():
                    if key == '\\':
                        if callable(getattr(commandObject, funcName)):
                            getattr(commandObject, funcName)(message)
                    elif key[0] == '!':
                        if message.content.startswith(key):
                            if callable(getattr(commandObject, funcName)):
                                getattr(commandObject, funcName)(message)
                                found = True
                                break
                    elif key in message.content:
                        if callable(getattr(commandObject, funcName)):
                            getattr(commandObject, funcName)(message)
                            break
            if not found and message.content.startswith("!"):
                client.send_message(message.channel, dunnos[random.randrange(dunnos.__len__())])

    @client.event
    def on_channel_update(channel):
        global commandObjects
        for commandObject in commandObjects:
            for key, funcName in commandObject.commandDict.items():
                if key == '\\on_channel_update':
                    if callable(getattr(commandObject, funcName)):
                        getattr(commandObject, funcName)(channel)
    
    @client.event
    def on_ready():
        global commandObjects
        global plugins

        print("Logged in as")
        print(client.user.name)
        print(client.user.id)
        print("------")

        def load_all_modules_from_dir(dirname): #modded from: http://stackoverflow.com/questions/1057431/loading-all-modules-in-a-folder-in-python/8556471#8556471
            modules = []
            for importer, package_name, _ in pkgutil.iter_modules([dirname]):
                full_package_name = '%s.%s' % (dirname, package_name)
                if full_package_name not in sys.modules:
                    modules.append(importer.find_module(package_name).load_module(full_package_name))
                    print(modules[-1]) #python, where this means the last element of a list
            return modules
    
        plugins = load_all_modules_from_dir("plugins")

        commandObjects = []

        for plugin in plugins:
            commandObjects.append(plugin.Class(client))
    
        print(str(commandObjects.__len__()) + " plugins loaded")
    client.run()

listen()
