import discord
from discord.ext import commands
from random import choice


class Utility:
    """Various utility commands for your server"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="giveallroles")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def give_all_role(self, ctx, *roles):
        """Give x roles to all users in the server"""

        guild = ctx.guild

        if not roles:
            await self.bot.send_cmd_help(ctx)
            return

        for role in roles:
            try:
                new_role = discord.utils.get(guild.roles, id=format(role))
                return
            except Exception as e:
                await ctx.send("Unable to locate the" +
                               "role: {0}\n{1}".format(new_role, e))
            try:
                for member in guild.members:
                    await self.bot.add_roles(member, role)
                await ctx.send("Success adding the {0} role" +
                               "to everyone".format(new_role))
            except Exception as e:
                await ctx.send("Unable to add the {0} role" +
                               "to everyone.\n{1}".format(new_role, e))
                return

    @commands.command(name="noroles")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def noroles(self, ctx):
        """List all users in the server with no roles"""

        guild = ctx.guild

        try:
            await ctx.send("The following users have no roles:\n" + "\n".join([
                mem.mention for mem in guild.members if (len(mem.roles == 1))
            ]))
        except Exception as e:
            await ctx.send("Error: {1}".format(e))

    @commands.command(name="serverinfo")
    @commands.guild_only()
    async def serverinfo(self, ctx):
        """View the server's information"""

        guild = ctx.guild

        online = len([
            m.status for m in guild.members
            if m.status == discord.Status.online
            or m.status == discord.Status.idle
        ])
        total_users = len(guild.members)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        passed = (ctx.message.created_at - guild.created_at).days
        created_at = ("Since {}. That's over {} days ago!"
                      "".format(
                          guild.created_at.strftime("%d %b %Y %H:%M"), passed))

        colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)

        data = discord.Embed(
            description=created_at, colour=discord.Colour(value=colour))
        data.add_field(name="Region", value=str(guild.region))
        data.add_field(name="Users", value="{}/{}".format(online, total_users))
        data.add_field(name="Text Channels", value=text_channels)
        data.add_field(name="Voice Channels", value=voice_channels)
        data.add_field(name="Roles", value=len(guild.roles))
        data.add_field(name="Owner", value=str(guild.owner))
        data.set_footer(text="Server ID: " + str(guild.id))

        if guild.icon_url:
            data.set_author(name=guild.name, url=guild.icon_url)
            data.set_thumbnail(url=guild.icon_url)
        else:
            data.set_author(name=guild.name)

        try:
            await ctx.send(embed=data)
        except discord.HTTPException:
            await ctx.send("I need the `Embed links` permission "
                           "to send this")

    @commands.command()
    @commands.guild_only()
    async def userinfo(self, ctx, *, user: discord.Member = None):
        """Shows users's informations"""
        author = ctx.message.author
        server = ctx.guild

        if not user:
            user = author

        roles = [x.name for x in user.roles if x.name != "@everyone"]

        joined_at = user.joined_at
        since_created = (ctx.message.created_at - user.created_at).days
        since_joined = (ctx.message.created_at - joined_at).days
        user_joined = joined_at.strftime("%d %b %Y %H:%M")
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        member_number = sorted(
            server.members, key=lambda m: m.joined_at).index(user) + 1

        created_on = "{}\n({} days ago)".format(user_created, since_created)
        joined_on = "{}\n({} days ago)".format(user_joined, since_joined)

        game = "Chilling in {} status".format(user.status)
        color = discord.Colour.red()

        if not user.activity:
            pass
        if user.activity and user.activity.name == "Spotify":

            music_artist = ",".join(author.activity.artists)

            game = "Listening to Spotify: {0} by {1}".format(
                user.activity.title, music_artist)
            color = discord.Colour.green()
        elif user.activity and user.activity.name == "Streaming":
            game = "Streaming: [{}]({})".format(user.activity.name,
                                                user.activity.url)
            color = discord.Colour.purple()
        elif user.activity:
            game = "Playing {}".format(user.activity.name)
            color = discord.Colour.gold()

        if roles:
            roles = sorted(
                roles,
                key=[
                    x.name for x in server.role_hierarchy
                    if x.name != "@everyone"
                ].index)
            roles = ", ".join(roles)
        else:
            roles = "None"

        data = discord.Embed(description=game, colour=color)
        data.add_field(name="Joined Discord on", value=created_on)
        data.add_field(name="Joined this server on", value=joined_on)
        data.add_field(name="Roles", value=roles, inline=False)
        data.set_footer(text="Member #{} | User ID:{}"
                        "".format(member_number, user.id))

        name = str(user)
        name = " ~ ".join((name, user.nick)) if user.nick else name

        if user.avatar_url:
            data.set_author(name=name, url=user.avatar_url)
            data.set_thumbnail(url=user.avatar_url)
        else:
            data.set_author(name=name)

        try:
            await ctx.send(embed=data)
        except discord.HTTPException:
            await ctx.send("I need the `Embed links` permission "
                           "to send this")


def setup(bot):
    bot.add_cog(Utility(bot))
