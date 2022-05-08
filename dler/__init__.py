from .tasker import BaseTasker, conver_tasker


class Dler:
    tasker: BaseTasker
    def __init__(self, url: str, **kwargs):
        self.tasker = conver_tasker(url, **kwargs)

    def run(self):
        """运行

        """
        self.tasker.build()
        self.tasker.run()
        self.tasker.after_run()
