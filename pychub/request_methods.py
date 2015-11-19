from mongoengine import DoesNotExist
from .model.User import User


def get_user(request):
    try:
        return User.objects.get(username=request.authenticated_userid)
    except DoesNotExist:
        return None


def is_logged_in(request):
    if request.authenticated_userid:
        return True
    else:
        return False
