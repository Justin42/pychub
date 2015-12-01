from datetime import datetime
import warnings

from bcrypt import hashpw, gensalt
from mongoengine import *

from ..lodestone_update import Updateable
from ..lodestone.client import LodestoneClient
from ..exceptions import CharacterNotFound, CharacterAlreadyLinked, InvalidLinkCode
from .free_company import FreeCompany
from .common import classes, servers, genders, grand_companies, races, groups
from ..util import gen_random


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


class Character(Document, Updateable):
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
    last_update = DateTimeField()

    @property
    def class_dict(self):
        class_dict = {}
        for _class in self.classes:
            class_dict[_class.name] = _class
        return class_dict

    @property
    def user(self):
        return User.objects(characters__id=self.id)

    def update_lodestone_data(self, lodestone: LodestoneClient, achievements=True):
        new_data = lodestone.get_character_data(self.lodestone_id, achievements)

        # Update basic
        for key, value in new_data.items():
            setattr(self, key, value)

        # Update classes
        self.classes = [
            ClassData(name=c['name'], level=c['level'], current_exp=c['current_exp'], next_exp=c['next_exp']) for
            c in new_data['classes']
        ]

        # Update Achievements
        self.recent_achievements = [
            AchievementInfo(date=a['date'], type=a['type'], name=a['name'], text=a['text']) for
            a in new_data['recent_achievements']
        ]
        try:
            self.free_company = FreeCompany.objects.get(lodestone_id=new_data['free_company'])
        except DoesNotExist:  # TODO Logging
            return None
        self.last_update = datetime.utcnow()
        self.save()
        return self


class LinkCode(EmbeddedDocument):
    character = ReferenceField(Character)
    code = StringField()


class User(Document):
    username = StringField(required=True, max_length=20, min_length=3, unique=True)
    __password = StringField(required=True, db_field='password')
    email = EmailField(required=True, unique=True)
    groups = ListField(StringField(choices=groups), default=['member'])
    characters = ListField(ReferenceField(Character))
    link_code = EmbeddedDocumentField(LinkCode)

    def set_password(self, password, rounds=12):
        self.__password = hashpw(password.encode(), gensalt(rounds=rounds)).decode()

    def check_password(self, password):
        return hashpw(password.encode(), self.__password.encode()) == self.__password.encode()

    def get_link_code(self, character_name, server):
        # Check if character is tracked
        try:
            character = Character.objects.get(server=server, name=character_name)
        except DoesNotExist:
            raise CharacterNotFound
        link_code = LinkCode(character=character, code=gen_random(20))
        self.link_code = link_code
        self.save()
        return link_code.code

    def confirm_character(self):
        if not self.link_code:
            return False

        character = self.link_code.character.update_lodestone_data()

        # Check profile contents
        if self.link_code.code in character.lodestone_profile:
            self.link_code = None
            self.save()
            character.confirmed = True
            character.save()
            self.update(push__characters=character)

        return character
