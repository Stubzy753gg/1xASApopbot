# src/commands/population.py

import discord
from discord.ext import commands
from src.services.battlemetrics_api import (
    find_ark_server_by_number,
    get_server_info,
    search_asa_official_servers
)

class PopulationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='pop', usage='<ark_server_number or battlemetrics_server_id>')
    async def pop(self, ctx, server_id_or_number: str):
        """
        /pop <ark_server_number or battlemetrics_server_id>
        """
        await ctx.send(f"Fetching population for `{server_id_or_number}`...")

        # Try as BattleMetrics server ID first
        server_info = await get_server_info(server_id_or_number)
        if server_info.get("error"):
            # If not found, try as Ark server number
            server = await find_ark_server_by_number(server_id_or_number)
            if not server:
                await ctx.send("❌ That server was not found or is not available.")
                return
            # Now get full info by BattleMetrics ID
            server_id = server["id"]
            server_info = await get_server_info(server_id)
            if server_info.get("error"):
                await ctx.send("❌ That server was not found or is not available.")
                return

        # --- Validation for Ark Survival Ascended Official servers only ---
        if str(server_info.get("gameId")) != "48815":
            await ctx.send("❌ That server is not an Ark: Survival Ascended server.")
            return

        details = server_info.get("details", {})
        name = server_info.get("name", "").lower()
        is_official = False
        if isinstance(details, dict):
            is_official = details.get("official", False)
        if not is_official and "official" not in name:
            await ctx.send("❌ That server is not an official server.")
            return

        # Display info
        players = server_info['players']
        max_players = server_info['maxPlayers']
        server_name = server_info['name']
        status = server_info['status']
        ip = server_info.get("ip", "N/A")
        port = server_info.get("port", "N/A")
        server_id = server_info.get("id", server_id_or_number)
        link = f"https://www.battlemetrics.com/servers/asa/{server_id}"

        embed = discord.Embed(
            title=f"📊 {server_name} Population",
            description=f"**Server ID:** `{server_id}`",
            color=0x57F287 if status == 'online' else 0xED4245
        )
        embed.add_field(name="Status", value=status.capitalize(), inline=True)
        embed.add_field(name="Players", value=f"{players}/{max_players}", inline=True)
        embed.add_field(name="Connect", value=f"`{ip}:{port}`", inline=False)
        embed.add_field(
            name="BattleMetrics Link",
            value=f"[View Server]({link})",
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command(name='findasa', usage='<search_term>')
    async def findasa(self, ctx, *, search_term: str):
        servers = await search_asa_official_servers(search_term)
        if not servers:
            await ctx.send("No Ark Official servers found for that search.")
            return
        msg = "**Matching Ark Official Servers:**\n"
        for server in servers:
            name = server["attributes"]["name"]
            sid = server["id"]
            players = server["attributes"]["players"]
            max_players = server["attributes"]["maxPlayers"]
            msg += f"**{name}** (ID: `{sid}`) - {players}/{max_players} players\n"
        await ctx.send(msg)

    @commands.command(name="findserver", help="Find an ARK server by its number.")
    async def findserver(self, ctx, server_number: str):
        server = await find_ark_server_by_number(server_number)
        if server:
            name = server["attributes"]["name"]
            players = server["attributes"]["players"]
            max_players = server["attributes"]["maxPlayers"]
            await ctx.send(f"Found server: **{name}**\nPopulation: {players}/{max_players}")
        else:
            await ctx.send("Server not found.")

async def setup(bot):
    await bot.add_cog(PopulationCommands(bot))