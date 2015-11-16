from bcrypt import hashpw, gensalt
from mongoengine import *

from exceptions import CharacterNotFound, CharacterAlreadyLinked, InvalidLinkCode
from model.FreeCompany import FreeCompany
from model.common import classes, servers, genders, grand_companies, races, groups
from util import gen_random


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

    @staticmethod
    def from_dict(char_dict):
        character = Character()

        for key, value in char_dict.items():
            setattr(character, key, value)

        character.classes = [
            ClassData(name=c['name'], level=c['level'], current_exp=c['current_exp'], next_exp=c['next_exp']) for
            c in char_dict['classes']
        ]

        character.recent_achievements = [
            AchievementInfo(date=a['date'], type=a['type'], name=a['name'], text=a['text']) for
            a in char_dict['recent_achievements']
        ]

        try:
            character.free_company = FreeCompany.objects.get(lodestone_id=char_dict['free_company'])
        except DoesNotExist:  # TODO Logging
            return None
        return character


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
        # Check if character is already linked to an account
        if character.confirmed:
            raise CharacterAlreadyLinked
        link_code = LinkCode(character=character, code=gen_random(20))
        self.link_code = link_code
        self.save()
        return link_code.code

    def link_character(self, code):
        # Check if character is already linked to an account
        character = self.link_code.character
        if character.confirmed:
            raise CharacterAlreadyLinked
        if self.link_code.code == code:
            self.update(push__characters=character)
            character.confirmed = True
            character.save()
            self.link_code = None
            self.save()
        else:
            raise InvalidLinkCode
        return character
