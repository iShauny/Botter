import discord
from discord.ext import commands


class Reactions:
    """Text and Emote Reactions Controls"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="texttriggers")
    @commands.has_permissions(administrator=True)
    async def texttriggers(self, ctx):
        """Add emoji or text reactions"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @texttriggers.command(name="set_text_response")
    async def set_text_response(self, ctx, reacting_text, reacted_text):
        """React to messages with a text response

        reacting_text = Text that triggers the reaction
        reated_text = Text the bot will react with"""

        guild = ctx.guild
        doc = await self.bot.database.get(guild, self)
        text_reactions = doc.get("text_reactions")

        for reactions in text_reactions:
            if reacting_text in reactions:
                reacted_text = reactions[reacting_text]
                await ctx.send("Text reactions already exists." +
                               "I react to {} with {}.".format(
                                   reacting_text, reacted_text))
                return
        try:
            reaction = {reacting_text: reacted_text}
            await self.bot.database.set(
                guild, {"text_reactions": reaction}, self, operation="$push")
            await ctx.send("")
            return
        except Exception as e:
            await ctx.send("Exception occured: {}".format(e))
            return

    @texttriggers.command(name="remove_text_response")
    async def remove_text_response(self, ctx, reacting_text):
        """"""
