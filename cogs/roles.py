import discord
from discord.ext import commands

default_settings = {
    "autorole_on": True,
    "iam_on": True,
    "autorole_roles": [],
    "iam_roles": []
}

iamcommands = ["roles", "remove", "add", "toggle"]


class Roles:
    """Role management tools including:

    Autorole: automatically assign roles when a user joins
    Register: set up commands for users to join themselves
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.group(name="autorole")
    async def autorole(self, ctx):
        """Automatically assign new users roles"""

        guild = ctx.guild
        guild_settings = await self.bot.database.get(guild, self)

        if not guild_settings:
            await self.bot.database.set(guild, default_settings, self)

        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @autorole.command(name="show")
    async def autorole_show(self, ctx):
        """Show a list of roles users will recieve when they join the server
        """

        guild = ctx.guild

        guild_settings = await self.bot.database.get(guild, self)
        roles = guild_settings.get("autorole_roles", [])
        autorole_on = guild_settings.get("autorole_on", [])

        if not autorole_on:
            await ctx.send("Autorole commands are disabled in this server.")
            return

        if not roles:
            await ctx.send("There are no roles that will be" +
                           " automatically assigned to new users.")
            return

        available_roles = []

        for role in roles:
            role = discord.utils.get(guild.roles, id=role)
            available_roles.append(role.name)

        roles = ", ".join(available_roles)
        await ctx.send("The roles users will recieve" +
                       " when they join are: ``{0}``".format(roles))

    @autorole.command(name="add")
    async def autorole_add(self, ctx, *roles):
        """Add a role to be automatically assigned upon a user joining

        Duplicate entrys of the same name will be ignored
        Roles with a space should be in quotations
        """

        guild = ctx.guild

        guild_settings = await self.bot.database.get(guild, self)
        autoroles = guild_settings.get("autorole_roles", [])
        autorole_on = guild_settings.get("autorole_on", [])

        if not autorole_on:
            await ctx.send("Autorole is disabled in this server")
            return

        if not roles:
            await self.bot.send_cmd_help(ctx)
            return

        added = False

        for role in roles:
            role = discord.utils.get(guild.roles, name=role)
            if role:
                if role.id not in autoroles:
                    autoroles.append(role.id)
                    added = True

        if added:
            await self.bot.database.set(guild, {"autorole_roles": autoroles},
                                        self)
            await ctx.send("Roles will be automatically assigned to new users."
                           + " Use ``>autorole show`` to view the list of" +
                           " automatically added roles.")
            return
        else:
            await ctx.send("Roles not added. These may already be" +
                           " automatically assigned to new users." +
                           " Use ``>autorole show`` to view the list of" +
                           " automatically added roles.")

    @autorole.command(name="remove")
    async def autorole_remove(self, ctx, *roles):
        """Remove a role to be automatically assigned upon a user joining

        Entries that do not exist will be ignored
        Roles with a space should be in quotations
        """
        guild = ctx.guild

        guild_settings = await self.bot.database.get(guild, self)
        autoroles = guild_settings.get("autorole_roles", [])
        autorole_on = guild_settings.get("autorole_on", [])

        if not autorole_on:
            await ctx.send("Autorole is disabled in this server.")
            return

        if not roles:
            await self.bot.send_cmd_help(ctx)
            return

        if not autoroles:
            await ctx.send("This server has no roles to be" +
                           " automatically assigned to new users")
            return

        removed = False

        for role in roles:
            role = discord.utils.get(guild.roles, name=role)
            if role:
                if role.id in autoroles:
                    autoroles.remove(role.id)
                    removed = True

        if removed:
            await self.bot.database.set(guild, {"autorole_roles": autoroles},
                                        self)
            await ctx.send(
                "Roles will no longer be automatically assigned to new users."
                + " Use ``>autorole show`` to view the list of" +
                " automatically added roles.")
            return
        else:
            await ctx.send("Roles not removed. These may already not be" +
                           " automatically assigned to new users." +
                           " Use ``>autorole show`` to view the list of" +
                           " automatically added roles.")

    @autorole.command(name="toggle")
    async def autorole_toggle(self, ctx):
        """This will fully disable the autoroles feature

        Please note that this will not disable the iam commands.
        """

        guild = ctx.guild

        guild_setting = await self.bot.database.get(guild, self)
        autorole_on = guild_setting.get("autorole_on", [])

        if autorole_on:
            await self.bot.database.set(guild, {"autorole_on": False}, self)
            await ctx.send("Autorole has been disabled.")
            return
        if not autorole_on:
            await self.bot.database.set(guild, {"autorole_on": True}, self)
            await ctx.send("Autorole has been enabled")
            return

    @commands.guild_only()
    @commands.group(name="iamroles")
    async def iamroles(self, ctx):
        """Assign yourself a role on the server

        Note: The administrators must set up these roles to be joinable"""

        guild = ctx.guild
        guild_settings = await self.bot.database.get(guild, self)

        if not guild_settings:
            await self.bot.database.set(guild, default_settings, self)

        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @iamroles.command(name="show")
    async def iam_show(self, ctx):
        """These are a list of roles you may request to join
        """

        guild = ctx.guild

        guild_settings = await self.bot.database.get(guild, self)
        roles = guild_settings.get("iam_roles", [])
        iam_on = guild_settings.get("iam_on", [])

        if not iam_on:
            await ctx.send("'iam' commands are disabled in this server.")
            return

        if not roles:
            await ctx.send(
                "There are no roles that users are" + " able to join.")
            return

        role_names = []
        for role in roles:
            role = discord.utils.get(guild.roles, id=role)
            if role:
                role_names.append(role.name)

        roles = ", ".join(role_names)
        await ctx.send(
            "The roles users can join" + " are: ``{0}``".format(roles))

    @iamroles.command(name="add")
    async def iam_add(self, ctx, *roles):
        """Add a role that a user can join themselves

        Duplicate entrys of the same name will be ignored
        Roles with a space should be in quotations
        Note: this is case sensitive
        """

        guild = ctx.guild

        guild_settings = await self.bot.database.get(guild, self)
        iamroles = guild_settings.get("iam_roles", [])
        iam_on = guild_settings.get("iam_on", [])

        if not iam_on:
            await ctx.send("'iam' is disabled in this server.")
            return

        if not roles:
            await self.bot.send_cmd_help(ctx)
            return

        added = False

        for role in roles:
            joinable_role = discord.utils.get(guild.roles, name=role)
            if joinable_role:
                if joinable_role.id not in iamroles:
                    iamroles.append(joinable_role.id)
                    added = True
            else:
                await ctx.send("{0} does not exist.".format(role))

        if added:
            await self.bot.database.set(guild, {"iam_roles": iamroles}, self)
            await ctx.send("Users may now join these roles." +
                           " Use ``>iamroles show`` to view the list of" +
                           " user joinable roles.")
            return
        else:
            await ctx.send("Roles not added. These may already be" +
                           " joinable by users" + " or not exist." +
                           " Use ``>iamroles show`` to view the list of" +
                           " user joinable roles.")

    @iamroles.command(name="remove")
    async def iam_remove(self, ctx, *roles):
        """Remove a role that a user can add themselves.

        Entries that do not exist will be ignored
        Roles with a space should be in quotations
        Note: this is case sensitive
        """
        guild = ctx.guild

        guild_settings = await self.bot.database.get(guild, self)
        iamroles = guild_settings.get("iam_roles", [])
        iam_on = guild_settings.get("iam_on", [])

        if not iam_on:
            await ctx.send("'iam' is disabled in this server.")
            return

        if not roles:
            await self.bot.send_cmd_help(ctx)
            return

        if not iamroles:
            await ctx.send(
                "This server has no roles that a" + " user can join.")
            return

        removed = False

        for role in roles:
            role = discord.utils.get(guild.roles, name=role)
            if role:
                if role.id in iamroles:
                    iamroles.remove(role.id)
                    removed = True

        if removed:
            await self.bot.database.set(guild, {"iam_roles": iamroles}, self)
            await ctx.send("Roles will no longer be joinable by users." +
                           " Use ``>iamroles show`` to view the list of" +
                           " joinable user roles.")
            return
        else:
            await ctx.send("Roles not removed. These may already not be" +
                           " joinable by users." +
                           " Use ``>iamroles show`` to view the list of" +
                           " joinable user roles.")

    @iamroles.command(name="toggle")
    async def iam_toggle(self, ctx):
        """This will fully disable the 'iam' feature

        Please note that this will not disable the autorole commands.
        """

        guild = ctx.guild

        guild_setting = await self.bot.database.get(guild, self)
        iam_on = guild_setting.get("iam_on", [])

        if iam_on:
            await self.bot.database.set(guild, {"iam_on": False}, self)
            await ctx.send("'iam' has been disabled.")
            return
        if not iam_on:
            await self.bot.database.set(guild, {"iam_on": True}, self)
            await ctx.send("'iam' has been enabled")
            return

    @commands.command(name="iam")
    async def iam_command(self, ctx, *roles):
        """Join a role on the server that the admin has permitted

        Note: you may join multiple roles with one command
        """

        guild = ctx.guild

        guild_settings = await self.bot.database.get(guild, self)
        iam_roles = guild_settings.get("iam_roles", [])

        if not roles:
            await self.bot.send_cmd_help(ctx)
            return

        added_roles = []
        available_roles = []

        for role in iam_roles:
            role = discord.utils.get(guild.roles, id=role)
            available_roles.append(role.id)

        added = False

        for role in roles:
            drole = discord.utils.get(guild.roles, name=role)
            if drole:
                if drole.id in available_roles:
                    if drole not in ctx.message.author.roles:
                        try:
                            await ctx.message.author.add_roles(
                                drole, atomic=True)
                            added = True
                        except discord.Forbidden:
                            await ctx.send(
                                "Either I lack the neccessary permissions" +
                                " to add roles or the role is higher than me.")
                        added_roles.append(drole.name)
                    else:
                        await ctx.send(
                            "You already have the role: ``{0}``.".format(
                                drole.name))
                else:
                    await ctx.send("You cannot join the role: ``{0}``".format(
                        drole.name))
            else:
                await ctx.send(
                    "One of those roles do not exist: ``{0}``".format(role))

        if added:
            added_roles = ", ".join(added_roles)
            await ctx.send(
                "The roles: ``{0}`` have been".format(added_roles) +
                " added to the user {0}".format(ctx.message.author.mention))

    @commands.command(name="iamnot")
    async def iamnot_command(self, ctx, *roles):
        """Leave a role on the server that the admin has permitted

        Note: you may leave multiple roles with one command
        """

        guild = ctx.guild

        guild_settings = await self.bot.database.get(guild, self)
        iam_roles = guild_settings.get("iam_roles", [])

        if not roles:
            await self.bot.send_cmd_help(ctx)
            return

        removed_roles = []
        available_roles = []

        for role in iam_roles:
            role = discord.utils.get(guild.roles, id=role)
            available_roles.append(role.id)

        removed = False

        for role in roles:
            drole = discord.utils.get(guild.roles, name=role)
            if drole:
                if drole.id in available_roles:
                    if drole in ctx.message.author.roles:
                        try:
                            await ctx.message.author.remove_roles(
                                drole, atomic=True)
                            removed = True
                        except discord.Forbidden:
                            await ctx.send(
                                "Either I lack the neccessary permissions" +
                                " to add roles or the role is higher than me.")
                        removed_roles.append(drole.name)
                    else:
                        await ctx.send(
                            "You do not have the role: ``{0}``".format(
                                drole.name))
                else:
                    await ctx.send("You cannot leave the role: ``{0}``".format(
                        drole.name))
            else:
                await ctx.send(
                    "One of those roles do not exist: ``{0}``".format(role))

        if removed:
            removed_roles = ", ".join(removed_roles)
            await ctx.send("The roles: ``{0}`` have been".format(removed_roles)
                           + " removed from the user {0}".format(
                               ctx.message.author.mention))

    async def on_guild_role_delete(self, role):
        guild = role.guild

        guild_settings = await self.bot.database.get(guild, self)
        iamroles = guild_settings.get("iam_roles", [])

        if role.id in iamroles:
            iamroles.remove(role.id)
            await self.bot.database.set(guild, {"iam_roles": iamroles})

    async def on_member_join(self, user):

        guild = user.guild
        guild_settings = await self.bot.database.get(guild, self)
        autorole_roles = guild_settings.get("autorole_roles", [])

        autorole_roles_array = []

        if not autorole_roles:
            return

        for role in autorole_roles:
            role = discord.utils.get(guild.roles, id=role)
            autorole_roles_array.append(role)

        if not autorole_roles_array:
            return

        for role in autorole_roles_array:
            if role not in user.roles:
                try:
                    await user.add_roles(role, atomic=True)
                except Exception:
                    pass


def setup(bot):
    bot.add_cog(Roles(bot))
