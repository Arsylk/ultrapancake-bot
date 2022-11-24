import data
import views
import embeds

from discord import Color, Embed, Intents
from discord.ext import commands


import config

intents = Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents, command_prefix=config.command_prefix)


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


# direct bot commands
@bot.command()
async def skills(ctx, *query):
    query, lang = get_query_lang(' '.join(query or []))
    char = data.get(query, lang=lang)
    if char:
        await ctx.send(embed=embeds.char_embed(char, lang), view=views.CharView(char, lang))
    else:
        await ctx.send('Character not found!')


@bot.command()
async def search(ctx, *query):
    query, lang = get_query_lang(' '.join(query or []))
    found = data.search(query, lang=lang)
    if len(found) > 0:
        await ctx.send(embed=embeds.list_embed(query, found, 1, lang=lang), view=views.PaginationView())
    else:
        await ctx.send('No matches found!')


@bot.command()
async def buff(ctx, *query):
    query, lang = get_query_lang(' '.join(query or []))
    buff = data.buff(query, lang=lang)
    if buff:
        await ctx.send(embed=embeds.buff_embed(buff, lang))
    else:
        await ctx.send('Buff not found!')


@bot.command()
async def buffs(ctx, *query):
    query, lang = get_query_lang(' '.join(query or []))
    found = data.buffs(query, lang=lang)
    if len(found) > 0:
        await ctx.send(embed=embeds.buffs_embed(query, found, 1, lang=lang), view=views.PaginationView())
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


bot.run(token=config.token)
