from api.block_runner.base_task import BaseTask


class Task(BaseTask):
    need_cache: bool
    need_refresh_cache: bool

    def __init__(self, token: str, text: str = None, need_cache: bool = False, need_refresh_cache: bool = False):
        super().__init__(token)
        self.text = text
        self.need_refresh_cache = need_refresh_cache
        self.need_cache = need_cache

    text: str
