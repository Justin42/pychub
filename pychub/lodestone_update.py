import queue
import threading
from datetime import datetime, timedelta
from time import sleep

from .lodestone.client import LodestoneClient


class Updateable:
    @property
    def update_frequency(self):
        return timedelta(seconds=3600)

    def update_lodestone_data(self, lodestone, **kwargs):
        raise NotImplementedError()


class LodestoneUpdater:
    def __init__(self, delay):
        self.worker_thread = threading.Thread(target=self.__process, daemon=True)
        self.update_queue = queue.LifoQueue()
        self.delay = delay
        self.lodestone = LodestoneClient()
        self.worker_thread.start()
        print("Initialized new update service instance")

    def queue(self, item: Updateable):
        if not item.last_update or item.last_update + item.update_frequency <= datetime.utcnow():
            self.update_queue.put(item)

    @property
    def queue_size(self):
        return self.update_queue.qsize()

    def __process(self):
        while True:
            try:
                item = self.update_queue.get()
                if not item.last_update or item.last_update + item.update_frequency <= datetime.utcnow():
                    item.update_lodestone_data(self.lodestone)
                    print("Finished updating item", item.lodestone_id)
                    sleep(self.delay)
            except Exception as ex:
                print(ex)
