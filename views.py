import config
import discord
import data
import embeds


def parse_message(message: discord.Message):
    if len(message.content) == 0 and len(message.embeds) > 0:
        text = message.embeds[0].footer.text
        if isinstance(text, str):
            values = dict(part.split('=') for part in filter(lambda key: len(key) > 0, text.split('&')))
            values['lang'] = values.get('lang', 'kr')
            return values
    return dict()


class IgniteButtonView(discord.ui.Button):
    def __init__(self, parent):
        super().__init__(custom_id='ignite', emoji=config.reaction_ignite)
        self.parent = parent

    async def callback(self, interaction: discord.Interaction):
        ignited = not self.parent.is_ignited
        msg = parse_message(interaction.message)
        idx, lang = msg.get('idx'), msg.get('lang')
        if idx and lang:
            embed = embeds.char_embed(data.get(idx, ignited, lang=lang), lang=lang)
            await interaction.response.edit_message(embed=embed)
            self.parent.is_ignited = ignited
        else:
            await interaction.response.defer()


class LanguageButtonView(discord.ui.Button):
    def __init__(self, parent, lang: str):
        super().__init__(custom_id='language_%s' % lang, emoji=config.reaction_lang[lang])
        self.parent = parent
        self.lang = lang

    async def callback(self, interaction: discord.Interaction):
        lang = self.lang
        msg = parse_message(interaction.message)
        idx, current_lang = msg.get('idx'), msg.get('lang')
        if idx and current_lang and lang != current_lang:
            embed = embeds.char_embed(data.get(idx, ignited=False, lang=lang), lang=lang)
            await interaction.response.edit_message(embed=embed)
            self.parent.is_ignited = False
        else:
            await interaction.response.defer()


class CharView(discord.ui.View):
    def __init__(self, char: dict, lang: str):
        super().__init__(timeout=None)
        self.is_ignited = False
        self.char = char
        self.lang = lang

        idx = char['idx']
        if len(char['skills_ignited']) > 0:
            self.add_item(IgniteButtonView(self))

        has_lang = [l for l in config.langs if data.has(idx, l)]
        if len(has_lang) > 1:
            for l in has_lang:
                self.add_item(LanguageButtonView(self, lang=l))


class PaginationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(emoji=config.reaction_prev)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.run(interaction, -1)

    @discord.ui.button(emoji=config.reaction_next)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.run(interaction, +1)

    async def run(self, interaction: discord.Interaction, change: int):
        msg = parse_message(interaction.message)
        tag, query, page = msg.get('tag'), msg.get('query', ''), int(msg.get('page', 1)) + change
        lang = msg.get('lang')

        embed = None
        if tag == 'list':
            found = data.search(query, lang=lang)
            embed = embeds.list_embed(query, found, page, lang=lang)
        elif tag == 'buffs':
            found = data.buffs(query, lang=lang)
            embed = embeds.buffs_embed(query, found, page, lang=lang)

        if embed:
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.defer()
