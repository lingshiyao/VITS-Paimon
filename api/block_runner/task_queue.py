from api.task import Task


class TaskQueue:
    tasks: Task = []

    def remove_task_by_token(self, token):  # remove task by token
        for task in self.tasks:
            if task.token == token:
                self.tasks.remove(task)
                return True
        return False

    # remove not running task by token
    def remove_not_running_task_by_token(self, token):
        for task in self.tasks:
            if task.token == token and not task.running:
                self.tasks.remove(task)
                return True
        return False

    def is_task_running(self, token):  # is task running
        for task in self.tasks:
            if task.token == token and task.running:
                return True
        return False

    # return true update success
    # return false isRunning
    def add_task(self, task: Task):
        is_running = self.is_task_running(task.token)
        if not is_running:
            self.remove_not_running_task_by_token(task.token)
            self.enqueue(task)
            return True
        else:
            return False

    def enqueue(self, task: Task):  # 入队
        self.tasks.insert(0, task)

    # 返回队列头部元素
    def get_not_running_head(self):
        length = len(self.tasks)
        for i in range(length - 1, -1, -1):
            if not self.tasks[i].running:
                return self.tasks[i]
        return None

    # 返回队列的大小
    def size(self):
        return len(self.tasks)

    # -1 not found
    # 0 running
    # >0 排队中
    def get_index_not_running(self, token):
        length = len(self.tasks)
        # Traversal in reverse
        count = 0
        for i in range(length - 1, -1, -1):
            if not self.tasks[i].running:
                if self.tasks[i].token == token:
                    return count + 1
                count += 1
            else:
                if self.tasks[i].token == token:
                    return 0
        return -1
