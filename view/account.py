from pyramid.view import view_config


@view_config(route_name='account', renderer='account/index.jinja2', permission='member')
def index(request):
    return {'user': request.get_user}


@view_config(route_name='account_add_character', renderer='account/link_character.jinja2', permission='member')
def add_character(request):
    return {}
