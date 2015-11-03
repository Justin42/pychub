from mongoengine import DoesNotExist

from model.User import Character, ClassData, AchievementInfo
from model.FreeCompany import FreeCompany, FreeCompanyEstate


def fc_from_dict(fc_dict):
    fc = FreeCompany()

    for key, value in fc_dict.items():
        setattr(fc, key, value)

    if 'estate' in fc_dict:
        estate = FreeCompanyEstate()
        for key, value in fc_dict['estate'].items():
            setattr(estate, key, value)
        fc.estate = estate
    return fc


def character_from_dict(char_dict):
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
