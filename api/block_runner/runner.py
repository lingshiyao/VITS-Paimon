from api.log.log import Log


class Runner:
    runner = []

    def get_lock_count(self):
        count = 0
        for item in self.runner:
            if item.lock:
                count += 1
        return count

    def get_unlock_item(self):
        for item in self.runner:
            if not item.lock:
                return item
        return None

    def get_runner_count(self):
        return len(self.runner)

    def get_runner_count(self):
        return len(self.runner)

    def __init__(self, runner):
        self.runner = runner
        Log.print("paimon runner init finish")

    def run(self, method_name, *args, **kwargs):
        for item in self.runner:
            result = getattr(item, method_name)(*args, **kwargs)
            if result is not None:
                return result
        return None
