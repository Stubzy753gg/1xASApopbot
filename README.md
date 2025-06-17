Discord Ark Survival Ascended Pop Bot
A Discord bot to track Ark: Survival Ascended server population using BattleMetrics API, provide real-time updates, server online notifications, and visualize historical data with graphs.

Features
/pop <server_id>: Get current player count and server status.
/addserverup <server_id>: Get a direct message notification when a specified server comes online after being offline.
/removeserverup <server_id>: Stop receiving notifications for a server.
/graphday <server_id>: Visualize 24-hour population trends with a line graph, highlighting min/max pop times.
/graphweek <server_id>: Visualize 7-day average hourly population trends with a line graph and summarize weekly high/low times.

Setup & Installation
Clone the repository (or download the files):
git clone https://github.com/your-username/discord-ark-pop-bot.git
cd discord-ark-pop-bot

Create a Python Virtual Environment (Recommended):
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source ./.venv/bin/activate

Install Dependencies:
pip install -r requirements.txt

Create a Discord Bot:
Go to the Discord Developer Portal.
Click "New Application", give it a name (e.g., "Ark Pop Bot").
Go to "Bot" on the left sidebar, then "Add Bot".
Under "Privileged Gateway Intents", enable "Message Content Intent" and "Members Intent".
Click "Reset Token" and copy the token. Keep this token secret!

Configure the Bot (config.py):
Open config.py.
Replace "YOUR_DISCORD_BOT_TOKEN_HERE" with the bot token you copied.
Adjust GRAPH_MAX_POP if your server's population frequently exceeds 70.

Invite the Bot to Your Server:
In the Discord Developer Portal, go to "OAuth2" -> "URL Generator".
Select "bot" scope.
Under "Bot Permissions", select:
Send Messages
Embed Links (good for rich messages later, though not explicitly used now)
Attach Files (necessary for graphs)
Copy the generated URL and paste it into your web browser. Select your server to invite the bot.

Run the Bot:
python bot.py

The bot should now be online in your Discord server.

Usage
(See "Features" section above for commands)

BattleMetrics Server ID
To use the bot, you'll need the numerical BattleMetrics ID for your Ark: Survival Ascended server. You can find this by searching for your server on battlemetrics.com. When you view your server's page, the ID is part of the URL (e.g., https://www.battlemetrics.com/servers/ase/1234567, where 1234567 is the ID).

To use the bot, you'll need the numerical BattleMetrics ID for your Ark: Survival Ascended server. You can find this by searching for your server on [battlemetrics.com](https://www.battlemetrics.com/). When you view your server's page, the ID is part of the URL (e.g., `https://www.battlemetrics.com/servers/ase/1234567`, where `1234567` is the ID).

---

# Ark Discord Bot

## How to upload to GitHub

1. Initialize git (if not already done):
   ```
   git init
   ```

2. Add all files:
   ```
   git add .
   ```

3. Commit your changes:
   ```
   git commit -m "Initial commit"
   ```

4. Create a new repository on GitHub and copy its URL.

5. Add the remote:
   ```
   git remote add origin <your-repo-url>
   ```

6. Push your code:
   ```
   git push -u origin main
   ```
   *(or use `master` if that's your default branch)*

**Note:**  
Your `.env` file is ignored and will not be uploaded.
