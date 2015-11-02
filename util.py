from pychub import FreeCompany
from pychub.model.FreeCompany import FreeCompanyEstate


def fc_from_dict(fc_dict):
    fc = FreeCompany()

    for key, value in fc_dict.items():
        fc.__setattr__(key, value)

    if 'estate' in fc_dict:
        estate = FreeCompanyEstate()
        for key, value in fc_dict['estate'].items():
            estate.__setattr__(key, value)
        fc.estate = estate
    return fc
