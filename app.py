from flask import Flask, render_template
from flask_socketio import SocketIO
import pandas as pd
import data_analysis
import json
import time

app = Flask(__name__, template_folder='frontend')
socketio = SocketIO(app)
fast_lap_json = json.dumps([])  # Placeholder JSON data

def get_lap_times(file):
    """
    Function that calculates the fastest lap and average lap time for each transponder
    """
    fastest_lap_times = data_analysis.fastest_lap(file)
    average_lap_times = data_analysis.average_lap_time(file)

    # Merge data for display
    lap_times = pd.merge(fastest_lap_times, average_lap_times, on='transponder_id')
    lap_times.columns = ['transponder_id', 'fastest_lap_time', 'average_lap_time']
    
    return lap_times, fastest_lap_times, average_lap_times

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
def index():
    fileName = 'RecordingContext_20250214.csv'
    
    # Load data
    _, fastest_lap_times, average_lap_times = get_lap_times(fileName)

    # Convert DataFrames to lists
    avg_lap = limit_numeric_to_2_decimals(average_lap_times.values.tolist())
    fast_lap = limit_numeric_to_2_decimals(fastest_lap_times.head(5).values.tolist())
    slow_lap = limit_numeric_to_2_decimals(data_analysis.badman(fileName)[0].values.tolist())
    badman = limit_numeric_to_2_decimals(data_analysis.badman(fileName)[1].values.tolist())
    diesel = limit_numeric_to_2_decimals(data_analysis.diesel_engine(fileName).values.tolist())

    # Convert fastest lap times to JSON
    global fast_lap_json
    fast_lap_json = json.dumps(fast_lap, indent=4)

    print(fast_lap_json)  # Debugging output

    return render_template('Website_V1.0.html', 
                           averages=avg_lap, 
                           top_laps=fast_lap, 
                           slow_lap=slow_lap, 
                           badman_lap=badman,
                           diesel=diesel)

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
