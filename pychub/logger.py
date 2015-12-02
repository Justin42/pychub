import logging
import logging.handlers

# TODO It's probably better to do this through pyramids logging configuration

import sys

_file_handler = logging.handlers.TimedRotatingFileHandler(filename='error.log', when='midnight')
_memory_handler = logging.handlers.MemoryHandler(capacity=1024*10, flushLevel=logging.ERROR, target=_file_handler)
_stream_handler = logging.StreamHandler(stream=sys.stderr)

__initialized = False


def __init():
    global __initialized
    formatter = logging.Formatter("%(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s")
    _file_handler.setFormatter(formatter)
    _file_handler.setLevel(logging.WARN)
    _stream_handler.setFormatter(formatter)
    __initialized = True


def get_logger(clazz):
    if type(clazz) is str:
        clazz = clazz[clazz.find('.')+1:] # Strip top level package name
        log = logging.getLogger(clazz)
    else:
        log = logging.getLogger(type(clazz).__name__)
    if not __initialized:
        __init()
    log.setLevel(logging.DEBUG)
    log.addHandler(_memory_handler)
    log.addHandler(_stream_handler)
    return log
