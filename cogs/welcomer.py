import discord
from discord.ext import commands

DEFAULT = {
    "join_channel": "",
    "leave_channel": "",
    "join_message": "{0.mention} has joined the server {1}.",
    "leave_message": "{0.mention} has left the server {1}",
    "join_enabled": False,
    "leave_enabled": False,
}


class Welcomer:
    """Allow the server to welcome new members"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="welcomeset")
    @commands.guild_only()
    async def welcomeset(self, ctx):
        """Set options for the welcomer"""

        guild = ctx.guild
        guild_settings = await self.bot.database.get(guild, self)

        if not guild_settings:
            await self.bot.database.set(guild, DEFAULT, self)

        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @welcomeset.command(name="toggle")
    async def toggle(self, ctx, toggled_command):
        """Toggle with either "join" or "leave" after the command"""

        guild = ctx.guild
        guild_settings = await self.bot.database.get(guild, self)

        join_enabled = guild_settings.get("join_enabled")
        leave_enabled = guild_settings.get("leave_enabled")

        toggled_command = toggled_command.lower()

        if toggled_command == "join":
            if join_enabled:
                await self.bot.database.set(guild, {"join_enabled": False},
                                            self)
                await ctx.send('Join messaged have been disabled')
                return
            else:
                await self.bot.database.set(guild, {"join_enabled": True},
                                            self)
                await ctx.send('Join messages have been enabled')
                return
        if toggled_command == "leave":
            if leave_enabled:
                await self.bot.database.set(guild, {"leave_enabled": False},
                                            self)
                await ctx.send("Leave messages have been disabled")
                return
            else:
                await self.bot.database.set(guild, {"leave_enabled": True},
                                            self)
                await ctx.send("Leave messages have been enabled")
                return
        else:
            await self.bot.send_cmd_help(ctx)

    @welcomeset.command(name="join_message")
    async def join_message(self, ctx, message):
        """Set the join message
        Use {0} for the user
        Use {1} for the server."""

        guild = ctx.guild

        if len(message) > 200:
            await ctx.send("Message too long. Try again.")
            return

        try:
            await self.bot.database.set(guild, {"join_message": message}, self)
            await ctx.send(
                "Message has been set to:\n'''{}'''".format(message))
        except Exception as e:
            await ctx.send("Error settings message: {}".format(e))

    @welcomeset.command(name="leave_message")
    async def leave_message(self, ctx, message):
        """Set the join message
        Use {0} for the user
        Use {1} for the server.
        Max limit of 200 characters."""

        guild = ctx.guild

        if len(message) > 200:
            await ctx.send("Message too long. Try again.")
            return
        try:
            await self.bot.database.set(guild, {"leave_message": message},
                                        self)
            await ctx.send(
                "Message has been set to:\n'''{}'''".format(message))
        except Exception as e:
            await ctx.send("Error settings message: {}".format(e))

    @welcomeset.command(name="join_channel")
    async def join_channel(self, ctx, channel: discord.TextChannel):
        """Sets the join message channel"""

        guild = ctx.guild

        if not channel:
            await self.bot.send_cmd_help(ctx)
            return

        await self.bot.database.set(guild, {"join_channel": channel.id}, self)
        await ctx.send("Join messages will be sent to {}".format(
            channel.mention))

    @welcomeset.command(name="leave_channel")
    async def leave_channel(self, ctx, channel: discord.TextChannel):
        """Sets the leave message channel"""

        guild = ctx.guild

        if not channel:
            await self.bot.send_cmd_help(ctx)
            return

        await self.bot.database.set(guild, {"leave_channel": channel.id}, self)
        await ctx.send("Leave messages will be sent to {}".format(
            channel.mention))

    async def on_member_join(self, user):

        guild = user.guild
        guild_settings = await self.bot.database.get(guild, self)
        join_enabled = guild_settings.get("join_enabled")
        join_channel = guild_settings.get("join_channel")
        join_message = guild_settings.get("join_message")

        if not join_enabled:
            return

        embed_description = (join_message.format(user, guild))
        embed = discord.Embed(
            title="User Joined",
            description=embed_description,
            colour=discord.Colour.green())
        if guild.icon_url:
            embed.set_thumbnail(url=guild.icon_url)
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.set_footer(
            text=self.bot.user.name, icon_url=self.bot.user.avatar_url)

        destination = self.bot.get_channel(join_channel)
        await destination.send(embed=embed)
        return

    async def on_member_remove(self, user):

        guild = user.guild
        guild_settings = await self.bot.database.get(guild, self)
        leave_enabled = guild_settings.get("leave_enabled")
        leave_channel = guild_settings.get("leave_channel")
        leave_message = guild_settings.get("leave_message")

        if not leave_enabled:
            return

        embed_description = (leave_message.format(user, guild))
        embed = discord.Embed(
            title="User Left",
            description=embed_description,
            colour=discord.Colour.red())
        if guild.icon_url:
            embed.set_thumbnail(url=guild.icon_url)
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.set_footer(
            text=self.bot.user.name, icon_url=self.bot.user.avatar_url)

        destination = self.bot.get_channel(leave_channel)
        await destination.send(embed=embed)
        return


def setup(bot):
    bot.add_cog(Welcomer(bot))
