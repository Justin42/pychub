from mongoengine import DoesNotExist, ValidationError
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.view import view_config
from logger import get_logger

from ..model.user import User

log = get_logger(__name__)


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
            else:
                log.info("Password check failed for user '%s' from IP %s", username, request.remote_addr)
        except DoesNotExist:
            message = 'Login failed.'
            return dict(message=message, username=username, password=password)
    return {'username': '', 'password': '', 'message': ''}


@view_config(route_name='register', renderer='register.jinja2')
def register(request): # TODO Add captcha and e-mail verification
    if request.POST:
        if not request.POST['username'] or not request.POST['password'] or not request.POST['email']:
            request.session.flash('Username, password, and e-mail are required fields.')
            return HTTPFound(location=request.route_url('register'))

        username = request.POST['username'].strip()
        email = request.POST['email'].strip()
        password = request.POST['password']

        # Validate
        if not username.isalpha():
            request.session.flash('Username can contain only alphanumeric characters')
            return HTTPFound(location=request.route_url('register'))

        if password != request.POST['password_retype']: # Check that passwords match
            request.session.flash('Password fields do not match.')
            return HTTPFound(location=request.route_url('register'))

        if len(password) < 5 or len(password) > 20: # Password length 5-20 characters
            request.session.flash('Please use a password with a length of at least 5 characters')
            return HTTPFound(location=request.route_url('register'))

        if len(username) < 3 or len(username) > 15: # Username length 3-15 characters
            request.session.flash('Please use a username with a length of at least 3 characters')
            return HTTPFound(location=request.route_url('register'))

        if '@' not in email:  # TODO Proper e-mail validation
            request.session.flash('Invalid e-mail address.')
            return HTTPFound(location=request.route_url('register'))

        try:
            User.objects.get(email__iexact=request.POST['email'])
            request.session.flash('A user with that e-mail has already been registered.')
            return HTTPFound(location=request.route_url('register'))
        except DoesNotExist:
            pass

        try:
            User.objects.get(username__iexact=request.POST['username'])
            request.session.flash('Username already in use.')
            return HTTPFound(location=request.route_url('register'))
        except DoesNotExist:
            pass

        # Valid registration
        user = User()
        user.username = username
        user.set_password(str(password))
        user.email = email
        user.save()
        log.info("User '%s' registered by IP %s", user.username, request.remote_addr)
        request.session.flash('Account created.')
        return HTTPFound(location=request.route_url('home'))
    return {}
