import os

env_token_id = os.getenv("ID_TOKEN")
id = env_token_id[:env_token_id.index(":")]
token = env_token_id[env_token_id.index(":") + 1:]

command_prefix = '?'
reaction_ignite = '🔥'
reaction_prev, reaction_next = '⬅', '➡'
reaction_lang = {'kr': '🇰🇷', 'jp': '🇯🇵', 'en': '🇺🇸'}


skills = ['default', 'normal', 'slide', 'drive', 'leader']
colors = {
    'Water': (0, 204, 255),  # '#00ccff',
    'Fire': (239, 65, 18),  # '#ef4112',
    'Forest': (85, 255, 33),  # '#55ff21',
    'Light': (233, 214, 74),  # '#e9d64a',
    'Dark': (224, 15, 255),  # '#e00fff',
}
roles = {
    'None': '',
    'Attacker': '<:ATTACKER:310815634625658881>',
    'Defencer': '<:TANK:352113180111142914>',
    'Healer': '<:HEALER:310815634965528601>',
    'Balancer': '<:DEBUFFER:310815634910871553>',
    'Supporter': '<:SUPPORT:310815634936299521>',
    'Exp': '',
    'Upgrade': '',
    'Over Limit': '',
    'Max Exp': '',
}
attributes = {
    'Water': '<:watere:310815479294066690>',
    'Fire': '<:firee:310815479138615296>',
    'Forest': '<:foreste:310815479361044480>',
    'Light': '<:lighte:310815479688331264>',
    'Dark': '<:darke:310815479054860288>',
}

data_files = {
    'kr': 'data/CharacterDatabaseKr.json',
    'jp': 'data/CharacterDatabaseJp.json',
    'en': 'data/CharacterDatabaseEn.json',
}
langs = ['kr', 'jp', 'en']
icon_url = 'https://arsylk.pythonanywhere.com/static/icons/%s.png'


dump_files = {
    'kr': ['dump/SKILL_ACTIVE_DATA.json', 'dump/SKILL_BUFF_DATA.json'],
    'jp': [],
    'en': [],
}
