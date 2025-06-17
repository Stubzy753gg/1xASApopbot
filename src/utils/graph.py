# src/utils/graph.py
import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta
import numpy as np

# config.py is two levels up from src/utils/
# Example: src/utils/graph.py -> src/ -> discord_pop_bot/ -> config.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
import config

# Discord Dark Theme Colors
DISCORD_BG = '#2F3136'
DISCORD_PRIMARY_TEXT = '#DCDDDE'
DISCORD_SECONDARY_TEXT = '#909192' # For axis labels, ticks
DISCORD_LINE_COLOR = '#5865F2' # A nice blue
DISCORD_ACCENT_COLOR = '#57F287' # Green for high, red for low (or other contrasts)
DISCORD_ERROR_COLOR = '#ED4245'

def setup_plot_style(ax):
    fig = ax.figure
    fig.patch.set_facecolor(DISCORD_BG) # Outer figure background
    ax.set_facecolor(DISCORD_BG) # Plot area background

    # Axis colors and labels
    ax.tick_params(axis='x', colors=DISCORD_SECONDARY_TEXT)
    ax.tick_params(axis='y', colors=DISCORD_SECONDARY_TEXT)
    ax.xaxis.label.set_color(DISCORD_SECONDARY_TEXT)
    ax.yaxis.label.set_color(DISCORD_SECONDARY_TEXT)

    # Spines (borders)
    ax.spines['bottom'].set_color(DISCORD_SECONDARY_TEXT)
    ax.spines['top'].set_color(DISCORD_SECONDARY_TEXT)
    ax.spines['left'].set_color(DISCORD_SECONDARY_TEXT)
    ax.spines['right'].set_color(DISCORD_SECONDARY_TEXT)

    # Grid (optional, but can help readability)
    ax.grid(False) # Keep it clean like the example

def generate_day_graph(server_id: str, data: list):
    if not data:
        return None, "No data available for the last 24 hours.", ""

    # Sort data by timestamp (BattleMetrics sometimes returns out of order)
    data.sort(key=lambda x: x['timestamp'])

    # Convert timestamps to datetime objects
    timestamps = [datetime.fromtimestamp(d['timestamp']) for d in data]
    populations = [d['population'] for d in data]

    # Calculate "hours ago" for x-axis labels
    now = datetime.now()
    hours_ago_raw = [(now - ts).total_seconds() / 3600 for ts in timestamps]

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    setup_plot_style(ax)

    ax.plot(hours_ago_raw, populations, color=DISCORD_LINE_COLOR, marker='o', linestyle='-')

    # Invert x-axis to show 0 hours ago on the right (current)
    ax.set_xlim(24, 0) # 0-24 hours ago, right-to-left
    ax.set_ylim(0, config.GRAPH_MAX_POP)

    ax.set_xlabel('Hours Ago', color=DISCORD_SECONDARY_TEXT)
    ax.set_ylabel('Server Population', color=DISCORD_SECONDARY_TEXT)

    # Set x-axis ticks to show every hour
    ax.set_xticks(np.arange(0, 25, 1))
    ax.set_xticklabels([f"{int(h)} hours ago" if h != 0 else "Now" for h in np.arange(0, 25, 1)],
                       rotation=45, ha='right', fontsize=8, color=DISCORD_SECONDARY_TEXT)
    ax.set_yticks(np.arange(0, config.GRAPH_MAX_POP + 1, 4)) # Example: 0, 4, 8, ...

    # Highlight min/max and notate
    min_msg = "N/A"
    max_msg = "N/A"
    if populations:
        min_pop = min(populations)
        max_pop = max(populations)
        min_idx = populations.index(min_pop)
        max_idx = populations.index(max_pop)

        min_time_ago = hours_ago_raw[min_idx]
        max_time_ago = hours_ago_raw[max_idx]

        ax.plot(min_time_ago, min_pop, 'o', color=DISCORD_ERROR_COLOR, markersize=8, label=f'Min: {min_pop}')
        ax.plot(max_time_ago, max_pop, 'o', color=DISCORD_ACCENT_COLOR, markersize=8, label=f'Max: {max_pop}')

        # Use actual time from data point for message
        min_msg = f"{min_pop} at {datetime.fromtimestamp(data[min_idx]['timestamp']).strftime('%I:%M %p')}"
        max_msg = f"{max_pop} at {datetime.fromtimestamp(data[max_idx]['timestamp']).strftime('%I:%M %p')}"


    # Add current population large in the middle
    current_pop = populations[-1] if populations else 0
    ax.text(ax.get_xlim()[0] / 2, config.GRAPH_MAX_POP / 2, str(current_pop),
            horizontalalignment='center', verticalalignment='center',
            transform=ax.transData, fontsize=60, color=DISCORD_SECONDARY_TEXT, alpha=0.5)

    # Add title bar elements
    current_time_str = datetime.now().strftime("%m/%d/%Y %I:%M %p")
    fig.text(0.05, 0.95, "👁️‍🗨️  Pop Tracker APP", fontsize=14, color=DISCORD_PRIMARY_TEXT,
             ha='left', va='top', transform=fig.transFigure)
    fig.text(0.95, 0.95, current_time_str, fontsize=10, color=DISCORD_SECONDARY_TEXT,
             ha='right', va='top', transform=fig.transFigure)


    plt.tight_layout(rect=(0, 0, 1, 0.9)) # Adjust layout to make space for title text
    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=DISCORD_BG)
    buf.seek(0)
    plt.close(fig) # Close the figure to free memory

    return buf, min_msg, max_msg

