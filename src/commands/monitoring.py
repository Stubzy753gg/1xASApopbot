# src/commands/monitoring.py
import discord
from discord.ext import commands

# Relative imports from the src directory structure
# Example: src/commands/monitoring.py -> src/ -> utils/database.py
from ..utils import database
from ..services import battlemetrics_api
from src.services.battlemetrics_api import find_ark_server_by_number

class MonitoringCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='addserverup', usage='<battlemetrics_server_id>')
    async def add_server_up(self, ctx, server_id: str):
        """Registers a server to get a notification when it comes online."""
        # First, verify the server ID exists on BattleMetrics
        server_info = await battlemetrics_api.get_server_info(server_id)
        if server_info.get("error"):
            await ctx.send(f"Could not add server: {server_info['error']}")
            return

        database.add_monitored_server(server_id, ctx.author.id)
        # Note: The in-memory cache in StatusNotifier will be updated on its next loop.
        # For immediate consistency, you could add an explicit update call to StatusNotifier if needed,
        # but the next background check will sync it.

        await ctx.send(f"Server `{server_id}` ({server_info['name']}) has been added for online notifications. I will @ you when it comes online if it crashes.")

    @commands.command(name='removeserverup', usage='<battlemetrics_server_id>')
    async def remove_server_up(self, ctx, server_id: str):
        """Removes a server from online notification monitoring."""
        database.remove_monitored_server(server_id)
        # Note: Similar to add, the in-memory cache in StatusNotifier will sync on its next loop.
        await ctx.send(f"Server `{server_id}` removed from online notifications.")

    @commands.command(name="monitorserver", help="Monitor an ARK server by its number.")
    async def monitorserver(self, ctx, server_number: str):
        server = await find_ark_server_by_number(server_number)
        if server:
            # Logic to add server to monitoring
            await ctx.send(f"Now monitoring server: **{server['attributes']['name']}**")
        else:
            await ctx.send("Server not found.")

# Standard Discord.py cog setup function
async def setup(bot):
    await bot.add_cog(MonitoringCommands(bot))