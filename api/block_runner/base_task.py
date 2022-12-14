class BaseTask:
    running: bool = False
    token = None

    def __init__(self, token):
        self.token = token
