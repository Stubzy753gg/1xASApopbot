# src/commands/graph.py
import discord
from discord.ext import commands

# Relative imports from the src directory structure
# Example: src/commands/graph.py -> src/ -> utils/database.py
from ..utils import database
from ..utils import graph # This imports the graph plotting functions

class GraphCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='graphday', usage='<battlemetrics_server_id>')
    async def graph_day(self, ctx, server_id: str):
        """Shows a 24-hour population graph for the specified server."""
        await ctx.send(f"Generating daily graph for server `{server_id}`. This might take a moment...")

        data = database.get_pop_data_for_hours(server_id, hours=24)

        if len(data) < 2: # Need at least 2 points to draw a line
            await ctx.send("Not enough data to generate a 24-hour graph yet. Please try again after some time or use `/pop` to record more data.")
            return

        try:
            graph_buffer, min_info_msg, max_info_msg = graph.generate_day_graph(server_id, data)
            if graph_buffer is None:
                await ctx.send("Failed to generate the daily graph image.")
                return
            file = discord.File(graph_buffer, filename="day_pop_graph.png")
            
            await ctx.send(
                f"**Daily Population Graph for {server_id}**\n"
                f"**Highest Pop:** {max_info_msg}\n"
                f"**Lowest Pop:** {min_info_msg}",
                file=file
            )
        except Exception as e:
            print(f"Error generating daily graph for {server_id}: {e}")
            await ctx.send(f"An error occurred while generating the graph: `{e}`")


    @commands.command(name='graphweek', usage='<battlemetrics_server_id>')
    async def graph_week(self, ctx, server_id: str):
        """Shows a 7-day population graph and weekly trends for the specified server."""
        await ctx.send(f"Generating weekly graph for server `{server_id}`. This might take a moment...")

        data = database.get_pop_data_for_week(server_id)

        # A more reasonable check for weekly data, e.g., at least 1 day's worth of points (24 entries)
        if len(data) < 24:
            await ctx.send("Not enough data to generate a 7-day graph yet. Please try again after more data has been collected.")
            return

        try:
            graph_buffer, summary_message = graph.generate_week_graph(server_id, data)
            if graph_buffer is None:
                await ctx.send("Failed to generate the weekly graph image.")
                return
            file = discord.File(graph_buffer, filename="week_pop_graph.png")
            
            await ctx.send(
                f"**Weekly Population Graph for {server_id}**\n"
                f"{summary_message}",
                file=file
            )
        except Exception as e:
            print(f"Error generating weekly graph for {server_id}: {e}")
            await ctx.send(f"An error occurred while generating the graph: `{e}`")

# Standard Discord.py cog setup function
async def setup(bot):
    await bot.add_cog(GraphCommands(bot))