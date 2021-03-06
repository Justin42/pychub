import math
from mongoengine import DoesNotExist, NotUniqueError
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from bs4 import BeautifulSoup
import bbcode
from ..model.forum import Category, Topic, Post
from ..logger import get_logger

log = get_logger(__name__)


@view_config(route_name='forum', renderer='forum/index.jinja2')
def index(request):
    return {'categories': Category.objects}


@view_config(route_name='forum_category', renderer='forum/category.jinja2')
def category_view(request):  # TODO Paginate topics
    try:
        category = Category.objects.get(name=request.matchdict['category_name'])
    except DoesNotExist:
        try:
            category = Category.objects.get(link_alias=request.matchdict['category_name'])
        except DoesNotExist:
            request.session.flash("Invalid category.")
            return HTTPFound(location=request.route_url('forum'))
    topics = Topic.objects(category=category).order_by('-last_post_date')
    return {'topics': topics, 'category': category}


@view_config(route_name='forum_topic', renderer='forum/topic.jinja2')
def topic_view(request):
    posts_per_page = 20  # TODO Posts per page should probably be configurable
    page = int(request.matchdict['page'])
    start = (page - 1) * posts_per_page
    end = posts_per_page * page
    try:
        topic = Topic.objects.get(id=request.matchdict['topic_id'])
        posts = topic.posts[start:end]
    except DoesNotExist:
        request.session.flash("Invalid topic ID")
        return HTTPFound(location=request.route_url('forum'))

    last_page = math.ceil(len(topic.posts) / posts_per_page)

    if 'content' in request.POST and request.has_permission('forum_post_reply'):
        content = BeautifulSoup(request.POST['content'][:5000], 'html.parser').get_text()  # Strip all HTML
        content = bbcode.render_html(content)  # Convert remaining BBCode to HTML
        post = Post(user=request.get_user, content=content)
        topic.update(push__posts=post, last_post_date=post.post_date)
        request.session.flash('New reply posted.')
        return HTTPFound(location=request.route_url('forum_topic', page=page, topic_id=topic.id))
    return {'posts': posts, 'topic': topic, 'page': page, 'category': topic.category, 'last_page': last_page,
            'start_post': start+1, 'end_post': min(end, len(topic.posts)), 'total_posts': len(topic.posts)}


@view_config(route_name='forum_add_category', renderer='forum/add_category.jinja2', permission='forum_add_category')
def add_category(request):
    if 'name' in request.POST:
        try:
            category = Category()
            category.name = request.POST['name'].strip()
            if 'alias' in request.POST:
                category.link_alias = request.POST['alias'].strip()
            if category.link_alias == '':
                category.link_alias = category.name.lower()
            if 'description' in request.POST:
                category.description = request.POST['description'].strip()
            category.save()
            log.info("New category created '%s' by user %s", category.name, request.authenticated_userid)
            return HTTPFound(location=request.route_url('forum'))
        except NotUniqueError as ex:
            request.session.flash('A category with that name or alias already exists')
            log.exception('Could not create category %s', category.name)
            return {}
    else:
        return {}


@view_config(route_name='forum_new_topic', renderer='forum/new_topic.jinja2', permission='forum_new_topic')
def new_topic(request):  # TODO configurable max chars for title and content
    category = Category.objects.get(id=request.matchdict['category_id'])
    if 'name' in request.POST and 'content' in request.POST:
        content = BeautifulSoup(request.POST['content'][:5000], 'html.parser').get_text()  # Strip all HTML
        content = bbcode.render_html(content)  # Convert remaining BBCode to HTML
        topic = Topic(user=request.get_user, name=request.POST['name'][:100], category=category)
        post = Post(user=request.get_user, content=content)
        topic.last_post_date = post.post_date
        topic.posts.append(post)
        topic.save()
        return HTTPFound(location=request.route_url('forum_topic', topic_id=topic.id, page=1))
    return {'category': category}


@view_config(route_name='forum_delete_topic', permission='forum_delete_topic')
def delete_topic(request):
    topic = Topic.objects.get(id=request.matchdict['topic_id'])
    topic.delete()
    request.session.flash("Topic deleted.")
    return HTTPFound(location=request.route_url('forum_category', category_name=topic.category.name))


@view_config(route_name='forum_delete_post', permission='forum_delete_post')
def delete_post(request):
    topic = Topic.objects.get(id=request.matchdict['topic_id'])
    topic.update(pull__posts__id=request.matchdict['post_id'])
    return HTTPFound(location=request.route_url('forum_topic', topic_id=topic.id, page=1))
