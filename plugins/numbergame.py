import random
import asyncio

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
class NumberGame:
	legacy = True
	"""A plugin that plays a simple high-low number guessing game.
	!startgame <range> : starts a game with a number between 1 and range. range is 100 if not given.
	!guess number : Enters a guess, then tells you if it is high, low, or correct. A correct guess ends the game. Guesses that have been guessed before are not acccepted.
	!stop : stops the game in the current channel"""
	def __init__(self, client):
		self.client = client
		self.games = {}	
	async def startgame(self, message):
		if message.channel.id in self.games:
			await self.client.send_message(message.channel, "Sorry, a game is already in progress")
			return
		
		args = message.content.split()
		range = 100
		for arg in args:
			try:
				range = int(arg)
				break
			except:
				range = 100
		newgame = Game(range)
		self.games[message.channel.id] = newgame
		await self.client.send_message(message.channel, "Game started")
		
	async def guess(self, message):
		if not message.channel.id in self.games:
			await self.client.send_message(message.channel, "No game in progress for this channel")
			return
		
		args = message.content.split()
		guess = 0
		for arg in args:
			try:
				guess = int(arg)
				break
			except:
				guess = 0
		
		if self.games[message.channel.id].wasguessed(guess):
			await self.client.send_message(message.channel, "Sorry but " + str(guess) + " was already guessed")
			return
		
		result = self.games[message.channel.id].guess(guess)
		if result == 0:
			await self.client.send_message(message.channel, "User " + message.author.name + " won! With " + str(self.games[message.channel.id].guesses) + " guesses. !startgame to play again")
			await self.client.send_message(message.channel, "Guesses: " + str(self.games[message.channel.id].previousGuesses))
			self.games.pop(message.channel.id, None)
		elif result == -1:
			await self.client.send_message(message.channel, "Guess " + str(guess) + " was too low. Number of guesses so far: " + str(self.games[message.channel.id].guesses) + ".")
		elif result == 1:
			await self.client.send_message(message.channel, "Guess " + str(guess) + " was too high. Number of guesses so far: " + str(self.games[message.channel.id].guesses) + ".")
		else:
			await self.client.send_message(message.channel, "What the fuck")

	async def stop(self, message):
		if not message.channel.id in self.games:
			await self.client.send_message(message.channel, "Theres no game to stop")
			return
		
		self.games.pop(message.channel.id, None)
		await self.client.send_message(message.channel, "Game stopped")
	commandDict = { "!startgame": "startgame", "!guess" : "guess", "!stop" : "stop" }
Class = NumberGame
