import unittest

from pychub.exceptions import InvalidLinkCode
from pychub.lodestone.LodestoneClient import LodestoneClient
from pychub.model.FreeCompany import FreeCompany, FreeCompanyEstate
import datetime
from mongoengine import *
from pychub.model.User import User, Character


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        self.db = connect('Test')

        # Drop collections
        FreeCompany.drop_collection()

        self.fc = FreeCompany()
        self.fc_data = dict(
            name='Nexus of Divinity', tag='neXus', lodestone_id='9228157111458889477',
            form_date=datetime.datetime.fromtimestamp(1409566643), active_members=33,
            rank=8, weekly_rank=56, monthly_rank=22,
            slogan='We are Nexus. Raid/Craft/Gather, '
                   'WE WANT IT ALL! We like to have fun, '
                   'but get shit done! Who wants to be '
                   'a smelly vegetable anyway?',
            focus=['Leveling', 'Hardcore', 'Dungeons', 'Trials', 'Raids'],
            seeking=['Tank', 'Healer', 'DPS', 'Crafter', 'Gatherer'],
            active='Always', recruiting=True,
        )
        estate_data = dict(
                        name='The Armament', address='Plot 19, 5 Ward', area='The Goblet', size='Medium',
                        greeting='Grab your weapons! Bryn first, '
                                 'then...... THE WORLD! Oh, and '
                                 'welcome and what not :D'
        )
        for key, value in self.fc_data.items():
            setattr(self.fc, key, value)
        self.fc.estate = FreeCompanyEstate()
        for key, value in estate_data.items():
            setattr(self.fc.estate, key, value)
        self.lodestoneClient = LodestoneClient()

    def tearDown(self):
        self.db.disconnect()

    def test_database_save_fc(self):  # TODO
        self.fc.members = self.lodestoneClient.get_fc_members(self.fc_data)
        self.fc.member_ranks = self.fc_data['member_ranks']
        try:
            fc = FreeCompany.objects.get(lodestone_id='9228157111458889477')
        except DoesNotExist:
            self.fc.save()
            fc = FreeCompany.objects.get(lodestone_id='9228157111458889477')
        self.assertEquals(fc.name, self.fc.name)
        self.assertEquals(fc.members, self.fc.members)


class TestUser(unittest.TestCase):
    def setUp(self):
        connect('Test')
        User.drop_collection()

    def test_user_set_password(self):
        user = User()
        user.username = 'TestUser'
        user.email = 'email@example.com'
        user.set_password('test')
        user.save()
        user = User.objects.get(username='TestUser')
        self.assertTrue(user.check_password('test'))

    def test_link_character(self):
        # Create user
        user = User()
        user.username = 'TestUser'
        user.email = 'email@exampl.com'
        user.set_password('test')
        user.save()
        code = user.get_link_code('Squish Twirly', 'Brynhildr')

        # Test for invalid link codes
        self.assertRaises(InvalidLinkCode, user.link_character, 'thisisinvalid')

        # Test that proper character was linked
        character = user.link_character(code)
        self.assertEquals(character.name, 'Squish Twirly')


class TestUtil(unittest.TestCase):
    def setUp(self):
        connect('Test')
        Character.drop_collection()
        self.lodestone = LodestoneClient()

    def test_character_from_dict(self):
        char = self.lodestone.get_character_data('7208613', True)
        char = Character.from_dict(char)
        char.save()
        char = Character.objects.get(lodestone_id='7208613')
        self.assertEquals(char.name, 'Squish Twirly')
