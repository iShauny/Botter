from discord.ext import commands
import textwrap
from contextlib import redirect_stdout
import io
import traceback


class Debug:
    """Commands for bot control"""

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    async def __local_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command(pass_context=True, hidden=True, name='eval')
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = "async def func():\n{}".format(
            textwrap.indent(body, "  "))

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send("```py\n{}: {}\n```".format(
                e.__class__.__name__, e))

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send("```py\n{}{}\n```".format(value,
                                                     traceback.format_exc()))
        else:
            value = stdout.getvalue()
            if ret is None:
                if value:
                    await ctx.send("```py\n{}\n```".format(value))
            else:
                self._last_result = ret
                await ctx.send("```py\n{}{}\n```".format(value, ret))


def setup(bot):
    bot.add_cog(Debug(bot))