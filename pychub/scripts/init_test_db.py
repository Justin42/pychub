from datetime import datetime

from mongoengine import connect

from pychub.model.forum import Category, Topic, Post
from pychub.model.news_post import NewsPost
from pychub.model.user import User, Character


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

    Category.drop_collection()
    category = Category(name="Test Category", link_alias='test', description="This is a test.")
    category.save()

    Topic.drop_collection()
    topic = Topic(name='Test Topic', category=category, user=user)
    topic.posts.append(Post(user=user, content="This is a test post."))
    topic.save()

if __name__ == '__main__':
    init_test_db()
