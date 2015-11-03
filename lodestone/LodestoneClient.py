from configparser import ConfigParser

from urllib import request
from urllib.error import HTTPError

from bs4 import BeautifulSoup
from datetime import datetime
import math


class LodestoneClient:
    HTML_PARSER = 'html.parser'

    def __init__(self):
        self.config = ConfigParser()
        self.config.read('config/config.ini')
        self.config = self.config['lodestoneClient']
        self.lodestoneUrl = self.config['lodestoneUrl']

    def get_fc_by_id(self, lodestoneid):
        free_company = {'estate': {}}
        data = request.urlopen('{0}/freecompany/{1}'.format(self.lodestoneUrl, lodestoneid)).read()
        page = BeautifulSoup(data, LodestoneClient.HTML_PARSER)
        free_company['lodestone_id'] = lodestoneid
        free_company['name'] = page.select(self.config['selector.fc.name'], limit=1)[0].text
        free_company['tag'] = page.select(self.config['selector.fc.tag'], limit=1)[0].text.split('«')[1][0:-1]
        free_company['form_date'] = datetime.fromtimestamp(int(
            page.select(self.config['selector.fc.form_date'], limit=1)[0].text.split(',')[0][-10:]))
        free_company['active_members'] = int(page.select(self.config['selector.fc.active_members'], limit=1)[0].text)
        free_company['rank'] = int(page.select(self.config['selector.fc.rank'], limit=1)[0].text.strip())
        tmp = page.select(self.config['selector.fc.ranking'], limit=1)[0].text
        free_company['weekly_rank'], free_company['monthly_rank'] = [int(s) for s in tmp.split() if s.isdigit()]
        free_company['slogan'] = page.select(self.config['selector.fc.slogan'], limit=1)[0].text.strip()
        free_company['focus'] = [node.img['title'] for node in page.select(self.config['selector.fc.focus']) if
                                 'class' not in node.attrs]
        free_company['seeking'] = [node.img['title'] for node in page.select(self.config['selector.fc.seeking']) if
                                   'class' not in node.attrs]
        free_company['active'] = page.select(self.config['selector.fc.active'], limit=1)[0].text.strip()
        free_company['recruiting'] = page.select(self.config['selector.fc.recruitment'], limit=1)[
                                         0].text.strip() == 'Open'
        tmp = page.select(self.config['selector.fc.estate'], limit=1)[0].text.strip().split('\n')
        tmp_a = tmp[2].split(',')
        free_company['estate']['name'] = tmp[0]
        free_company['estate']['address'] = tmp_a[0] + ',' + tmp_a[1]
        free_company['estate']['area'] = tmp_a[2].split('(')[0].strip()
        free_company['estate']['size'] = tmp_a[2].split('(')[1][:-1]
        free_company['estate']['greeting'] = tmp[4]
        print(free_company)
        return free_company

    def get_fc_members(self, free_company):
        members = {}
        for page_num in range(0, math.ceil(free_company['active_members'] / 50)):  # 50 per page
            data = request.urlopen(
                '{0}/freecompany/{1}/member/?page={2}'.format(self.lodestoneUrl, free_company['lodestone_id'],
                                                              page_num))
            page = BeautifulSoup(data, LodestoneClient.HTML_PARSER)
            free_company['member_ranks'] = []
            last_member_rank = None
            for node in page.select(self.config['selector.member']):
                name_node = node.select(self.config['selector.member.name'], limit=1)[0]
                name = name_node.text
                members[name] = {}
                members[name]['name'] = name_node.text
                members[name]['lodestone_id'] = name_node['href'].split('/')[3]
                members[name]['server'] = node.select(self.config['selector.member.server'], limit=1)[0].text[2:-1]
                members[name]['rank'] = node.select(self.config['selector.member.rank'], limit=1)[0].text.strip()
                if last_member_rank != members[name]['rank']:
                    last_member_rank = members[name]['rank']
                    free_company['member_ranks'].append(last_member_rank)
        free_company['members'] = members
        return members

    def get_character_data(self, lodestone_id, achievements=False):
        data = request.urlopen('{0}/character/{1}'.format(self.lodestoneUrl, lodestone_id))
        page = BeautifulSoup(data, LodestoneClient.HTML_PARSER)
        # noinspection PyDictCreation
        character = {}
        character['lodestone_id'] = lodestone_id
        character['name'] = page.select_one(self.config['selector.character.name']).text
        character['server'] = page.select_one(self.config['selector.character.server']).text.strip() \
            .replace('(', '').replace(')', '')
        character['free_company'] = \
        page.select(self.config['selector.character.free_company'])[0].attrs['href'].split('/')[3]
        character['lodestone_profile'] = page.select_one(self.config['selector.character.profile']).text.strip()
        tmp = page.select_one(self.config['selector.character.race']).text.strip().split(' / ')
        character['race'] = tmp[0]

        character['gender'] = 'Male' if tmp[2] == '♂' else 'Female'
        tmp = page.select(self.config['selector.character.main'])
        character['nameday'] = tmp[0].text
        character['guardian'] = tmp[1].text
        character['city_state'] = tmp[2].text
        character['grand_company'] = tmp[3].text.split('/')[0]
        character['grand_company_rank'] = tmp[3].text.split('/')[1]
        character['mounts'] = [node.attrs['title'] for node in
                               page.select(self.config['selector.character.mounts'])[0].findAll('a')
                               if 'title' in node.attrs]
        character['minions'] = [node.attrs['title'] for node in
                                page.select(self.config['selector.character.mounts'])[1].findAll('a')
                                if 'title' in node.attrs]

        character['classes'] = []
        tmp = []
        for d in page.select(self.config['selector.character.classes']):
            if not d.text:
                continue
            tmp.append(d.text)
        for i in range(0, len(tmp), 3):
            if '-' in tmp[i + 1]:
                continue
            exp = tmp[i + 2].split(' / ')
            character['classes'].append({
                'name': tmp[i], 'level': int(tmp[i + 1]), 'current_exp': int(exp[0]), 'next_exp': int(exp[1])
            })
        if achievements:
            character['recent_achievements'] = self.get_character_achievements(lodestone_id)
        return character

    def get_character_achievements(self, lodestone_id):
        try:
            data = request.urlopen("{0}/character/{1}/achievement".format(self.lodestoneUrl, lodestone_id))
            page = BeautifulSoup(data, LodestoneClient.HTML_PARSER)
        except HTTPError:  # TODO Logging
            return []
        achievements = []
        for node in page.select(self.config['selector.character.achievements']):
            # noinspection PyDictCreation
            a = {}
            a['date'] = datetime.fromtimestamp(int(node.find('script').text.split(',')[0][-10:]))
            a['type'] = ' '.join(node.find(attrs={'class': 'achievement_txt'}).contents[2].strip().replace(" \"", "").split(" ")[:-1])
            a['name'] = node.find(attrs={'class': 'achievement_txt'}).contents[3].text
            a['text'] = a['type'] + ' achievement \"' + a['name'] + "\" earned!"
            achievements.append(a)
        return achievements
