from pprint import pprint
import unittest
from datetime import datetime

from pychub.lodestone.LodestoneClient import LodestoneClient


class LodestoneClientTest(unittest.TestCase):
    def setUp(self):
        self.lodestoneClient = LodestoneClient()
        self.fc_compare = dict(
            name='Nexus of Divinity', tag='neXus', lodestone_id='9228157111458889477',
            form_date=datetime.fromtimestamp(1409566643), active_members=16,
            rank=8, weekly_rank=24, monthly_rank=62,
            slogan='We are Nexus. Raid/Craft/Gather, '
                   'WE WANT IT ALL! We like to have fun, '
                   'but get shit done! Who wants to be '
                   'a smelly vegetable anyway?',
            focus=['Leveling', 'Casual', 'Hardcore', 'Dungeons', 'Trials', 'Raids'],
            seeking=['Tank', 'Healer', 'DPS', 'Crafter', 'Gatherer'],
            active='Always', recruiting=True,
            estate=dict(name='The Armament', address='Plot 19, 5 Ward', area='The Goblet', size='Medium',
                        greeting='Grab your weapons! Bryn first, '
                                 'then...... THE WORLD! Oh, and '
                                 'welcome and what not :D')
        )

    def test_init(self):
        config = self.lodestoneClient.config
        assert config is not None
        assert config['lodestoneUrl'] == 'http://na.finalfantasyxiv.com/lodestone'

    # TODO Tests on dynamic data is probably a bad idea.
    def test_get_fc_by_id(self):
        free_company = self.lodestoneClient.get_fc_by_id('9228157111458889477')
        #pprint("FC Data: {0}".format(free_company))
        print(free_company['form_date'])
        for key, value in self.fc_compare.items():
            self.assertEqual(free_company[key], value,
                             "Unexpected value for data key {0}\n Got: {1}\nExpected: {2}".format(
                                 key, free_company[key], value
                             ))

    def test_get_fc_members(self):
        members = self.lodestoneClient.get_fc_members(self.fc_compare)
        self.assertEqual(members['Hydryn Sole']['name'], 'Hydryn Sole')
        self.assertEqual(members['Hydryn Sole']['server'], 'Brynhildr')
        self.assertEqual(len(members), self.fc_compare['active_members'])

    def test_get_character_data(self):
        character = self.lodestoneClient.get_character_data('7208613')
        self.assertEqual(character['name'], 'Squish Twirly')
        self.assertTrue('Company Chocobo' in character['mounts'])
        self.assertTrue('Pudgy Puk' in character['minions'])
        self.assertEqual(character['server'], 'Brynhildr')
        self.assertTrue(len(character['classes']) > 0)

    def test_get_character_achievements(self):
        achievements = self.lodestoneClient.get_character_achievements('7208613')
        print(achievements)
        self.assertTrue(len(achievements) > 0)
