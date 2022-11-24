from discord import Client, Color, Embed, Member
from discord.ext import commands
from math import ceil
import config
import data


client, bot = Client(), commands.Bot(command_prefix=config.command_prefix)


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


def get_query_lang(query):
    lang = 'kr'
    for l in config.langs:
        tag = 'lang=%s' % l
        if tag in query:
            query, lang = query.replace(tag, '').strip(), l
    return query, lang


@bot.event
async def on_ready():
    print('Logged in as:', bot.user.name, bot.user.id)


@bot.event
async def on_message(message):
    if message.author.id == config.id:
        if len(message.content) == 0 and len(message.embeds) > 0:
            if isinstance(message.embeds[0].footer.text, str):
                values = dict(part.split('=') for part in filter(lambda key: len(key) > 0, message.embeds[0].footer.text.split('&')))
                tag, lang, idx = values.get('tag', None), values.get('lang', 'kr'), values.get('idx', None)

                # modify char
                if tag == 'char' and idx:
                    # add ignition reaction
                    if data.has(idx, lang) and len(data.get(idx, lang=lang)['skills_ignited']) > 0:
                        await message.add_reaction(config.reaction_ignite)

                    # add region flag reactions
                    # if data.has(idx, 'kr') and data.has(idx, 'en'):
                    #     await message.add_reaction(config.reaction_lang['kr'])
                    #     await message.add_reaction(config.reaction_lang['en'])
                    if sum([data.has(idx, l) for l in config.langs]) > 0:
                        for l in config.langs:
                            if data.has(idx, l):
                                await message.add_reaction(config.reaction_lang[l])

                # modify list & buffs
                if tag == 'list' or tag == 'buffs':
                    # add prev page reaction
                    await message.add_reaction(config.reaction_prev)
                    # add next page reaction
                    await message.add_reaction(config.reaction_next)

    await bot.process_commands(message)


@bot.event
async def on_reaction_add(reaction, user):
    emoticon, message = str(reaction), reaction.message
    if user.id != config.id and message.author.id == config.id:
        if len(message.content) == 0 and len(message.embeds) > 0:
            if isinstance(message.embeds[0].footer.text, str):
                values = dict(part.split('=') for part in filter(lambda key: len(key) > 0, message.embeds[0].footer.text.split('&')))
                tag, lang, idx = values.get('tag', None), values.get('lang', 'kr'), values.get('idx', None)

                # modify char
                if tag == 'char' and idx:
                    # toggle ignite
                    if emoticon == config.reaction_ignite:
                        await message.edit(embed=char_embed(data.get(idx, True, lang=lang), lang=lang))

                    # toggle region flags
                    # if emoticon == config.reaction_lang['kr']:
                    #     await message.edit(embed=char_embed(data.get(values.get('idx'), False, lang='kr'), lang='kr'))
                    # if emoticon == config.reaction_lang['en']:
                    #     await message.edit(embed=char_embed(data.get(values.get('idx'), False, lang='en'), lang='en'))
                    for l in config.langs:
                        if emoticon == config.reaction_lang[l]:
                            await message.edit(embed=char_embed(data.get(values.get('idx'), False, lang=l), lang=l))

                # modify list & buffs
                if tag == 'list' or tag == 'buffs':
                    # page prev
                    if emoticon == config.reaction_prev:
                        query, page = values.get('query', ''), int(values.get('page', 1)) - 1
                        if tag == 'list':
                            found = data.search(query, lang=lang)
                            await message.edit(embed=list_embed(query, found, page, lang=lang))
                        elif tag == 'buffs':
                            found = data.buffs(query, lang=lang)
                            await message.edit(embed=buffs_embed(query, found, page, lang=lang))
                    # page next
                    if emoticon == config.reaction_next:
                        query, page = values.get('query', ''), int(values.get('page', 1)) + 1
                        if tag == 'list':
                            found = data.search(query, lang=lang)
                            await message.edit(embed=list_embed(query, found, page, lang=lang))
                        elif tag == 'buffs':
                            found = data.buffs(query, lang=lang)
                            await message.edit(embed=buffs_embed(query, found, page, lang=lang))


@bot.event
async def on_reaction_remove(reaction, user):
    emoticon, message = str(reaction), reaction.message
    if user.id != config.id and message.author.id == config.id:
        if len(message.content) == 0 and len(message.embeds) > 0:
            if isinstance(message.embeds[0].footer.text, str):
                values = dict(part.split('=') for part in filter(lambda key: len(key) > 0, message.embeds[0].footer.text.split('&')))
                tag, lang, idx = values.get('tag', None), values.get('lang', 'kr'), values.get('idx', None)

                # modify char
                if tag == 'char' and idx:
                    # toggle ignite
                    if emoticon == config.reaction_ignite:
                        await message.edit(embed=char_embed(data.get(idx, False, lang=lang), lang=lang))


# direct bot commands
@bot.command()
async def skills(ctx, *query):
    query, lang = get_query_lang(' '.join(query or []))
    char = data.get(query, lang=lang)
    if char:
        await ctx.send(embed=char_embed(char, lang))
    else:
        await ctx.send('Character not found!')


@bot.command()
async def search(ctx, *query):
    query, lang = get_query_lang(' '.join(query or []))
    found = data.search(query, lang=lang)
    if len(found) > 0:
        await ctx.send(embed=list_embed(query, found, 1, lang=lang))
    else:
        await ctx.send('No matches found!')


@bot.command()
async def buff(ctx, *query):
    query, lang = get_query_lang(' '.join(query or []))
    buff = data.buff(query, lang=lang)
    if buff:
        await ctx.send(embed=buff_embed(buff, lang))
    else:
        await ctx.send('Buff not found!')


@bot.command()
async def buffs(ctx, *query):
    query, lang = get_query_lang(' '.join(query or []))
    found = data.buffs(query, lang=lang)
    if len(found) > 0:
        await ctx.send(embed=buffs_embed(query, found, 1, lang=lang))
    else:
        await ctx.send('No matches found!')


@bot.command()
async def raw(ctx, *query):
    query, lang = get_query_lang(' '.join(query or []))
    selected_skills, ignited = [], False

    for skill in config.skills:
        tag = 'skill=%s' % skill
        if tag in query:
            selected_skills.append(skill)
            query = query.replace(tag, '').strip()
    if 'ignite' in query or 'ignited' in query:
        ignited = True
        query = query.replace('ignite', '').strip().replace('ignited', '').strip()

    char = data.get(query, lang=lang)
    if char:
        just_char = dict((key, val) for key, val in char.items() if key != 'skills' and key != 'skills_ignited')
        await ctx.author.send('```\n%s\n```' % data.char_raw(just_char))

        for skill in selected_skills:
            just_skill = char['skills' if not ignited else 'skills_ignited']
            just_skill = just_skill[skill] if skill in just_skill else {}
            just_skill['ignited'] = ignited

            await ctx.author.send('```\n%s\n```' % data.char_raw({skill: dict((key, val if key != 'text' else val.split('\\')) for key, val in just_skill.items())}))
    else:
        await ctx.author.send('Character not found!')


@bot.command()
async def dump(ctx, *query):
    query, lang = get_query_lang(' '.join(query or []))
    dump = data.dump(query, lang=lang)
    if dump:
        await ctx.author.send('```\n%s\n```' % data.char_raw(dump))
    else:
        await ctx.author.send('Dump data not found!')


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


bot.run(config.token)