def generate_week_graph(server_id: str, data: list):
    if not data:
        return None, "No data available for the last 7 days."

    data.sort(key=lambda x: x['timestamp'])

    # Aggregate data by hour of the day for each day
    # Structure: {weekday_hour: [pop1, pop2, ...]}
    hourly_pops = {}
    # Structure for daily min/max times: {weekday: {'min_pop': val, 'min_time': hour, 'max_pop': val, 'max_time': hour}}
    daily_min_max = {}

    for entry in data:
        dt_obj = datetime.fromtimestamp(entry['timestamp'])
        weekday = dt_obj.weekday() # Monday 0, Sunday 6
        hour = dt_obj.hour
        
        key = (weekday, hour)
        if key not in hourly_pops:
            hourly_pops[key] = []
        hourly_pops[key].append(entry['population'])

        # Track daily min/max for specific hours
        day_key = weekday
        if day_key not in daily_min_max:
            daily_min_max[day_key] = {'min_pop': float('inf'), 'min_time': None, 'max_pop': float('-inf'), 'max_time': None}

        current_pop = entry['population']
        # Only update min/max if we have data for that hour
        if current_pop < daily_min_max[day_key]['min_pop']:
            daily_min_max[day_key]['min_pop'] = current_pop
            daily_min_max[day_key]['min_time'] = hour
        if current_pop > daily_min_max[day_key]['max_pop']:
            daily_min_max[day_key]['max_pop'] = current_pop
            daily_min_max[day_key]['max_time'] = hour

    # Calculate average population for each hour of the week
    avg_hourly_pops = {}
    for (weekday, hour), pops in hourly_pops.items():
        avg_hourly_pops[(weekday, hour)] = sum(pops) / len(pops)

    # Prepare data for plotting
    x_labels = []
    y_values = []
    plot_points = [] # To store (x_index, avg_pop) for plotting

    # Day mapping for labels
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Generate labels and data points for each hour of each day
    # Iterate through days and then hours to ensure proper order on graph
    x_index = 0
    # Start from 6 days ago (Monday), loop up to today (Sunday)
    # Get the current day's weekday (e.g., if today is Thursday, start from previous Friday)
    today_weekday = datetime.now().weekday()
    
    # Create an ordered list of weekdays starting from 6 days ago to today
    ordered_weekdays = []
    for i in range(7):
        ordered_weekdays.append((today_weekday - 6 + i) % 7)

    for current_weekday in ordered_weekdays:
        for hour in range(24):
            key = (current_weekday, hour)
            avg_pop = avg_hourly_pops.get(key, 0) # Default to 0 if no data
            y_values.append(avg_pop)
            plot_points.append((x_index, avg_pop))
            
            # Create a label every 6 hours or at start of day
            if hour % 6 == 0 or hour == 0:
                x_labels.append(f"{day_names[current_weekday]} {hour:02d}:00")
            else:
                x_labels.append("") # Empty label for intermediate ticks

            x_index += 1

    # Create the plot
    fig, ax = plt.subplots(figsize=(15, 7)) # Wider for weekly data
    setup_plot_style(ax)

    # Plot the line
    x_coords = [p[0] for p in plot_points]
    y_coords = [p[1] for p in plot_points]
    ax.plot(x_coords, y_coords, color=DISCORD_LINE_COLOR, marker='o', linestyle='-', markersize=3)

    ax.set_xlim(0, len(x_labels) - 1)
    ax.set_ylim(0, config.GRAPH_MAX_POP)

    ax.set_xlabel('Day and Hour', color=DISCORD_SECONDARY_TEXT)
    ax.set_ylabel('Avg. Server Population', color=DISCORD_SECONDARY_TEXT)

    # Set x-axis ticks and labels
    ax.set_xticks(range(len(x_labels)))
    ax.set_xticklabels(x_labels, rotation=60, ha='right', fontsize=8, color=DISCORD_SECONDARY_TEXT)
    ax.set_yticks(np.arange(0, config.GRAPH_MAX_POP + 1, 5))

    # Add current population large in the middle (optional for weekly, but can be done)
    populations = [d['population'] for d in data] if data else []
    current_pop = populations[-1] if populations else 0 # Get last known pop for display
    ax.text(ax.get_xlim()[1] / 2, config.GRAPH_MAX_POP / 2, str(current_pop),
            horizontalalignment='center', verticalalignment='center',
            transform=ax.transData, fontsize=60, color=DISCORD_SECONDARY_TEXT, alpha=0.5)

    # Add title bar elements
    current_time_str = datetime.now().strftime("%m/%d/%Y %I:%M %p")
    fig.text(0.05, 0.95, "👁️‍🗨️  Pop Tracker APP", fontsize=14, color=DISCORD_PRIMARY_TEXT,
             ha='left', va='top', transform=fig.transFigure)
    fig.text(0.95, 0.95, current_time_str, fontsize=10, color=DISCORD_SECONDARY_TEXT,
             ha='right', va='top', transform=fig.transFigure)

    plt.tight_layout(rect=(0, 0, 1, 0.9))
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=DISCORD_BG)
    buf.seek(0)
    plt.close(fig)

    # Summarize weekly trends (text message)
    summary_messages = ["**Weekly Population Trends (Avg. per day):**"]
    # Ensure consistent order of days for the summary
    for weekday in ordered_weekdays:
        day_name = day_names[weekday]
        if weekday in daily_min_max and daily_min_max[weekday]['min_time'] is not None:
            min_info = daily_min_max[weekday]
            summary_messages.append(
                f"- **{day_name}:** Lowest Avg Pop around {min_info['min_time']:02d}:00 ({min_info['min_pop']:.0f} players)"
                f", Highest Avg Pop around {min_info['max_time']:02d}:00 ({min_info['max_pop']:.0f} players)"
            )
        else:
            summary_messages.append(f"- **{day_name}:** Not enough data.")
    
    return buf, "\n".join(summary_messages)