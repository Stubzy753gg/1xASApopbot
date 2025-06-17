import discord
from discord.ext import commands
import config
import logging
import asyncio

from src.commands.population import PopulationCommands

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

# Create bot instance
bot = commands.Bot(command_prefix='/', intents=intents)

# Events
@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}!')

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"Error: {error}")

# Main async entry point
async def main():
    logger.info("Adding cogs and starting bot...")
    await bot.add_cog(PopulationCommands(bot))

    token = config.DISCORD_BOT_TOKEN
    if not token:
        raise ValueError("DISCORD_BOT_TOKEN is not set in config.py or .env")

    await bot.start(token)

# Standard Python entry point
if __name__ == '__main__':
    try:
        logger.info("Starting Discord bot...")
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Error starting bot: {e}")