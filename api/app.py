from flask import Flask, render_template
from app.extra_functions import limit_numeric_to_2_decimals
from app.data_analysis_classes import DataAnalysis
from app.data_analysis import remove_initial_lap, preprocess_lap_times
#from app.Read_supabase_data import *
import pandas as pd


app = Flask(__name__, template_folder='templates')
data_objects = {}
PER_PAGE = 10

@app.route('/') 
def index():
    return render_template('index.html')

@app.route('/leaderboard/')
def leaderboard(page=1):
    start_idx = (page - 1) * PER_PAGE
    end_idx = start_idx + PER_PAGE

    avg_lap = []  
    fast_lap = []  
    slow_lap = []  
    badman = []  
    diesel = []  
    electric = [] 

    avg_lap_cut = avg_lap[start_idx:end_idx]
    total_riders = len(avg_lap)
    total_pages = (total_riders + PER_PAGE - 1) // PER_PAGE  
    next_page = page + 1 if page < total_pages else 1  
    prev_page = page - 1 if page > 1 else total_pages 
    
    return render_template('leaderboard.html', 
                           averages=avg_lap_cut, 
                           top_laps=fast_lap, 
                           slow_lap=slow_lap, 
                           badman_lap=badman,
                           diesel=diesel,
                           electric=electric,
                           next_page=next_page,
                           prev_page=prev_page,
                           page=page
    )

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