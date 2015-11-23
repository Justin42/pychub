import random
import string

from .lodestone.client import LodestoneClient


def gen_random(length):
    return ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in
        range(length))

lodestone = LodestoneClient()
