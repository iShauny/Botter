import discord
from discord.ext import commands
from random import randint, choice
import aiohttp
import os


class Fun:
    """A list of commands for your entertainment"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    def __unload(self):
        self.session.close()

    @commands.command(name="choose")
    @commands.guild_only()
    async def choose(self, ctx, *choices):
        """Ask the bot to choose between several choices

        Use double quotes to denote multiple choices
        """

        if "@everyone" in choices or "@here" in choices:
            await ctx.send("No mass mentions sorry")
            return
        if len(choices) < 2:
            await ctx.send("Please provide more choices")
            return
        else:
            await ctx.send(choice(choices))

    @commands.command(name="randnum")
    @commands.guild_only()
    async def randnum(self, ctx, number: int = 100):
        """Roll a random number between 1 and x

        If x is not specified, defaults to 100
        """

        user = ctx.message.author
        if number < 1:
            await ctx.send("Please provide a number bigger than 1")
            return
        else:
            number = randint(1, number)
            await ctx.send("{0} The dice has rolled".format(user.mention) +
                           " and you got:" +
                           " :game_die: {0} :game_die:".format(number))

    @commands.command(name="dadjoke")
    @commands.guild_only()
    async def dadjoke(self, ctx):
        """Get a random dad joke"""

        api = 'https://icanhazdadjoke.com/'
        async with aiohttp.request(
                'GET', api, headers={'Accept': 'text/plain'}) as r:
            result = await r.text()
            await ctx.send('`' + result + '`')

    @commands.command(name="cat")
    @commands.guild_only()
    async def cat(self, ctx):
        """Get a random cat!"""

        url = "http://aws.random.cat/meow"

        async with self.session.get(url) as response:
            img_url = (await response.json())["file"]
            filename = os.path.basename(img_url)
            async with self.session.get(img_url) as image:
                file = discord.File(await image.read(), filename)
                await ctx.send(content=None, file=file)

    @commands.command(name="fox")
    async def fox(self, ctx):
        """Shows a random fox."""

        url = "http://wohlsoft.ru/images/foxybot/randomfox.php"
        async with self.session.get(url) as response:
            img_url = (await response.json())["file"]
            filename = os.path.basename(img_url)
            async with self.session.get(img_url) as image:
                file = discord.File(await image.read(), filename)
                await ctx.send(content=None, file=file)

    @commands.command(name="dog")
    async def dog(self, ctx):
        """Shows a random dog."""

        url = "http://random.dog/"
        async with self.session.get(url + "woof") as response:
            filename = (await response.text())
            async with self.session.get(url + filename) as image:
                file = discord.File(await image.read(), filename)
                await ctx.send(content=None, file=file)


def setup(bot):
    bot.add_cog(Fun(bot))
