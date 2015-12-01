import random
import string

from .lodestone.client import LodestoneClient


def gen_random(length):
    return ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in
        range(length))


def copy_keys(dict: dict, keys: list, default=None, skip_missing=True):
    new_dict = {}
    for key in keys:
        value = dict.get(key)
        if value or not skip_missing:
            new_dict[key] = dict.get(key, default)
    return new_dict
