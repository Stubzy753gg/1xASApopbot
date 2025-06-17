# src/utils/database.py
import sqlite3
import os
import time
from datetime import datetime, timedelta

# This import statement is crucial.
# It means: Go up two directories (src/utils/ -> src/ -> discord_pop_bot/)
# then find the 'config' module (config.py).
import config

def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    Ensures the 'data' directory exists for the database file.
    """
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(config.DATABASE_FILE), exist_ok=True)
    conn = sqlite3.connect(config.DATABASE_FILE)
    # Allows accessing columns by name (e.g., row['column_name'] instead of row[0])
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
    """
    Initializes the database by creating necessary tables if they don't exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table to store historical population data for graphing
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS population_data (
            server_id TEXT NOT NULL,
            timestamp INTEGER NOT NULL, -- Unix timestamp
            population INTEGER NOT NULL,
            PRIMARY KEY (server_id, timestamp) -- Ensures unique entries per server at a given time
        );
    ''')

    # Table to store servers being monitored for online/offline notifications
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monitored_servers (
            server_id TEXT PRIMARY KEY, -- Unique ID for the server being monitored
            notify_user_id INTEGER NOT NULL, -- Discord User ID to notify
            last_known_status TEXT DEFAULT 'unknown', -- 'online', 'offline', 'dead'
            last_status_check INTEGER DEFAULT 0 -- Unix timestamp of last check
        );
    ''')
    conn.commit()
    conn.close()

def insert_pop_data(server_id: str, population: int):
    """
    Inserts or updates population data for a given server and timestamp.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = int(time.time()) # Current Unix timestamp
    cursor.execute('INSERT OR REPLACE INTO population_data (server_id, timestamp, population) VALUES (?, ?, ?)',
                   (server_id, timestamp, population))
    conn.commit()
    conn.close()

def get_pop_data_for_hours(server_id: str, hours: int = 24):
    """
    Retrieves population data for a specific server for the last 'hours'.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cutoff_time = int(time.time()) - (hours * 3600) # Calculate timestamp 'hours' ago
    cursor.execute('SELECT timestamp, population FROM population_data WHERE server_id = ? AND timestamp >= ? ORDER BY timestamp ASC',
                   (server_id, cutoff_time))
    data = cursor.fetchall()
    conn.close()
    return [{'timestamp': row['timestamp'], 'population': row['population']} for row in data]

def get_pop_data_for_week(server_id: str):
    """
    Retrieves population data for a specific server for the last 7 days.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cutoff_time = int(time.time()) - (7 * 24 * 3600) # 7 days in seconds
    cursor.execute('SELECT timestamp, population FROM population_data WHERE server_id = ? AND timestamp >= ? ORDER BY timestamp ASC',
                   (server_id, cutoff_time))
    data = cursor.fetchall()
    conn.close()
    return [{'timestamp': row['timestamp'], 'population': row['population']} for row in data]

def add_monitored_server(server_id: str, user_id: int):
    """
    Adds or updates a server to be monitored for online notifications by a specific user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    # INSERT OR REPLACE handles both adding new and updating existing (if primary key matches)
    cursor.execute('INSERT OR REPLACE INTO monitored_servers (server_id, notify_user_id) VALUES (?, ?)',
                   (server_id, user_id))
    conn.commit()
    conn.close()

def get_monitored_servers():
    """
    Retrieves a list of all servers currently being monitored.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT server_id, notify_user_id, last_known_status, last_status_check FROM monitored_servers')
    servers = cursor.fetchall()
    conn.close()
    # Return as a list of dictionaries for easier access
    return [{'server_id': row['server_id'], 'notify_user_id': row['notify_user_id'],
             'last_known_status': row['last_known_status'], 'last_status_check': row['last_status_check']}
            for row in servers]

def update_monitored_server_status(server_id: str, new_status: str):
    """
    Updates the last known status and check time for a monitored server.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = int(time.time())
    cursor.execute('UPDATE monitored_servers SET last_known_status = ?, last_status_check = ? WHERE server_id = ?',
                   (new_status, timestamp, server_id))
    conn.commit()
    conn.close()

def remove_monitored_server(server_id: str):
    """
    Removes a server from the monitoring list.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM monitored_servers WHERE server_id = ?', (server_id,))
    conn.commit()
    conn.close()