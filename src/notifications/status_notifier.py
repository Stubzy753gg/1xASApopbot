# src/cogs/status_notifier.py
import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime

# Relative imports for utils and services from src/
# Example: src/cogs/status_notifier.py -> src/ -> utils/database.py
from ..utils import database
from ..services import battlemetrics_api

class StatusNotifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # This dictionary stores the in-memory state of monitored servers
        # {server_id: {'status': 'online/offline', 'name': 'Server Name'}}
        self.last_known_server_statuses = {}
        # The background task will be started once the bot is ready
        self.check_server_status_task.start()
        print("StatusNotifier Cog initialized. Background task scheduled.")

    # Special method called when the cog is loaded (after bot is ready)
    async def cog_load(self):
        print("StatusNotifier Cog loaded. Loading initial server statuses from DB.")
        # Load initial server statuses from DB into in-memory cache
        monitored_servers_data = database.get_monitored_servers()
        for server in monitored_servers_data:
            self.last_known_server_statuses[server['server_id']] = {
                'status': server['last_known_status'],
                'name': f"Server {server['server_id']}" # Placeholder, will be updated by check_server_status_task
            }
        print(f"Loaded {len(self.last_known_server_statuses)} monitored servers into cache.")

    # Special method called when the cog is unloaded
    async def cog_unload(self):
        self.check_server_status_task.cancel()
        print("StatusNotifier Cog unloaded. Background task cancelled.")

    @tasks.loop(minutes=10) # Check every 10 minutes
    async def check_server_status_task(self):
        print(f"Running background server status check at {datetime.now()}")
        monitored_servers = database.get_monitored_servers()
        
        for server_data in monitored_servers:
            server_id = server_data['server_id']
            notify_user_id = server_data['notify_user_id']
            
            # Get server info from BattleMetrics
            server_info = await battlemetrics_api.get_server_info(server_id)

            if server_info.get("error"):
                print(f"Error checking server {server_id}: {server_info['error']}")
                # Do not update status if there's an error, assume previous status holds
                continue

            current_status = server_info['status']
            server_name = server_info['name']
            current_players = server_info['players']
            try:
                current_players_int = int(current_players)
            except (ValueError, TypeError):
                print(f"Warning: Could not convert current_players '{current_players}' to int for server {server_id}. Skipping population data insert.")
                current_players_int = 0

            # Store current population data regardless of status change (for graphing)
            database.insert_pop_data(server_id, current_players_int)

            # Retrieve last known status from in-memory cache
            last_status_info = self.last_known_server_statuses.get(server_id)

            # Initialize or update cache if server was just added or bot restarted
            if not last_status_info:
                self.last_known_server_statuses[server_id] = {
                    'status': current_status,
                    'name': server_name
                }
                database.update_monitored_server_status(server_id, current_status)
                continue # Skip notification on first check or after restart

            prev_status = last_status_info['status']

            # Check for status change: offline -> online
            if prev_status == 'offline' and current_status == 'online':
                user = self.bot.get_user(notify_user_id) # get_user is synchronous for cached users
                if user:
                    try:
                        await user.send(f"🎉 **Server Up Notification!** 🎉\n"
                                        f"Your monitored server **{server_name}** (`{server_id}`) is now **online**!\n"
                                        f"Current population: {current_players}/{server_info['maxPlayers']}")
                        print(f"Sent server up notification for {server_id} to user {user.name}")
                    except discord.Forbidden:
                        print(f"Could not send DM to {user.name}. User has DMs disabled or blocked bot.")
                        # Optionally: remove monitoring for this user if DMs consistently fail,
                        # but be careful not to spam if it's a temporary block.
                else:
                    print(f"User {notify_user_id} not found for server {server_id}. Removing from monitoring.")
                    database.remove_monitored_server(server_id) # Clean up if user is gone

            # Update last known status in memory and DB
            self.last_known_server_statuses[server_id]['status'] = current_status
            self.last_known_server_statuses[server_id]['name'] = server_name # Update name just in case
            database.update_monitored_server_status(server_id, current_status)

        # Add a small delay to respect API rate limits (even if BattleMetrics allows more)
        await asyncio.sleep(5) 

    @check_server_status_task.before_loop
    async def before_check_server_status_task(self):
        # Wait until the bot is connected and ready before starting the task
        await self.bot.wait_until_ready()

# Standard Discord.py cog setup function
async def setup(bot):
    await bot.add_cog(StatusNotifier(bot))