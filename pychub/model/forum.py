from datetime import datetime

from bson import ObjectId
from mongoengine import Document, StringField, DateTimeField, ReferenceField, EmbeddedDocument, SortedListField, \
    EmbeddedDocumentField, ObjectIdField
from .user import User


class Category(Document):
    name = StringField(unique=True, required=True)
    link_alias = StringField(unique=True)
    description = StringField()

    @property
    def last_topic(self):
        try:
            return Topic.objects(category=self).order_by('-last_post_date')[0]
        except IndexError:
            return None

    @property
    def last_post(self):
        last_topic = self.last_topic
        if last_topic and len(last_topic.posts) > 0:
            return last_topic.posts[0]
        else:
            return None

    @property
    def topic_count(self):
        return len(Topic.objects(category=self))

    @property
    def post_count(self):
        count = 0
        for topic in Topic.objects(category=self):
            count += len(topic.posts)
        return count


class Post(EmbeddedDocument):
    id = ObjectIdField(primary_key=True, unique=True, required=True, default=ObjectId)
    user = ReferenceField(User)
    content = StringField()
    post_date = DateTimeField(default=datetime.now)


class Topic(Document):  # TODO Add indexes
    name = StringField(required=True)
    category = ReferenceField(Category)
    user = ReferenceField(User)
    creation_date = DateTimeField(default=datetime.now)
    last_post_date = DateTimeField()
    posts = SortedListField(EmbeddedDocumentField(Post), ordering="post_date", reverse=True)
