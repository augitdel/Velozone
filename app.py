from flask import Flask, render_template, redirect, url_for
from flask_socketio import SocketIO
import pandas as pd
from data_analysis_classes import DataAnalysis
import json
import time

PER_PAGE = 10  # Number of riders per page

app = Flask(__name__, template_folder='frontend')
socketio = SocketIO(app)
fast_lap_json = json.dumps([])  # Placeholder JSON data

def limit_numeric_to_2_decimals(data):
    # Function to limit numeric values to 2 decimal places
    if isinstance(data, list):
        return [limit_numeric_to_2_decimals(item) for item in data]
    elif isinstance(data, dict):
        return {key: limit_numeric_to_2_decimals(value) for key, value in data.items()}
    elif isinstance(data, float):
        return round(data, 2)
    else:
        return data

@app.route('/', defaults={'page': 1})  # Default to page 1
@app.route('/index/<int:page>')
def index(page):
    fileName = 'RecordingContext_20250214.csv'
    
    data_obj = DataAnalysis(fileName, debug=True)

    start_idx = (page - 1) * PER_PAGE
    end_idx = start_idx + PER_PAGE

    avg_lap = limit_numeric_to_2_decimals(data_obj.average_lap.values.tolist())
    avg_lap_cut = avg_lap[start_idx:end_idx]
    fast_lap = limit_numeric_to_2_decimals(data_obj.fastest_lap.sort_values(by='fastest_lap_time').head(5).values.tolist())
    slow_lap = limit_numeric_to_2_decimals(data_obj.slowest_lap.values.tolist())
    badman = limit_numeric_to_2_decimals(data_obj.badman.values.tolist())
    diesel = limit_numeric_to_2_decimals(data_obj.diesel.values.tolist())
    electric = limit_numeric_to_2_decimals(data_obj.electric.values.tolist())

    total_riders = len(avg_lap)
    total_pages = (total_riders + PER_PAGE - 1) // PER_PAGE  # Calculate total pages
    next_page = page + 1 if page < total_pages else 1  # Loop back to first page
    prev_page = page - 1 if page > 1 else total_pages  # Loop back to last page

    global fast_lap_json
    fast_lap_json = json.dumps(fast_lap, indent=4)

    return render_template('index.html', 
                           averages=avg_lap_cut, 
                           top_laps=fast_lap, 
                           slow_lap=slow_lap, 
                           badman_lap=badman,
                           diesel=diesel,
                           electric=electric,
                           next_page=next_page,
                           prev_page=prev_page,
                           page=page)
# @app.route('/index2')
# def index2():
#     print('Rendering index2')
#     fileName = 'RecordingContext_20250214.csv'
    
#     # Use the DataAnalysis class instance
#     data_obj = DataAnalysis(fileName, debug=True)

#     # Convert DataFrames to lists for rendering
#     avg_lap = limit_numeric_to_2_decimals(data_obj.average_lap.values.tolist())
#     fast_lap = limit_numeric_to_2_decimals(data_obj.fastest_lap.sort_values(by='fastest_lap_time').head(5).values.tolist()) 
#     slow_lap = limit_numeric_to_2_decimals(data_obj.slowest_lap.values.tolist())
#     badman = limit_numeric_to_2_decimals(data_obj.badman.values.tolist())
#     diesel = limit_numeric_to_2_decimals(data_obj.diesel.values.tolist())
#     electric = limit_numeric_to_2_decimals(data_obj.electric.values.tolist())

#     # Convert fastest lap times to JSON
#     global fast_lap_json
#     fast_lap_json = json.dumps(fast_lap, indent=4)

#     print(fast_lap_json)  # Debugging output

#     return render_template('index2.html', 
#                            averages=avg_lap, 
#                            top_laps=fast_lap, 
#                            slow_lap=slow_lap, 
#                            badman_lap=badman,
#                            diesel=diesel,
#                            electric=electric)


@socketio.on('connect')
def handle_connect():
    print("Client connected")
    socketio.emit('fast_lap_data', fast_lap_json)

def send_fast_lap_times():
    while True:
        socketio.emit('fast_lap_data', fast_lap_json)
        time.sleep(1)  # Simulate real-time updates

if __name__ == '__main__':
    socketio.run(app, debug=True)
