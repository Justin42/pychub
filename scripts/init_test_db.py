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


def most_minions():
    connect('CompanyHub')
    highest = Character.objects[0]
    for char in Character.objects:
        if len(char.minions) == len(highest.minions):
            print(char.name, 'tied with', highest.name, 'with', len(char.minions), 'minions')
        if len(char.minions) > len(highest.minions):
            highest = char
    print(highest.name, "has the most minions with", len(highest.minions))


def most_mounts():
    connect('CompanyHub')
    highest = Character.objects[0]
    for char in Character.objects:
        if len(char.mounts) == len(highest.mounts):
            print(char.name, 'tied with', highest.name, 'with', len(char.mounts), 'mounts')
        if len(char.mounts) > len(highest.mounts):
            highest = char
    print(highest.name, "has the most mounts with", len(highest.mounts))
