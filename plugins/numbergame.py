import random
import asyncio
import commands

class Game:
	def __init__(self, range=100):
		self.targetNumber = random.randrange(1,range)
		self.guesses = 0
		self.previousGuesses = []
	def wasguessed(self, guess):
		return guess in self.previousGuesses
	def guess(self, guess):
		self.guesses += 1
		self.previousGuesses.append(guess)

		if guess == self.targetNumber:
			return 0
		elif guess < self.targetNumber:
			return -1
		elif guess > self.targetNumber:
			return 1

	"""A plugin that plays a simple high-low number guessing game.
	!startgame <range> : starts a game with a number between 1 and range. range is 100 if not given.
	!guess number : Enters a guess, then tells you if it is high, low, or correct. A correct guess ends the game. Guesses that have been guessed before are not acccepted.
	!stopgame : stops the game in the current channel"""

client = None
games = {}

@commands.registerEventHandler(name="startgame")
async def startgame(triggerMessage):
    if triggerMessage.channel.id in games:
        await triggerMessage.channel.send( "Sorry, a game is already in progress")
        return
    
    args = triggerMessage.content.split()
    range = 100
    for arg in args:
        try:
            range = int(arg)
            break
        except:
            range = 100
    newgame = Game(range)
    games[triggerMessage.channel.id] = newgame
    await triggerMessage.channel.send( "Game started")
    
@commands.registerEventHandler(name="guess")	
async def guess(triggerMessage):
    if not triggerMessage.channel.id in games:
        await triggerMessage.channel.send( "No game in progress for this channel")
        return
    
    args = triggerMessage.content.split()
    guess = 0
    for arg in args:
        try:
            guess = int(arg)
            break
        except:
            guess = 0
    
    if games[triggerMessage.channel.id].wasguessed(guess):
        await triggerMessage.channel.send( "Sorry but " + str(guess) + " was already guessed")
        return
    
    result = games[triggerMessage.channel.id].guess(guess)
    if result == 0:
        await triggerMessage.channel.send( "User " + triggerMessage.author.name + " won! With " + str(games[triggerMessage.channel.id].guesses) + " guesses. !startgame to play again")
        await triggerMessage.channel.send( "Guesses: " + str(games[triggerMessage.channel.id].previousGuesses))
        games.pop(triggerMessage.channel.id, None)
    elif result == -1:
        await triggerMessage.channel.send( "Guess " + str(guess) + " was too low. Number of guesses so far: " + str(games[triggerMessage.channel.id].guesses) + ".")
    elif result == 1:
        await triggerMessage.channel.send( "Guess " + str(guess) + " was too high. Number of guesses so far: " + str(games[triggerMessage.channel.id].guesses) + ".")
    else:
        await triggerMessage.channel.send( "What the fuck")

@commands.registerEventHandler(name="stopgame")
async def stop(triggerMessage):
    if not triggerMessage.channel.id in games:
        await triggerMessage.channel.send( "Theres no game to stop")
        return
    
    games.pop(triggerMessage.channel.id, None)
    await triggerMessage.channel.send( "Game stopped")
    
