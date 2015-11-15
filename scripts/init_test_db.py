from datetime import datetime

from mongoengine import connect

from pychub.model.NewsPost import NewsPost
from pychub.model.User import User, Character


def init_test_db():
    connect('CompanyHub')
    User.drop_collection()
    user = User()
    user.username = 'testadmin'
    user.set_password('admin')
    user.groups.append('admin')
    user.email = 'test@example.com'
    user.save()
    user = User()
    user.username = 'testuser'
    user.set_password('user')
    user.groups.append('member')
    user.email = 'test1@example.com'
    user.save()

    NewsPost.drop_collection()
    news_post = NewsPost()
    news_post.user = User.objects.get(username='testadmin')
    news_post.date = datetime.now()
    news_post.title = 'Test Post'
    news_post.body = 'Testing. Only a test.'
    news_post.save()
