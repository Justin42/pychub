from datetime import datetime

from mongoengine import Document, StringField, DateTimeField, ReferenceField, EmbeddedDocument, SortedListField, \
    EmbeddedDocumentField

from .User import User


class Category(Document):
    name = StringField(unique=True, required=True)
    link_alias = StringField(unique=True)
    description = StringField()


class Post(EmbeddedDocument):
    user = ReferenceField(User)
    content = StringField()
    post_date = DateTimeField(default=datetime.now())


class Topic(Document):  # TODO Add indexes
    name = StringField(required=True)
    category = ReferenceField(Category)
    user = ReferenceField(User)
    creation_date = DateTimeField(default=datetime.now())
    last_post_date = DateTimeField()
    posts = SortedListField(EmbeddedDocumentField(Post), ordering="post_date", reverse=True)