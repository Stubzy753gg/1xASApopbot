# config.py

import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN") # KEEP YOUR DISCORD BOT TOKEN HERE
BATTLEMETRICS_API_TOKEN = os.getenv("BATTLEMETRICS_API_TOKEN")
BATTLEMETRICS_API_BASE = "https://api.battlemetrics.com/servers/" # <-- THIS IS THE CORRECT BASE URL
# If you need a BattleMetrics API TOKEN for more advanced features or higher rate limits,
# you would add a *separate* variable for it and use it in an 'Authorization' header in battlemetrics_api.py
# Example (uncomment if you add it later):
# BATTLEMETRICS_API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbiI6IjE1MmNhOTE5ZGQyZDc3YTciLCJpYXQiOjE3NTAwNzgzNjksIm5iZiI6MTc1MDA3ODM2OSwiaXNzIjoiaHR0cHM6Ly93d3cuYmF0dGxlbWV0cmljcy5jb20iLCJzdWIiOiJ1cm46dXNlcjo5ODk3ODIifQ.SlK0gLOufUHANvUyWhDdtoewn6bILWbbg7m8Q7FB5So"
DATABASE_FILE = "data/pop_data.db"
GRAPH_MAX_POP = 70