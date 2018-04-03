import discord
from discord.ext import commands
import xml.etree.ElementTree as ET
from random import choice
import aiohttp


class TooManyTagsError(Exception):
    pass


userAgent = {"User-Agent": "Toothy V2"}

MAX_FILTERS = 10


class Lewd:
    """Recieve lewd pictures from both E621 and Rule34"""

    def __init__(self, bot: commands.Bot):

        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    def __unload(self):
        self.session.close()

    @commands.group(name="lewdset")
    @commands.has_permissions(manage_guild=True)
    async def lewdset(self, ctx):
        guild = ctx.guild
        guild_settings = await self.bot.database.get(guild, self)
        if not guild_settings:
            await self.bot.database.set(guild, {
                "e621_enabled": True,
                "rule34_enabled": True
            }, self)
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @lewdset.command(usage="<rule34 or e621>", name="toggle")
    @commands.has_permissions(manage_guild=True)
    async def toggle(self, ctx, site_name):
        guild = ctx.guild
        guild_data = await self.bot.database.get(guild, self)
        is_rule34_enabled = guild_data.get("rule34_enabled")
        is_e621_enabled = guild_data.get("e621_enabled")
        site_name = site_name.lower()

        if site_name == "rule34":
            if is_rule34_enabled:
                await self.bot.database.set(guild, {"rule34_enabled": False},
                                            self)
                await ctx.send('Rule34 Disabled')
                return
            else:
                await self.bot.database.set(guild, {"rule34_enabled": True},
                                            self)
                await ctx.send('Rule34 Enabled')
                return
        if site_name == "e621":
            if is_e621_enabled:
                await self.bot.database.set(guild, {"e621_enabled": False},
                                            self)
                await ctx.send("E621 Disabled")
                return
            else:
                await self.bot.database.set(guild, {"e621_enabled": True},
                                            self)
                await ctx.send("E621 Enabled")
                return
        else:
            await self.bot.send_cmd_help(ctx)

    @lewdset.command(name="channel")
    @commands.has_permissions(manage_channels=True)
    async def channel(self, ctx, mode):
        """Sets channel mode.

        Off - disables NSFW commands
        On - enable NSFW commands"""

        channel = ctx.message.channel
        allowed_responses = ["off", "on"]

        chosen_mode = mode.lower()
        if chosen_mode not in allowed_responses:
            await self.bot.send_cmd_help(ctx)
            return
        await self.bot.database.set(channel, {"mode": chosen_mode}, self)
        await channel.send(
                           '{0.mention} is now set to {1} mode!'.format(
                               channel, chosen_mode))

    @lewdset.group(name="personal_filter")
    async def personal_filter(self, ctx):
        """Personal Filter Management"""
        if ctx.invoked_subcommand is None or isinstance(
                ctx.invoked_subcommand, commands.Group):
            await self.bot.send_cmd_help(ctx)
            return

    @personal_filter.command(name="add")
    async def pf_add(self, ctx, *tags):
        """Add tags to the personal filter. Seperate with a space"""

        user = ctx.message.author
        channel = ctx.message.channel
        added = False

        if not tags:
            await self.bot.send_cmd_help(ctx)
            return

        user_data = await self.bot.database.get(user, self)
        user_tags = user_data.get("filtered_tags", [])

        if not user_tags:
            await self.bot.database.set(user, {"filtered_tags": []}, self)

        if len(tags) + len(user_tags) > MAX_FILTERS:
            await channel.send('Woah! Too many tags in your filter!')
            return
        for tag in tags:
            if tag.lower() not in user_tags:
                user_tags.append(tag.lower())
                added = True
        if added:
            await self.bot.database.set(user, {"filtered_tags": user_tags},
                                        self)
            await channel.send('Tags added to filter!')
        else:
            await channel.send('Tags already in filter!')

    @personal_filter.command(name="remove")
    async def pf_remove(self, ctx, *tags):
        """Remove words from the personal filter. Seperate with a space."""

        user = ctx.message.author
        removed = False
        if not tags:
            await self.bot.send_cmd_help(ctx)
            return
        user_data = await self.bot.database.get(user, self)
        user_tags = user_data.get("filtered_tags", [])
        if not user_tags:
            await ctx.send('You have no tags in your filter')
            return
        for tag in tags:
            if tag in user_tags:
                user_tags.remove(tag.lower())
                removed = True
        if removed:
            await self.bot.database.set(user, {"filtered_tags": user_tags},
                                        self)
            await ctx.send('Tags were removed from your filter')
        else:
            await ctx.send('The specified tags are not in your filter')

    @personal_filter.command(name="show")
    async def pf_show(self, ctx):
        """Show your current filter"""

        user = ctx.message.author
        guild = ctx.guild

        user_data = await self.bot.database.get(user, self)
        if not user_data:
            user_tags = "None"
            personal_filter = "None"
        else:
            user_tags = user_data.get("filtered_tags", [])
            personal_filter = ", ".join(user_tags)
        guild_data = await self.bot.database.get(guild, self)
        if not guild_data:
            guild_tags = "None"
            guild_filter = "None"
        else:
            guild_tags = guild_data.get("filtered_tags", [])
            guild_filter = ", ".join(guild_tags)

        message = (
            "{0.mention},".format(user) + " you're currently filtering the " +
            "following tags: {0}\n\n".format(personal_filter) +
            " {0} is currently filtering the ".format(guild.name) +
            "following tags: {0}".format(guild_filter))

        await ctx.send(message)

    @lewdset.group(name="server_filter")
    @commands.has_permissions(manage_guild=True)
    async def server_filter(self, ctx):
        """Server Filter Management"""
        if ctx.invoked_subcommand is None or isinstance(
                ctx.invoked_subcommand, commands.Group):
            await self.bot.send_cmd_help(ctx)
            return

    @server_filter.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def sf_add(self, ctx, *tags):
        """Add words to the server's filter"""

        guild = ctx.guild
        guild_data = await self.bot.database.get(guild, self)
        guild_tags = guild_data.get("filtered_tags", [])
        added = False

        if not tags:
            await self.bot.send_cmd_help(ctx)
            return

        if not guild_tags:
            await self.bot.database.set(guild, {"filtered_tags": []}, self)

        if len(tags) + len(guild_tags) > MAX_FILTERS:
            await ctx.send('Woah! Too many server filters!')
        for tag in tags:
            if tag.lower() not in guild_tags:
                guild_tags.append(tag.lower())
                added = True
        if added:
            await self.bot.database.set(guild, {"filtered_tags": guild_tags},
                                        self)
            await ctx.send('Tags added to server filter.')
        else:
            await ctx.send('Tags already in server filter')

    @server_filter.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def sf_remove(self, ctx, *tags):
        """Remove words from the server's filter"""

        guild = ctx.guild
        guild_data = await self.bot.database.get(guild, self)
        guild_tags = guild_data.get("filtered_tags", [])
        removed = False

        if not tags:
            await self.bot.send_cmd_help(ctx)
            return

        if not guild_tags:
            await ctx.send("{0} has no filtered server tags.", guild.name)

        for tag in guild_tags:
            if tag.lower() in guild_tags:
                guild_tags.remove(tag.lower())
                removed = True
        if removed:
            await self.bot.database.set(guild, {"filtered_tags": guild_tags},
                                        self)
            await ctx.send("Tags were removed from the server filter.")
        else:
            await ctx.send("Those tags do not exist in the server filter.")

    @server_filter.command(name="show")
    @commands.has_permissions(manage_guild=True)
    async def sf_show(self, ctx):
        """Show your current filter"""

        guild = ctx.guild
        guild_data = await self.bot.database.get(guild, self)

        if not guild_data:
            guild_tags = "None"
            guild_filter = "None"
        else:
            guild_tags = guild_data.get("filtered_tags", [])
            guild_filter = ", ".join(guild_tags)

        message = ("{0} is currently filtering the following tags: {1}".format(
            guild.name, guild_filter))

        await ctx.send(message)

    @commands.command(name="e621")
    async def e621(self, ctx, *tags):
        """Search E621. If no tags are specified, result is random"""

        guild = ctx.guild
        channel = ctx.message.channel
        search = ""

        guild_data = await self.bot.database.get(guild, self)
        channel_data = await self.bot.database.get(channel, self)
        if guild_data:
            channel_mode = channel_data.get("mode")
            if not channel_mode:
                channel_mode = "on"
        else:
            channel_mode = "off"
            await self.bot.database.set(guild, {channel.id: channel_mode},
                                        self)
        e621_is_enabled = guild_data.get("e621_enabled")

        if not e621_is_enabled:
            await ctx.send("E621 command is disabled in this server.")
            return

        if channel_mode == "off":
            await ctx.send('Lewd module is disabled in this channel')
            return

        if not channel.is_nsfw() and self.nsfw_in_tags(tags):
            await ctx.send("Sorry, channel is set to SFW and you have" +
                           " specified an NSFW E621 rating in your tags.")
            return

        msg = await ctx.send("Getting a result...")

        if tags:
            search = " ".join(tags)
        else:
            search = "random"

        try:
            url, filters = await self.construct_url("e621", ctx, tags)
            headers = userAgent

            async with self.session.get(url, headers=headers) as r:
                results = await r.json()
                results = [
                    res for res in results
                    if not any(x in res["tags"] for x in filters)
                    and not res["file_url"].endswith((".mp4", ".swf", ".webm"))
                ]

                random_post = choice(results)
                embed = self.e621_embed(random_post, search)
            try:
                await msg.edit(content=None, embed=embed)
            except Exception as e:
                await msg.edit(content="Unable to find result: {0}".format(e))
        except IndexError:
            await msg.edit(content="No results found for: {0}".format(search))
        except TooManyTagsError:
            await msg.edit(content="Sorry: too many tags.")
        except Exception as e:
            await msg.edit(content="Unknown exception occured: {0}".format(e))

    @commands.command(name="rule34")
    async def rule34(self, ctx, *tags):
        """Search Rule34. If no tags are specified the result is random"""

        guild = ctx.guild
        channel = ctx.message.channel
        search = ""

        guild_data = await self.bot.database.get(guild, self)
        channel_data = await self.bot.database.get(channel, self)
        channel_mode = channel_data.get("mode")
        if not channel_mode:
            channel_mode = "on"
        rule34_is_enabled = guild_data.get("rule34_enabled")

        if not rule34_is_enabled:
            await ctx.send("Rule34 command is disabled in this server.")
            return

        if channel_mode == "off":
            await ctx.send('Lewd module is disabled in this channel')
            return

        if not channel.is_nsfw() and self.nsfw_in_tags(tags):
            await ctx.send("Sorry, channel is set to SFW and you have" +
                           " specified an NSFW Rule34 rating in your tags.")
            return

        msg = await ctx.send("Getting a result...")

        if tags:
            search = " ".join(tags)
        else:
            search = "random"

        try:
            url, filters = await self.construct_url("r34", ctx, tags)
            async with self.session.get(url) as r:
                tree = ET.fromstring(await r.read())
                results = [
                    {
                        "url": str(post.attrib.get('file_url')),
                        "source": str(post.attrib.get('source'))
                    } for post in tree.iter("post")
                    if not any(x in post.attrib.get('tags') for x in filters)
                    and not str(post.attrib.get("file_url")).endswith(
                        (".mp4", ".webm", ".swf"))
                ]
            post = choice(results)
            embed = self.r34_embed(post, search)
            try:
                await msg.edit(content=None, embed=embed)
            except Exception as e:
                await msg.edit(content="Unable to find result: {0}".format(e))

        except IndexError:
            await msg.edit(content="No results found for: {0}".format(search))
        except TooManyTagsError:
            await msg.edit(content="Sorry: too many tags.")
        except Exception as e:
            await msg.edit(content="Unknown exception occured: {0}".format(e))

    def nsfw_in_tags(self, tags):
        nsfw = [
            "rating:e", "rating:explicit", "rating:q", "rating:questionable"
        ]
        if any(x in [tag.lower() for tag in tags] for x in nsfw):
            return True
        else:
            return False

    def e621_embed(self, post, search):
        url = post["file_url"]
        submission = "https://e621.net/post/show/" + str(post["id"])
        source = post["source"]
        if not source:
            description = "[e621 post]({0})".format(submission)
        else:
            description = "[e621 post]({0}) ⋅ [original source]({1})".format(
                submission, source)
        color = 0x152f56
        data = discord.Embed(
            title="e621 search results", colour=color, description=description)
        data.set_image(url=url)
        data.set_footer(text="Results for: {0}".format(search))
        return data

    def r34_embed(self, post, search):
        url = post["url"]
        source = post["source"]
        if not source:
            description = None
        else:
            description = "[Source]({0})".format(source)
        color = 0xaae5a3
        data = discord.Embed(
            title="Rule 34 search results",
            colour=color,
            description=description)
        data.set_image(url=url)
        data.set_footer(text="Results for: {0}".format(search))
        return data

    async def construct_url(self, base, ctx, text):
        user = ctx.message.author
        channel = ctx.message.channel
        guild = ctx.guild

        guild_data = await self.bot.database.get(guild, self)
        server_filters = guild_data.get("filtered_tags", [])

        user_data = await self.bot.database.get(user, self)
        user_filters = user_data.get("filtered_tags", [])

        tags = []
        filters = []
        text = [x.lower() for x in text]
        filters.extend([t.lower() for t in text if t.startswith("-")])
        text = list(set(text) - set(filters))

        if not channel.is_nsfw():
            if "rating:s" not in tags or "rating:safe" not in tags:
                tags.append("rating:safe")
            elif "rating:safe" not in tags and base != "e621":
                tags.append("rating:safe")
        if not text and base == "e621":
            tags.append("random")
        else:
            tags.extend(text)
        if base == "e621":
            max_tags = 6
            url = "https://e621.net/post/index.json?limit=150&tags="
        else:
            max_tags = 20
            url = "https://rule34.xxx/index.php?page=dapi&s=post&q=index&tags="
        if len(tags) > max_tags:
            raise TooManyTagsError()
        filters_allowed = max_tags - len(tags)
        filters.extend(["-" + x.lower() for x in server_filters])
        filters.extend(["-" + x.lower() for x in user_filters])
        filters = list(set(filters))
        tags.extend(filters[:filters_allowed])
        del filters[:filters_allowed]
        search = "%20".join(tags)
        filters = [f.lstrip("-") for f in filters]
        return url + search, filters


def setup(bot):
    n = Lewd(bot)
    bot.add_cog(n)
