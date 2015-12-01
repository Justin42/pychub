import queue
import threading
from datetime import datetime, timedelta

from mongoengine import Document

from .lodestone.client import LodestoneClient


class LodestoneUpdater:
    def __init__(self, delay, frequency):
        self.worker_thread = threading.Thread(target=self.__process, daemon=True)
        self.update_queue = queue.LifoQueue()
        self.delay = delay
        self.frequency = timedelta(seconds=frequency)
        self.lodestone = LodestoneClient()
        self.worker_thread.start()
        print("Initialized new update service instance")
        pass

    def queue(self, item: Document):
        if item.last_update + self.frequency <= datetime.utcnow():
            self.update_queue.put(item)
            print("Item added to update queue")

    @property
    def queue_size(self):
        return self.update_queue.qsize()

    def __process(self):
        while True:
            try:
                item = self.update_queue.get()
                print("Updating item...")
                item.update_lodestone_data(self.lodestone)
                print("Finished Update.")
            except Exception as ex:
                print(ex)
