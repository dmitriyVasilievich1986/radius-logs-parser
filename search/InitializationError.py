from .Config import V3

class InitializationError(Exception):
    def __init__(self, *args, **kwargs):
        if V3:
            super().__init__(*args, **kwargs)
        else:
            super(Exception, self).__init__(*args, **kwargs)