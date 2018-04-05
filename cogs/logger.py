import discord
from discord.ext import commands
import aiohttp
import logging

log = logging.getLogger(__name__)

default_settings = {
    "user_logging_channels": [],
    "update_logging_channels": [],
    "exceptions": [],
    "on": False,
    "channels": []
}


class Logger:
    """Announces logged changes in the server."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    def __unload(self):
        self.session.close()

    @commands.group(name="logger_set")
    @commands.has_permissions(manage_guild=True)
    async def logger_set(self, ctx):
        """Change the logger settings"""

        guild = ctx.guild
        guild_settings = await self.bot.database.get(guild, self)

        if not guild_settings:
            await self.bot.database.set(guild, default_settings, self)

        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)
            return

    @logger_set.command(name="toggle")
    @commands.has_permissions(manage_guild=True)
    async def logger_toggle(self, ctx):
        """Toggle the logger on and off"""

        guild = ctx.guild

        guild_setting = await self.bot.database.get(guild, self)
        logger_on = guild_setting.get("on", [])

        if logger_on:
            await self.bot.database.set(guild, {"on": False}, self)
            await ctx.send("Logger has been disabled.")
            return
        if not logger_on:
            await self.bot.database.set(guild, {"on": True}, self)
            await ctx.send("Logger has been enabled")
            return

    @logger_set.command(name="userlog_channels")
    @commands.has_permissions(manage_guild=True)
    async def userlog_channels(self, ctx, *channels: discord.TextChannel):
        """Set the channels that user notifications will be sent to

        This includes: User join, leave, ban and unban notifications
        """

        guild = ctx.guild

        if not channels:
            await self.bot.send_cmd_help(ctx)
            return

        logging_channels = []

        for channel in channels:
            logging_channels.append(channel.id)

        await self.bot.database.set(
            guild, {"user_logging_channels": logging_channels}, self)
        await ctx.send("Logging channels set!")

    @logger_set.command(name="updatelog_channels")
    @commands.has_permissions(manage_guild=True)
    async def updatelog_channels(self, ctx, *channels: discord.TextChannel):
        """Set the channels that update notifications will be sent to

        This includes: Message edits, deletes and user nickname changes
        """

        guild = ctx.guild

        if not channels:
            await self.bot.send_cmd_help(ctx)
            return

        logging_channels = []

        for channel in channels:
            logging_channels.append(channel.id)

        await self.bot.database.set(
            guild, {"update_logging_channels": logging_channels}, self)
        await ctx.send("Logging channels set!")

    @logger_set.command(name="exceptions")
    @commands.has_permissions(manage_guild=True)
    async def exceptions(self, ctx, *users: discord.User):
        """Set the users that are exempt from the logger."""

        guild = ctx.guild
        guild_settings = await self.bot.database.get(guild, self)
        exceptions = guild_settings.get("exceptions")

        if not users:
            await self.bot.send_cmd_help(ctx)
            return

        for user in users:
            if user.id not in exceptions:
                exceptions.append(user.id)
                await ctx.send("{0} added to exceptions".format(user.name))
            elif user.id in exceptions:
                exceptions.remove(user.id)
                await ctx.send("{0} removed from exceptions".format(user.name))

        await self.bot.database.set(guild, {"exceptions": exceptions}, self)
        await ctx.send("Exceptions set!")

    async def on_member_join(self, user):

        guild = user.guild
        guild_settings = await self.bot.database.get(guild, self)
        logger_enabled = guild_settings.get("on")
        logger_channels = guild_settings.get("user_logging_channels")
        exceptions = guild_settings.get("exceptions")

        if not logger_enabled:
            return

        if user.id in exceptions:
            return

        embed_description = (
            "{0.mention} ({1}) has joined the server {2}!".format(
                user, user, guild))
        embed = discord.Embed(
            title="User Joined",
            description=embed_description,
            colour=discord.Colour.green())
        if guild.icon_url:
            embed.set_thumbnail(url=guild.icon_url)
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.set_footer(
            text=self.bot.user.name, icon_url=self.bot.user.avatar_url)

        for channel in logger_channels:
            destination = self.bot.get_channel(channel)
            await destination.send(embed=embed)
        return

    async def on_member_remove(self, user):

        guild = user.guild
        guild_settings = await self.bot.database.get(guild, self)
        logger_enabled = guild_settings.get("on")
        logger_channels = guild_settings.get("user_logging_channels")
        exceptions = guild_settings.get("exceptions")

        if not logger_enabled:
            return

        if user.id in exceptions:
            return

        embed_description = (
            "{0.mention} ({1}) has left the server {2}!".format(
                user, user, guild))
        embed = discord.Embed(
            title="User Left",
            description=embed_description,
            colour=discord.Colour.red())
        if guild.icon_url:
            embed.set_thumbnail(url=guild.icon_url)
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.set_footer(
            text=self.bot.user.name, icon_url=self.bot.user.avatar_url)

        for channel in logger_channels:
            destination = self.bot.get_channel(channel)
            await destination.send(embed=embed)
        return

    async def on_member_ban(self, guild, user):

        guild_settings = await self.bot.database.get(guild, self)
        logger_enabled = guild_settings.get("on")
        logger_channels = guild_settings.get("user_logging_channels")
        exceptions = guild_settings.get("exceptions")

        if not logger_enabled:
            return

        if user.id in exceptions:
            return

        embed_description = (
            "{0.mention} ({1}) has been banned from the server {2}!".format(
                user, user, guild))
        embed = discord.Embed(
            title="User Banned",
            description=embed_description,
            colour=discord.Colour.purple())
        if guild.icon_url:
            embed.set_thumbnail(url=guild.icon_url)
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.set_footer(
            text=self.bot.user.name, icon_url=self.bot.user.avatar_url)

        for channel in logger_channels:
            destination = self.bot.get_channel(channel)
            await destination.send(embed=embed)
        return

    async def on_member_unban(self, guild, user):

        guild_settings = await self.bot.database.get(guild, self)
        logger_enabled = guild_settings.get("on")
        logger_channels = guild_settings.get("user_logging_channels")
        exceptions = guild_settings.get("exceptions")

        if not logger_enabled:
            return

        if user.id in exceptions:
            return

        embed_description = (
            "{0.mention} ({1}) has been unbanned from the server {2}!".format(
                user, user, guild))
        embed = discord.Embed(
            title="User Unbanned",
            description=embed_description,
            colour=discord.Colour.purple())
        if guild.icon_url:
            embed.set_thumbnail(url=guild.icon_url)
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.set_footer(
            text=self.bot.user.name, icon_url=self.bot.user.avatar_url)

        for channel in logger_channels:
            destination = self.bot.get_channel(channel)
            await destination.send(embed=embed)
        return

    async def on_member_update(self, before, after):

        guild = after.guild
        guild_settings = await self.bot.database.get(guild, self)
        logger_enabled = guild_settings.get("on")
        logger_channels = guild_settings.get("update_logging_channels")
        exceptions = guild_settings.get("exceptions")

        if before.nick == after.nick:
            return

        if not logger_enabled:
            return

        if after.id in exceptions:
            return

        embed_description = (
            "{0} has changed their nickname on the".format(before.name) +
            " server to {0} ({1.mention})".format(after.nick, after))
        embed = discord.Embed(
            title="User Nickname Change",
            description=embed_description,
            colour=discord.Colour.light_grey())
        if guild.icon_url:
            embed.set_thumbnail(url=guild.icon_url)
        embed.set_author(name=after.name, icon_url=after.avatar_url)
        embed.set_footer(
            text=self.bot.user.name, icon_url=self.bot.user.avatar_url)

        for channel in logger_channels:
            destination = self.bot.get_channel(channel)
            await destination.send(embed=embed)
        return

        for channel in logger_channels:
            destination = self.bot.get_channel(channel)
            await destination.send(embed=embed)
        return

    async def on_message_edit(self, before, after):

        guild = after.guild
        guild_settings = await self.bot.database.get(guild, self)
        logger_enabled = guild_settings.get("on")
        logger_channels = guild_settings.get("update_logging_channels")
        exceptions = guild_settings.get("exceptions")

        if not logger_enabled:
            return

        if after.author.id in exceptions:
            return

        if after.author == self.bot.user:
            return

        embed_description = ("{0} has edited their message in the ".format(
            before.author.mention) +
                             "server.\n\nBefore: {0}\n\nAfter: {1}".format(
                                 before.content, after.content))
        embed = discord.Embed(
            title="Message Edited",
            description=embed_description,
            colour=discord.Colour.blue())
        if guild.icon_url:
            embed.set_thumbnail(url=guild.icon_url)
        embed.set_author(
            name=after.author.name, icon_url=after.author.avatar_url)
        embed.set_footer(
            text=self.bot.user.name, icon_url=self.bot.user.avatar_url)

        for channel in logger_channels:
            destination = self.bot.get_channel(channel)
            await destination.send(embed=embed)
        return

        for channel in logger_channels:
            destination = self.bot.get_channel(channel)
            await destination.send(embed=embed)
        return

    async def on_message_delete(self, message):

        guild = message.guild
        guild_settings = await self.bot.database.get(guild, self)
        logger_enabled = guild_settings.get("on")
        logger_channels = guild_settings.get("update_logging_channels")
        exceptions = guild_settings.get("exceptions")

        if not logger_enabled:
            return

        if message.author.id in exceptions:
            return

        if message.author == self.bot.user:
            return

        embed_description = ("{0} has has a message deleted in the ".format(
            message.author.mention) +
                             "server.\n\nContent: {0}".format(message.content))
        embed = discord.Embed(
            title="Message Deleted",
            description=embed_description,
            colour=discord.Colour.gold())
        if guild.icon_url:
            embed.set_thumbnail(url=guild.icon_url)
        embed.set_author(
            name=message.author.name, icon_url=message.author.avatar_url)
        embed.set_footer(
            text=self.bot.user.name, icon_url=self.bot.user.avatar_url)

        for channel in logger_channels:
            destination = self.bot.get_channel(channel)
            await destination.send(embed=embed)
        return

        for channel in logger_channels:
            destination = self.bot.get_channel(channel)
            await destination.send(embed=embed)
        return


def setup(bot):
    n = Logger(bot)
    bot.add_cog(n)
