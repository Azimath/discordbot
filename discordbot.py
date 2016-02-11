import discord
import pkgutil
import sys
import json
import asyncio

#yay, bad bad "superglobal" things?
import builtins
import permissions
builtins.permissions = permissions

####Helper stuff
def loadPlugins():
    global commandObjects

    #see: http://stackoverflow.com/questions/1057431/loading-all-modules-in-a-folder-in-python/8556471#8556471
    def load_all_modules_from_dir(dirname):
        modules = []
        for importer, package_name, _ in pkgutil.iter_modules([dirname]):
            full_package_name = '%s.%s' % (dirname, package_name)
            if full_package_name not in sys.modules:  #TODO:get a proper plugin framework, idk if this needs to be changed like the following line was (see commit history)
                mod = importer.find_module(package_name).load_module(package_name)
                modules.append(mod)
                print(mod)
        return modules
    
    plugins = load_all_modules_from_dir("plugins")
    commandObjects = [plugin.Class(client) for plugin in plugins]

    context = globals()
    context.update(locals())
    callEvents("\\set_root_context_on_load", commandObjects, context)  #TODO: probably dont need to pass locals()
    print("%s plugins loaded" % len(commandObjects))


class COCallablesIterator:  #co = commandobjects
    def __init__(self, cos, name):
        self.cos = cos
        self.name = name

    def __iter__(self):
        for commandObject in self.cos:
            for key, funcName in commandObject.commandDict.items():
                if key == self.name:
                    thing = getattr(commandObject, funcName)
                    if callable(getattr(commandObject, funcName)):
                        yield thing, commandObject


def callEvents(eventName, cos, *args, **kwargs):
    calledCount = 0
    for method, commandObject in COCallablesIterator(cos, eventName):
        method(*args, **kwargs)
        calledCount += 1
    return calledCount


#TODO: what if?: !command is defined multiple times
def callCommand(cos, commandName, remainder, messageObj, *args, **kwargs):
    for method, commandObject in COCallablesIterator(cos, commandName):
        if hasattr(commandObject, "legacy") and commandObject.legacy:
            method(messageObj)
        else:
            method(remainder, messageObj, *args, **kwargs)
        return True  #TODO: continue or not? => if yes, return counter instead of bool
    return False

#####
#####


if __name__ == "__main__":
    with open('config.json', 'r') as configfile:
        config = json.loads(configfile.read())

    client = discord.Client()

    def listen():
        @client.event
        async def on_message(message):
            callEvents("\\message_with_bot", commandObjects, message)

            if message.author.id != client.user.id:  #we ignore our own messages
                callEvents("\\message_no_bot", commandObjects, message)

                #commands
                if message.content.startswith("!"):
                    if message.content.startswith("!help"):
                        args = message.content.replace("!help", "", 1).split()
                        if len(args) == 0:
                            for plugin in commandObjects:
                                asyncio.ensure_future(client.send_message(message.author, "%s\n%s" % (str(plugin.__module__), str(plugin.__doc__))))
                        return
                    commandName = message.content.split()[0]  #TODO:im not sure if this should be done in *this* part of the code, but then how?
                    remainder = message.content.replace(commandName, "", 1)
                    found = callCommand(commandObjects, commandName, remainder, message)
                    if not found:
                        callEvents("\\command_not_found", commandObjects, commandName, message)  #TODO: how much functionality should be plugins? taken to the extreme the bot could just be a "loader"
                    return

                #"keyword events"
                for commandObject in commandObjects:
                    for key, funcName in commandObject.commandDict.items():
                        #if not command and not event then run keyword command
                        if not key.startswith("!") and not key.startswith("\\") and key in message.content:
                            if callable(getattr(commandObject, funcName)):
                                getattr(commandObject, funcName)(message)
                                break
                return

        @client.event
        async def on_channel_update(before, after):
            callEvents("\\on_channel_update", commandObjects, after)

        @client.event
        async def on_ready():
            global commandObjects

            print("Logged in as")
            print(client.user.name)
            print(client.user.id)
            print("------")
    
            loadPlugins()
    
        client.run(config["DiscordEmail"], config["DiscordPassword"])

    listen()  #hey, listen,
