class cb_timer:
    def __init__( self, callback, msg, timeout=10 ):
        self._timeout = 10
        self.callback = callback
