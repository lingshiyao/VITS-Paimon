from api.block_runner.base_task import BaseTask


class Task(BaseTask):
    def __init__(self, token: str, text: str = None):
        super().__init__(token)
        self.text = text

    text: str
