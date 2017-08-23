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

@commands.registerEventHander(name="startgame")
async def startgame(triggerMessage):
    if triggerMessage.channel.id in games:
        await client.send_message(triggerMessage.channel, "Sorry, a game is already in progress")
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
    await client.send_message(triggerMessage.channel, "Game started")
    
@commands.registerEventHander(name="guess")	
async def guess(triggerMessage):
    if not triggerMessage.channel.id in games:
        await client.send_message(triggerMessage.channel, "No game in progress for this channel")
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
        await client.send_message(triggerMessage.channel, "Sorry but " + str(guess) + " was already guessed")
        return
    
    result = games[triggerMessage.channel.id].guess(guess)
    if result == 0:
        await client.send_message(triggerMessage.channel, "User " + triggerMessage.author.name + " won! With " + str(games[triggerMessage.channel.id].guesses) + " guesses. !startgame to play again")
        await client.send_message(triggerMessage.channel, "Guesses: " + str(games[triggerMessage.channel.id].previousGuesses))
        games.pop(triggerMessage.channel.id, None)
    elif result == -1:
        await client.send_message(triggerMessage.channel, "Guess " + str(guess) + " was too low. Number of guesses so far: " + str(games[triggerMessage.channel.id].guesses) + ".")
    elif result == 1:
        await client.send_message(triggerMessage.channel, "Guess " + str(guess) + " was too high. Number of guesses so far: " + str(games[triggerMessage.channel.id].guesses) + ".")
    else:
        await client.send_message(triggerMessage.channel, "What the fuck")

@commands.registerEventHander(name="stopgame")
async def stop(triggerMessage):
    if not triggerMessage.channel.id in games:
        await client.send_message(triggerMessage.channel, "Theres no game to stop")
        return
    
    games.pop(triggerMessage.channel.id, None)
    await client.send_message(triggerMessage.channel, "Game stopped")
    
