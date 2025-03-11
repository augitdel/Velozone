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

@app.route('/')
def debug():
    fileName = 'RecordingContext_20250214.csv'
    
    data_obj = DataAnalysis(fileName, debug=True)

    avg_lap = limit_numeric_to_2_decimals(data_obj.average_lap.values.tolist())
    fast_lap = limit_numeric_to_2_decimals(data_obj.fastest_lap.sort_values(by='fastest_lap_time').head(5).values.tolist())
    slow_lap = limit_numeric_to_2_decimals(data_obj.slowest_lap.values.tolist())
    badman = limit_numeric_to_2_decimals(data_obj.badman.values.tolist())
    diesel = limit_numeric_to_2_decimals(data_obj.diesel.values.tolist())
    electric = limit_numeric_to_2_decimals(data_obj.electric.values.tolist())

    global fast_lap_json
    fast_lap_json = json.dumps(fast_lap, indent=4)

    return render_template('debug.html', 
                           averages=avg_lap, 
                           top_laps=fast_lap, 
                           slow_lap=slow_lap, 
                           badman_lap=badman,
                           diesel=diesel,
                           electric=electric)


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