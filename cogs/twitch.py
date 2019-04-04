from discord.ext import commands
from string import ascii_letters
from random import choice
import discord
import re
import aiohttp

TWITCH_TOKEN = "ofgy2jmklm638s1bz6ncq5rt6gm14t"


class StreamsError(Exception):
    pass


class StreamNotFound(StreamsError):
    pass


class APIError(StreamsError):
    pass


class InvalidCredentials(StreamsError):
    pass


class OfflineStream(StreamsError):
    pass


class Twitch:
    """Set twitch stream alerts"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="twitch")
    async def twitch(self, ctx, stream: str):
        """Check is a stream is active"""

        regex = r'^(https?\:\/\/)?(www\.)?(twitch\.tv\/)'
        stream = re.sub(regex, '', stream)
        try:
            data = await self.fetch_twitch_ids(stream, raise_if_none=True)
            embed = await self.twitch_online(data[0]["_id"])
        except OfflineStream:
            await ctx.send(stream + " is offline.")
        except StreamNotFound:
            await ctx.send("That stream doesn't exist.")
        except APIError:
            await ctx.send("Error contacting the API.")
        except InvalidCredentials:
            await ctx.send("Owner: Client-ID is invalid or not set. "
                           "See `{}streamset twitchtoken`"
                           "".format(ctx.prefix))
        else:
            await ctx.send(embed=embed)

    async def fetch_twitch_ids(self, *streams, raise_if_none=False):
        def chunks(l):
            for i in range(0, len(l), 100):
                yield l[i:i + 100]

        base_url = "https://api.twitch.tv/kraken/users?login="
        header = {
            'Client-ID': TWITCH_TOKEN,
            'Accept': 'application/vnd.twitchtv.v5+json'
        }
        results = []

        for streams_list in chunks(streams):
            session = aiohttp.ClientSession()
            url = base_url + ",".join(streams_list)
            async with session.get(url, headers=header) as r:
                data = await r.json()
            if r.status == 200:
                results.extend(data["users"])
            elif r.status == 400:
                raise InvalidCredentials()
            else:
                raise APIError()
            await session.close()

        if not results and raise_if_none:
            raise StreamNotFound()

        return results

    async def twitch_online(self, stream):
        session = aiohttp.ClientSession()
        url = "https://api.twitch.tv/kraken/streams/" + stream
        header = {
            'Client-ID': TWITCH_TOKEN,
            'Accept': 'application/vnd.twitchtv.v5+json'
        }

        async with session.get(url, headers=header) as r:
            data = await r.json(encoding='utf-8')
        await session.close()
        if r.status == 200:
            if data["stream"] is None:
                raise OfflineStream()
            return self.twitch_embed(data)
        elif r.status == 400:
            raise InvalidCredentials()
        elif r.status == 404:
            raise StreamNotFound()
        else:
            raise APIError()

    def twitch_embed(self, data):
        channel = data["stream"]["channel"]
        url = channel["url"]
        logo = channel["logo"]
        if logo is None:
            logo = "https://static-cdn.jtvnw.net/jtv_u"
            + "ser_pictures/xarth/404_user_70x70.png"
        status = channel["status"]
        if not status:
            status = "Untitled broadcast"
        embed = discord.Embed(title=status, url=url)
        embed.set_author(name=channel["display_name"])
        embed.add_field(name="Followers", value=channel["followers"])
        embed.add_field(name="Total views", value=channel["views"])
        embed.set_thumbnail(url=logo)
        if data["stream"]["preview"]["medium"]:
            embed.set_image(url=data["stream"]["preview"]["medium"] +
                            self.rnd_attr())
        if channel["game"]:
            embed.set_footer(text="Playing: " + channel["game"])
        embed.color = 0x6441A4
        return embed

    def rnd_attr(self):
        """Avoids Discord's caching"""
        return "?rnd=" + "".join([choice(ascii_letters) for i in range(6)])


def setup(bot):
    bot.add_cog(Twitch(bot))
