from datetime import datetime

from mongoengine import *

from ..lodestone_update import Updateable
from ..lodestone.client import LodestoneClient


class FreeCompanyEstate(EmbeddedDocument):
    name = StringField(required=True)
    address = StringField(required=True)
    area = StringField(required=True)
    size = StringField(required=True)
    greeting = StringField(required=True)


class FreeCompany(Document, Updateable):
    lodestone_id = StringField(required=True, unique=True)
    name = StringField(required=True)
    tag = StringField(required=True)
    form_date = DateTimeField(required=True)
    active_members = IntField(required=True)
    rank = IntField(required=True)
    weekly_rank = IntField(required=True)
    monthly_rank = IntField(required=True)
    slogan = StringField(required=True)
    focus = ListField(StringField(), required=True)
    seeking = ListField(StringField(), required=True)
    active = StringField(required=True)
    recruiting = BooleanField(required=True)
    estate = EmbeddedDocumentField(FreeCompanyEstate)
    members = DictField(required=True)
    member_ranks = ListField(StringField(), required=True)
    last_update = DateTimeField()

    meta = {
        'index_drop_dups': True,
        'indexes': [
            {'fields': ['lodestone_id'],
             'unique': True}
        ]
    }

    @property
    def sorted_member_list(self): # TODO Additional sorting by name might be nice.
        members = []
        for rank in self.member_ranks:
            for data in self.members.values():
                if data['rank'] == rank:
                    members.append(data)
        return members

    def update_lodestone_data(self, lodestone: LodestoneClient, members=True):
        fc_dict = lodestone.get_fc_by_id(self.lodestone_id)
        fc_dict['members'] = lodestone.get_fc_members(fc_dict)

        for key, value in fc_dict.items():
            setattr(self, key, value)

        if 'estate' in fc_dict:
            estate = FreeCompanyEstate()
            for key, value in fc_dict['estate'].items():
                setattr(estate, key, value)
            self.estate = estate

        self.last_update = datetime.utcnow()
        self.save()
