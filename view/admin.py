from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.view import view_config

from pychub import User
from pychub.model.NewsPost import NewsPost

models = {'User': User, 'NewsPost': NewsPost}
actions = ['view', 'edit', 'add', 'delete']
fields = {'User': ['username', 'email', 'groups']}
display_models = {'User': User}

@view_config(route_name='admin', renderer='admin/index.jinja2', permission='admin')
def index(request):
    return dict(models=display_models)


@view_config(route_name='admin_view_model', renderer='admin/view_model.jinja2', permission='admin')
def view_model(request):
    model = request.matchdict['model']
    if model not in models:
        return HTTPNotFound('Invalid model specified.')
    return {'fields': fields[model], 'model': models[model], 'model_name': model}


@view_config(route_name='admin_delete_item', permission='admin')
def delete_item(request):
    id = request.matchdict['id']
    model = models[request.matchdict['model']]
    model.objects.get(id=id).delete()
    ref = request.params.get('ref')
    if not ref:
        ref = request.route_url('home')
    return HTTPFound(location=ref)

