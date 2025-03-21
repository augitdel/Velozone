from flask import Flask, render_template
from app.extra_functions import limit_numeric_to_2_decimals
from app.data_analysis_classes import DataAnalysis
from app.data_analysis import remove_initial_lap, preprocess_lap_times
from app.Read_supabase_data import *
import pandas as pd
import json
import os


PER_PAGE = 10  # Number of riders per page
app = Flask(__name__, template_folder='templates')
data_objects = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/leaderboard')
def leaderboard():
    global data_objects
    start_idx = (page - 1) * PER_PAGE
    end_idx = start_idx + PER_PAGE

    # Check if data attributes exist and are not empty
    avg_lap = limit_numeric_to_2_decimals(latest_data_obj.average_lap.values.tolist())[start_idx:end_idx]
    fast_lap = limit_numeric_to_2_decimals(latest_data_obj.fastest_lap.sort_values(by='fastest_lap_time').head(5).values.tolist())
    slow_lap = limit_numeric_to_2_decimals(latest_data_obj.slowest_lap.values.tolist())
    badman = limit_numeric_to_2_decimals(latest_data_obj.badman.values.tolist()) if latest_data_obj.badman is not None else []
    diesel = limit_numeric_to_2_decimals(latest_data_obj.diesel.values.tolist()) if latest_data_obj.diesel is not None else []
    electric = limit_numeric_to_2_decimals(latest_data_obj.electric.values.tolist())

    avg_lap_cut = avg_lap[start_idx:end_idx]
    total_riders = len(avg_lap)
    total_pages = (total_riders + PER_PAGE - 1) // PER_PAGE  
    next_page = page + 1 if page < total_pages else 1  
    prev_page = page - 1 if page > 1 else total_pages  

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


@app.route('/start_session')
def start_session():
    return "Session started!"

@app.route('/stop_session')
def stop_session():
    return "Session stopped!"

@app.route('/generate_report')
def generate_report():
    return "Report generated!" 

@app.route('/names')
def names():
    return render_template('names.html')

if __name__ == '__main__':
    app.run(debug=True)