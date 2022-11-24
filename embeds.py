from math import ceil
from discord import Color, Embed
import data
import config


def char_embed(char, lang):
    embed = Embed(
        title=data.char_title(char),
        description=data.char_description(char),
        color=Color.from_rgb(*config.colors[char['attribute']]),
    )
    embed.set_thumbnail(url=data.char_icon(char))
    embed.set_footer(text='&tag=char&lang=%s&idx=%s' % (lang, char['idx']), icon_url='')
    for field in data.char_skill_fields(char):
        embed.add_field(**field)

    return embed


def list_embed(query, found, page, lang):
    limit = int(ceil(len(found) / 20))
    page = min(max(1, int(page)), limit)
    embed = Embed(
        title='%s Page `%s`-`%s`' % (('Search `%s`,' % query if query else ''), page, limit),
        description='\n'.join(found[(page - 1) * 20:page * 20])
    )
    embed.set_footer(text='&tag=list&lang=%s&page=%d&query=%s' % (lang, page, query), icon_url='')
    return embed


def buff_embed(buff, lang):
    embed = Embed(
        title=data.buff_title(buff),
        description=data.buff_description(buff),
    )
    embed.set_thumbnail(url=data.buff_icon(buff))
    return embed


def buffs_embed(query, found, page, lang):
    limit = int(ceil(len(found) / 20))
    page = min(max(1, int(page)), limit)
    embed = Embed(
        title='%s Page `%s`-`%s`' % (('Search `%s`,' % query if query else ''), page, limit),
        description='\n'.join(found[(page - 1) * 20:page * 20])
    )
    embed.set_footer(text='&tag=buffs&lang=%s&page=%d&query=%s' % (lang, page, query), icon_url='')
    return embed