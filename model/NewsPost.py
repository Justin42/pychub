from datetime import datetime
from mongoengine import *
from . import User


class NewsPost(Document):
    user = ReferenceField(User, required=True)
    date = DateTimeField(default=datetime.now)
    title = StringField()
    body = StringField()
