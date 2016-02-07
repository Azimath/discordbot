import threading
import code

class REPL:
	commandDict = {}
	def __init__(self, client):
		self.rt = REPLThread([self, client])
		self.rt.start()
Class = REPL
		
class REPLThread(threading.Thread):
	def __init__(self, context):
		super().__init__()
		self.context = context

	def run(self):
		context = self.context
		code.interact(local=locals()) 		

