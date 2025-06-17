import aiohttp
import re
import config

async def find_ark_server_by_number(server_number: str):
    """
    Find an Ark: Survival Ascended official server by its Ark server number.
    Returns the full server object or None.
    """
    url = "https://api.battlemetrics.com/servers"
    params = {
        "filter[game]": "ark-survival-ascended",
        "filter[official]": "true",
        "filter[search]": f"Official {server_number}",
        "page[size]": 10
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            servers = data.get("data", [])
            # Match pattern: REGION-MODE-Official-MAP{server_number}
            pattern = re.compile(rf"^[A-Z]{{2}}-(PVE|PVP)-Official-.*{re.escape(server_number)}\b", re.IGNORECASE)
            for server in servers:
                name = server["attributes"]["name"]
                if pattern.search(name):
                    return server
            # Fallback: any server with the number in the name
            for server in servers:
                if server_number in server["attributes"]["name"]:
                    return server
            return None

async def search_asa_official_servers(search_term):
    """
    Search for Ark: Survival Ascended official servers matching the search term.
    Returns a list of server objects.
    """
    url = "https://api.battlemetrics.com/servers"
    params = {
        "filter[game]": "ark-survival-ascended",
        "filter[official]": "true",
        "filter[search]": search_term,
        "page[size]": 5
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            return data.get("data", [])

async def get_server_info(server_id: str):
    """
    Fetch server info from BattleMetrics by server ID.
    Returns a dict with server info or {"error": "..."} on failure.
    """
    url = f"https://api.battlemetrics.com/servers/{server_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return {"error": f"HTTP {resp.status}"}
            data = await resp.json()
            attributes = data.get("data", {}).get("attributes", {})
            relationships = data.get("data", {}).get("relationships", {})
            # Extract gameId from relationships
            game_id = None
            if 'game' in relationships and 'data' in relationships['game']:
                game_id = relationships['game']['data'].get('id')
            # Check if this is an Ark: Survival Ascended server
            if game_id != "48815":
                return {"error": "Not an Ark: Survival Ascended server"}
            return {
                "status": attributes.get("status"),
                "name": attributes.get("name"),
                "players": attributes.get("players"),
                "maxPlayers": attributes.get("maxPlayers"),
                "details": attributes.get("details", {}),
                "gameId": game_id,
                "id": data.get("data", {}).get("id"),
                "ip": attributes.get("ip"),
                "port": attributes.get("port"),
            }