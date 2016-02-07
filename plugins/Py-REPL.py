import threading
import code

class REPL:
	commandDict = {"\\set_root_context_on_load":"setRootContext"}
	def __init__(self, client):
		pass

	def setRootContext(self, rootContext):
		self.rt = REPLThread(rootContext)
		self.rt.start()

Class = REPL
		
class REPLThread(threading.Thread):
	def __init__(self, context):
		super().__init__()
		self.context = context

	def run(self):
		context = self.context
		code.interact(local=locals()) 		

