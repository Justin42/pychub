from mongoengine import DoesNotExist
from pyramid.security import ALL_PERMISSIONS, Allow
from pychub.model.User import User


def get_groups(username, request):
    try:
        groups = User.objects.get(username=username).groups
    except DoesNotExist:
        groups = None
    return groups


class RootFactory(object):
    __name__ = None

    __acl__ = [
        (Allow, 'admin', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        pass