from ..lodestone_update import LodestoneUpdater

groups = ['admin', 'member']

servers = ['Aegis', 'Atomos', 'Carbuncle', 'Garuda', 'Gungnir', 'Kujata', 'Ramuh', 'Tonberry',
             'Typon', 'Unicorn',
             'Alexander', 'Bahamut', 'Durandal', 'Fenrir', 'Ifrit', 'Ridill', 'Tiamat', 'Ultima',
             'Valefor', 'Yojimbo', 'Zeromus',
             'Anima', 'Asura', 'Belias', 'Chocobo', 'Hades', 'Ixion', 'Mandragora', 'Masamune',
             'Pandaemonium', 'Shinryu', 'Titan',
             'Adamantoise', 'Balmung', 'Cactuar', 'Coeurl', 'Faerie', 'Gilgamesh', 'Goblin',
             'Jenova', 'Mateus', 'Midgardsormr', 'Sargatanas', 'Siren', 'Zalera',
             'Behemoth', 'Brynhildr', 'Diabolos', 'Excalibur', 'Exodus', 'Famfrit', 'Hyperion',
             'Lamia', 'Leviathan', 'Malboro', 'Ultros',
             'Cerberus', 'Lich', 'Moogle', 'Odin', 'Phoenix', 'Ragnarok', 'Shiva', 'Zodiark']

classes = ['Gladiator', 'Pugilist', 'Marauder', 'Lancer', 'Archer', 'Rogue', 'Conjurer',
             'Thaumaturge', 'Arcanist', 'Dark Knight', 'Machinist', 'Astrologian', 'Carpenter',
             'Blacksmith', 'Armorer', 'Goldsmith', 'Leatherworker', 'Weaver', 'Alchemist',
             'Culinarian', 'Miner', 'Botanist', 'Fisher']

war_classes = classes[0:6] + classes[9:11]
magic_classes = classes[6:9] + [classes[11]]
extra_classes = classes[9:12]
hand_classes = classes[12:20]
land_classes = classes[20:23]

grand_companies = ['Immortal Flames', 'Maelstrom', 'Order of the Twin Adder', 'No Affiliation']

races = ['Miqo\'te', 'Hyur', 'Elezen', 'Lalafell', 'Roegadyn', 'Au Ra']

genders = ['Male', 'Female']

update_service = LodestoneUpdater(delay=1)
