from bcrypt import hashpw, gensalt
from mongoengine import *

from model.FreeCompany import FreeCompany
from .common import *


class ClassData(EmbeddedDocument):
    name = StringField(choices=classes, required=True)
    level = IntField(min_value=1, max_value=60, required=True)
    current_exp = LongField()
    next_exp = LongField()


class AchievementInfo(EmbeddedDocument):
    date = DateTimeField()
    type = StringField()
    name = StringField()
    text = StringField()


class Character(Document):
    name = StringField(required=True)
    server = StringField(choices=servers, required=True)
    free_company = ReferenceField(FreeCompany)
    confirmed = BooleanField(required=True, default=False)
    guardian = StringField()
    gender = StringField(choices=genders)
    classes = ListField(EmbeddedDocumentField(ClassData))
    nameday = StringField(required=True)
    city_state = StringField(required=True)
    grand_company = StringField(choices=grand_companies)
    grand_company_rank = StringField()
    mounts = ListField(StringField())
    minions = ListField(StringField())
    recent_achievements = ListField(EmbeddedDocumentField(AchievementInfo))
    race = StringField(choices=races)
    lodestone_profile = StringField()
    lodestone_id = StringField(unique=True, required=True)

    @property
    def user(self):
        return User.objects(characters__id=self.id)


class User(Document):
    username = StringField(required=True, max_length=20, min_length=3, unique=True)
    __password = StringField(required=True, db_field='password')
    email = EmailField(required=True, unique=True)
    groups = ListField(StringField(choices=groups))
    characters = ListField(ReferenceField(Character))

    def set_password(self, password, rounds=12):
        self.__password = hashpw(password.encode(), gensalt(rounds=rounds)).decode()

    def check_password(self, password):
        return hashpw(password.encode(), self.__password.encode()) == self.__password.encode()
