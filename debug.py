from flask import Flask, render_template, redirect, url_for
from flask_socketio import SocketIO
import pandas as pd
from data_analysis_classes import DataAnalysis
import json
import time
import threading

PER_PAGE = 10  # Number of riders per page

app = Flask(__name__, template_folder='frontend')
socketio = SocketIO(app)
fast_lap_json = json.dumps([])  # Placeholder JSON data
stop_thread = False

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
    global data_obj

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

from flask import Flask, render_template, redirect, url_for
from flask_socketio import SocketIO
import pandas as pd
from data_analysis_classes import DataAnalysis
import json
import time
import threading

PER_PAGE = 10  # Number of riders per page

app = Flask(__name__, template_folder='frontend')
socketio = SocketIO(app)
fast_lap_json = json.dumps([])  # Placeholder JSON data
stop_thread = False  # Flag to control the loop

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
    global data_obj

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
    socketio.emit('update_data', fast_lap_json)

def read_csv_in_chunks():
    global data_obj, stop_thread
    fileName = 'RecordingContext_20250214.csv'
    chunk_size = 1000  # Number of lines to read per chunk

    try:
        while not stop_thread:
            for chunk in pd.read_csv(fileName, chunksize=chunk_size):
                if stop_thread:
                    break
                data_obj.update(chunk)  # Assuming DataAnalysis has an update method

                # Prepare all the data to be sent
                data_to_send = {
                    'fastest_lap': limit_numeric_to_2_decimals(data_obj.fastest_lap.sort_values(by='fastest_lap_time').head(5).values.tolist()),
                    'average_lap': limit_numeric_to_2_decimals(data_obj.average_lap.values.tolist()),
                    'slow_lap': limit_numeric_to_2_decimals(data_obj.slowest_lap.values.tolist()),
                    'badman': limit_numeric_to_2_decimals(data_obj.badman.values.tolist()),
                    'diesel': limit_numeric_to_2_decimals(data_obj.diesel.values.tolist()),
                    'electric': limit_numeric_to_2_decimals(data_obj.electric.values.tolist())
                }

                # Emit all the data
                socketio.emit('update_data', json.dumps(data_to_send, indent=4))
                time.sleep(10)  # Wait for 10 seconds before reading the next chunk
    except KeyboardInterrupt:
        print("CSV file reading stopped by user.")
    finally:
        socketio.stop()  # Ensure the socket is properly closed

if __name__ == '__main__':
    initial_file = 'RecordingContext_20250214.csv'
    data_obj = DataAnalysis(initial_file, debug=True)  # Initialize with a subset of the CSV file

    try:
        thread = threading.Thread(target=read_csv_in_chunks)
        thread.start()
        socketio.run(app, debug=True,use_reloader=False)
    except KeyboardInterrupt:
        print("Application stopped by user.")
        stop_thread = True
        thread.join()  # Wait for the thread to finish