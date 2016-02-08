import threading
import code


class REPL:
    commandDict = {"\\set_root_context_on_load":"setRootContext"}

    def __init__(self, client):
        pass

    def setRootContext(self, context):
        self.rt = REPLThread(context)
        self.rt.start()

Class = REPL


class REPLThread(threading.Thread):
    def __init__(self, context):
        super().__init__()
        self.context = context

    def run(self):
        code.interact(local=self.context)
