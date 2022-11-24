import config
import json
import re


# loading dump data
dump_data = {}
for lang, files in config.dump_files.items():
    dump_data[lang] = {}
    for file in files:
        with open(file, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
            dump_data[lang].update(data)

# loading character databases
character_database = {}
for lang, file in config.data_files.items():
    with open(file, 'r', encoding='utf-8') as fp:
        content = fp.read()
        content = re.sub(r'<color=ffffff>(.*?)</color>', r'`\1`', content)
        content = re.sub(r'<color=[a-f0-9]{6}>(.*?)</color>', r'\1', content)

        character_database[lang] = json.loads(content)
        character_database[lang] = sorted(character_database[lang], key=lambda char: char['grade'], reverse=True)
        character_database[lang] = dict((data['idx'], data) for data in character_database[lang])
        for idx in character_database[lang].keys():
            character_database[lang][idx]['skins'] = dict(character_database[lang][idx]['skins'])
aliases = {
    'glisa':     	'10200200',
    'dsl':       	'10200186',
    'gdk':       	'10200180',
    'sang':      	'10100116',
    'sang ah':   	'10100116',
    'leo':       	'10200227',
    'rusalka2':  	'10200285',
    'dana2':     	'10200233',
    'jcb':       	'10200144',
    'jcb2':      	'10200230',
    'bathory2':  	'10200222',
    'miku2':     	'10200183',
    'miku3':     	'10200232',
    'werewolf':  	'10200055',
    'warwolf2':  	'10200225',
    'werewolf2': 	'10200225',
    'maat2':     	'10200184',
    'mafdet2':   	'10200253',
    'mafgod':    	'10200253',
    'semele2':   	'10200273',
    'hildr2':    	'10200196',
    'mona2':     	'10200199',
    'mona3':     	'10200219',
    'medb2':     	'10200220',
    'ruin2':     	'10200237',
    'sang2':     	'10200180',
    'sitri2':    	'10200202',
    'sitri3':    	'10200270',
    'eshu2':     	'10200265',
    'saturn2':   	'10200274',
    'nirrti2':   	'10200288',
    'aurora2':   	'10200297',
    'loki':      	'10200340',
    'metis2':    	'10200306',
    'kubaba2':   	'10200338',
    'dmars':   		'10200176',
    'dmaat':   		'10200184',
    'ddavi':   		'10200215',
    'eve':   		'10100093',
    'eve2':   		'10200223',
    'moa2':   		'10200211',
    'ruin':   		'10200135',
    'slime king':   '20100124',
    'leda2':   		'10200268',
    'arhat2':   	'10200300',
    'dmars2':   	'10200309',
    'aria2':   		'10200307',
    'saturn3':   	'10200313',
    'neptune2':   	'10200308',
    'venus2':   	'10200310',
    'eve3':   		'10200299',
    'ziva2':   		'10200304',
    'seth':   		'10200262',
    'seth2':   		'10200259',
    'botan2':   	'10200349',
    'bari2':   		'10200355',
}


# methods for char data retrieving
def has(idx, lang='kr'):
    return idx in character_database[lang]


def get(query, ignited=False, lang='kr'):
    query, character, exact = query.lower(), None, False
    if query.startswith('!'):
        query, exact = query[1:], True
    if query in aliases.keys():
        query = aliases[query]

    if query not in character_database[lang]:
        for char in character_database[lang].values():
            if (query in char['name'].lower() and not exact) or query == char['name'].lower():
                character = char
                break
            if True in [(query in view_idx.lower() and not exact) or query == view_idx.lower() for view_idx in char['skins'].keys()]:
                character = char
                break
            if True in [(query in skin.lower() and not exact) or query == skin.lower() for skin in char['skins'].values()]:
                character = char
                break
    else:
        character = character_database[lang][query]
    if character and isinstance(character, dict):
        character['ignited'], character['lang'] = ignited, lang
    return character


def search(query, lang='kr'):
    query, characters = query.lower(), []
    for char in character_database[lang].values():
        if query == char['idx']:
            characters.append(char)
            continue
        if query in char['name'].lower():
            characters.append(char)
            continue
        if True in [query in view_idx.lower() for view_idx in char['skins'].keys()]:
            characters.append(char)
            continue
        if True in [query in skin.lower() for skin in char['skins'].values()]:
            characters.append(char)
            continue
    return [char_short(char) for char in characters]


def buff(query, lang='kr'):
    query = query.lower()
    for char in character_database[lang].values():
        for skill in list(char['skills'].values()) + list(char['skills_ignited'].values() if len(char['skills_ignited']) > 0 else []):
            if 'buffs' in skill and isinstance(skill['buffs'], dict):
                for buff in skill['buffs'].values():
                    if query == buff['idx'] or query == buff['logic'].lower() or query == buff['name'].lower():
                        return buff
    return None


def buffs(query, lang='kr'):
    query, idxes, characters = query.lower(), [], []
    for char in character_database[lang].values():
        for skill in list(char['skills'].values()) + list(char['skills_ignited'].values() if len(char['skills_ignited']) > 0 else []):
            if 'buffs' in skill and isinstance(skill['buffs'], dict):
                for buff in skill['buffs'].values():
                    if query == buff['idx'] or query == buff['logic'].lower() or query == buff['name'].lower():
                        if char['idx'] not in idxes:
                            idxes.append(char['idx'])
                            characters.append(char)
    return [char_short(char) for char in characters]


def dump(idx, lang='kr'):
    return dump_data[lang][idx] if idx in dump_data[lang] else None


# various static formatters for char data
def char_title(char):
    name, skin = '(%s)' % char['name'] if char['lang'] == 'kr' else '', char_skin(char)
    skinname, role = char['skins'][skin], config.roles[char['role']]
    flag = config.reaction_lang[char['lang']]

    return '%s %s %s %s' % (flag, skinname, name, role)


def char_description(char):
    view_idx = sorted([key for key in char['skins'].keys() if key[-3:] != '_00'], key=lambda key: key[-2:])
    names = [char['skins'][key] for key in view_idx]

    return '%s\nview_idx: %s' % (', '.join(names), ', '.join(view_idx))


def char_skin(char):
    skins = list(char['skins'].keys())
    skins.sort(key=lambda key: len(key))
    if len(skins) > 0:
        skin = skins[0]
        if skin[:-3]+'_02' in skins:
            return skin[:-3]+'_02'
        if skin[:-3]+'_01' in skins:
            return skin[:-3] + '_01'
        return skin
    return None


def char_icon(char):
    skin = char_skin(char)
    if skin:
        return config.icon_url % skin
    return None


def char_skill_fields(char):
    ignite = (char['ignited'] and len(char['skills_ignited']) > 0)
    skills_key = 'skills_ignited' if ignite else 'skills'
    name_format = (config.reaction_ignite + ' %s Skill - %s ' + config.reaction_ignite) if ignite else '%s Skill - %s'

    fields = []
    for skill in config.skills:
        text = char[skills_key][skill]['text'].replace('\\', '\n')
        # for buff in char[skills_key][skill]['buffs']:
        #     buff = char[skills_key][skill]['buffs'][buff]
        #     text = text.replace('%s ' % buff['name'], '`%s` ' % buff['name'])
        fields.append(dict(name=name_format % (skill.capitalize(), char[skills_key][skill]['idx']), value=text, inline=False))

    return fields


def char_short(char):
    idx = char['idx']
    grade, attribute, role = char['grade'], char['attribute'], char['role']
    skin = char_skin(char) or ''
    skinname = char['skins'][skin] if skin in char['skins'] else ''
    role_icon = config.roles[role] if role in config.roles and len(config.roles[role]) > 0 else role
    attribute_icon = config.attributes[attribute] if attribute in config.attributes and len(config.attributes[attribute]) > 0 else attribute

    return '`%s` - %s - %s - %s* %s %s' % (idx, skinname, skin[:-3], grade, attribute_icon, role_icon)


def char_raw(char):
    key_order = [
        'idx', 'name', 'attribute', 'role', 'grade', 'status', 'skins', 'skills', 'skills_ignited',
        'hp', 'def', 'atk', 'cri', 'agi',
        'default', 'normal', 'slide', 'drive', 'leader',
        'text', 'buffs', 'logic', 'icon'
    ]

    def my_print(lines, data, depth=0):
        for key in sorted(data.keys() if isinstance(data, dict) else data, key=lambda key: key_order.index(key) if key in key_order else len(key_order)):
            lines.append('%s%s' % ('\t' * depth, key))
            if isinstance(data, dict):
                lines[-1] = '%s:' % lines[-1]
                if isinstance(data[key], dict) or isinstance(data[key], list):
                    lines = my_print(lines, data[key], depth + 1)
                else:
                    lines[-1] = '%s %s' % (lines[-1], data[key])
        return lines

    lines = []
    lines = my_print(lines, char)

    return '\n'.join(lines)


# various static formatters for buff data
def buff_title(buff):
    return buff['name']


def buff_description(buff):
    categories = ('categories: %s' % ', '.join(['`%s`' % value for value in buff['categories'].values()])) if 'categories' in buff and len(buff['categories']) > 0 and isinstance(buff['categories'], dict) else ''

    return '%s\n\nidx: `%s`\nlogic: `%s`\n%s' % (buff['text'], buff['idx'], buff['logic'], categories)


def buff_icon(buff):
    return config.icon_url % ('buff/' + buff['idx'])
