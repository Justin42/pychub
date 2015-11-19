from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from pychub.exceptions import CharacterAlreadyLinked, CharacterNotFound


@view_config(route_name='account', renderer='account/index.jinja2', permission='member')
def index(request):
    return {'user': request.get_user}


@view_config(route_name='account_add_character', renderer='account/add_character.jinja2', permission='member')
def add_character(request):
    user = request.get_user
    # Step 1
    if 'name' in request.POST and 'server' in request.POST:
        try:
            link_code = user.get_link_code(request.POST['name'], request.POST['server'])
        except CharacterAlreadyLinked:
            request.session.flash("That character is already linked to an account.")
            return {'user': user}
        except CharacterNotFound:
            request.session.flash("Unable to locate character. Is it a member of a known free company?")
            return {'user': user}
        return {'user': user, 'link_code': link_code, 'character_name': request.POST['name']}

    # Step 2
    if 'confirm' in request.POST:
        character = user.confirm_character()
        if not character:
            request.session.flash("Unable to verify character.")
            return {'user': user}
        else:
            request.session.flash("Character verified.")
            return HTTPFound(location=request.route_url('account'))

    return {'user': user}
