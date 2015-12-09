import queue
import threading
from datetime import datetime, timedelta
from time import sleep

from mongoengine import DoesNotExist

from .lodestone.client import LodestoneClient
from .logger import get_logger


class Updateable:
    @property
    def update_frequency(self):
        return timedelta(seconds=3600)

    def update_lodestone_data(self, lodestone, **kwargs):
        raise NotImplementedError()


class LodestoneUpdater:
    def __init__(self, delay):
        self.log = get_logger(self)
        self.worker_thread = threading.Thread(target=self.__process, daemon=True, name='UpdateThread')
        self.update_queue = queue.LifoQueue()
        self.delay = delay
        self.lodestone = LodestoneClient()
        self.worker_thread.start()
        self.enabled = True
        self.log.info("Initialized lodestone update service")

    def queue(self, item: Updateable):
        if not self.enabled:
            return
        try:
            if not item.last_update or item.last_update + item.update_frequency <= datetime.utcnow():
                self.log.info("Queueing item for update %s %s '%s'", type(item).__name__, item.lodestone_id, item.name)
                self.log.debug("Update queue size: %d", self.update_queue.qsize())
                self.update_queue.put(item)
        except Exception as ex:
            self.log.exception('Unable to queue item for update')

    @property
    def queue_size(self):
        return self.update_queue.qsize()

    def __process(self):
        while True:
            try:
                item = self.update_queue.get()
                # Update object from database record
                try:
                    item = item.__class__.objects.get(lodestone_id=item.lodestone_id)
                except DoesNotExist:
                    self.log.info("Adding new lodestone item to database '%s'", item.lodestone_id)
                if not item.last_update or item.last_update + item.update_frequency <= datetime.utcnow():
                    item.update_lodestone_data(self.lodestone)
                    self.log.info("Finished updating item %s %s '%s'", type(item).__name__, item.lodestone_id, item.name)
                    sleep(self.delay)
                else:
                    self.log.info("Skipping item update for %s %s '%s'", type(item).__name__, item.lodestone_id, item.name)

                # Queue new FC members to gather initial data
                # TODO This isn't very efficient.
                if type(item).__name__ == 'FreeCompany':
                    fc_members = set([member.lodestone_id for member in item.members])
                    from pychub import Character
                    known_members = Character.objects(free_company=item, lodestone_id__in=fc_members)
                    known_members = set([member.lodestone_id for member in known_members])
                    new_members = fc_members - known_members
                    for member in new_members:
                        character = Character(lodestone_id=member)
                        self.queue(character)


            except Exception as ex:
                self.log.exception("Cannot update object")

