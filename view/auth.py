from mongoengine import DoesNotExist
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.view import view_config

from pychub.model.User import User

__author__ = 'Justin Baldwin'


@view_config(route_name='login', renderer='login.jinja2')
def login(request):
    if 'username' in request.POST:
        username = request.POST['username']
        password = request.POST['password']
        referrer = request.url
        if referrer == request.resource_url(request.context, 'login'):
            referrer = '/'
        came_from = request.params.get('came_from', referrer)
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                headers = remember(request, username)
                return HTTPFound(location=came_from, headers=headers)
        except DoesNotExist:
            message = 'Login failed.'
            return dict(message=message, username=username, password=password)
    return {'username': '', 'password': '', 'message': 'Test'}
