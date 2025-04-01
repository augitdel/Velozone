from flask import Flask, render_template, request, url_for, redirect, session, send_from_directory,jsonify
from flask_cors import CORS
from transponder_names import TransponderDataBase
# from data_analysis_branch import DataAnalysis
from flask_cors import CORS 
from flask_session import Session
from data_analysis_branch import DataAnalysis
# from extra_functions import limit_numeric_to_2_decimals
# from data_analysis_classes import DataAnalysis
# from data_analysis import remove_initial_lap, preprocess_lap_times
# from Read_supabase_data import *
import pandas as pd
import os
import redis
import time


app = Flask(__name__, template_folder='templates')
app.secret_key = os.urandom(24)

PDF_DIR = os.path.join(app.root_path, "tmp")
PDF_PATH = os.path.join(PDF_DIR, "rider_report_UGent.pdf")

CORS(app)


session_active = False
session_stopped = False

changed_lines = pd.DataFrame()
session_data_analysis = []
names_dict = {}
names_database = {}
# Configure session management
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_PERMANENT"] = True  # Make sessions persistent across browser sessions
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_KEY_PREFIX"] = "velozone_session:"
app.config["SESSION_REDIS"] = redis.from_url(os.environ.get("REDIS_URL")) # Configure your Redis URL

Session(app)

PER_PAGE = 10
PDF_DIR = os.path.join(app.root_path, "tmp")
PDF_PATH = os.path.join(PDF_DIR, "rider_report_UGent.pdf")

CORS(app) # Enable CORS for development

# INITIALIZE THE DATAFRAMES
changed_lines = []
session_data_analysis = []
# We create a Database variable
names_dict = TransponderDataBase()

# Home screen
@app.route('/') 
@app.route('/home', methods=['GET', 'POST'])
def home():
    global names_dict
    competition_data = session.get('competition', None)
    #Initialize the flags
    if 'session_active' not in session:
        session['session_active'] = False
    if 'session_closed' not in session:
        session['session_closed'] = False
    if request.method == 'POST':
        data = request.json
        if data:
            names_dict = {item['transponder_id']: item['name'] for item in data}
            names_database = TransponderDataBase()
            names_database.update(names_dict)
            session['transponders'] = names_database.get_database
            print("Received data:", names_database.get_database)
            return jsonify({"message": "Transponder data opgeslagen!", "data": names_database.get_database}), 200
            
        else:
            return jsonify({"error": "Geen data ontvangen"}), 400
    competition_data = session.get('competition', None)
    return render_template('index.html', competition=competition_data)


@app.route('/leaderboard/')
def leaderboard():
    # Update every five seconds
    avg_lap = []  
    fast_lap = []  
    slow_lap = []  
    badman = [] 
    diesel = []  
    electric = [] 
    
    return render_template('leaderboard.html', 
                           averages=avg_lap, 
                           top_laps=fast_lap, 
                           slow_lap=slow_lap, 
                           badman_lap=badman,
                           diesel=diesel,
                           electric=electric,
    )

# Start a new session
@app.route('/start_session', methods=['POST', 'GET'])
def start_session():
    global changed_lines
    global session_data_analysis
    if request.method == 'POST':
        # Retrieve data from the form submitted in the frontend (JavaScript)
        start_date = request.form['startDate']
        start_time = request.form['startTime']
        duration = request.form['duration']
        participants = request.form['participants']

        # Store the data in the session
        session['competition'] = {
            'start_date': start_date,
            'start_time': start_time,
            'duration': duration,
            'participants': participants
        }
        
        # Print the data in the server console if needed
        print("Competition started with the following details:")
        print(f"Start Date: {start_date}")
        print(f"Start Time: {start_time}")
        print(f"Duration: {duration} hours")
        print(f"Participants: {participants}")

        session['session_active'] = True
        # Redirect to another page, such as the leaderboard or home page
        # Start fetchhing from the supabase
        # Insert 5s of sleep time before making the first data object   
        #time.sleep(5)
        # Aanmaken van data object
        changed_lines = pd.DataFrame()
        #session_data_analysis = DataAnalysis()
        #session_data_analysis.update(changed_lines)

        # Insert 5s of sleep time before making the first data object
        #    
        # time.sleep(5)

        # Aanmaken van data object
        changed_lines = pd.DataFrame()
        # session_data_analysis = DataAnalysis(changed_lines)
        # session_data_analysis.update(changed_lines)
        return redirect(url_for('home'))
    session_active = session.get('session_active', False)
    return render_template('start_session.html',is_session_active = session_active)

# Stop a session
@app.route('/stop_session', methods=['GET', 'POST'])
def stop_session():
    if request.method == 'POST':
        session['stop_message'] = "Session has been stopped successfully." if request.form.get('decision') == 'true' else ""
        session_active = False
        session_stopped = True
        session['stop_message'] = "Session has been stopped successfully."  # Store in session
        # Set the bits
        session['session_active'] = False
        session['session_stopped'] = True
        return redirect(url_for('home'))
    session_active = session.get('session_active', False)
    return render_template('stop_session.html', is_session_active = session_active)

@app.route('/generate_report')
def generate_report():
    session_active = session.get('session_active', False)
    session_stopped = session.get('session_stopped', False)
    return render_template('generate_report.html', is_session_active = session_active, is_session_stopped = session_stopped) 

@app.route('/names')
def names():
    session_active = session.get('session_active', False)
    return render_template('names.html',is_session_active = session_active)

@app.route('/download_report')
def download_report():
    return render_template('download_report.html')

@app.route('/check_pdf_status')
def check_pdf_status():
    """Check if the PDF file is generated"""
    time.sleep(5)
    # Return the pdf if it is generated
    if os.path.exists(PDF_PATH):
        return jsonify({"status": "ready", "pdf_url": "/static/tmp/rider_report_UGent.pdf"})
    else:
        return jsonify({"status": "pending"})

@app.route('/download_pdf')
def download_pdf():
    """Allow users to download the PDF"""
    return send_from_directory(PDF_DIR, "rider_report_UGent.pdf", as_attachment=True)

@app.route('/api/sessions/active')
def get_session_status():
    global is_session_active
    session_active = session.get('session_active', False)
    print(f"session_active: {session_active}")
    return jsonify({'isActive': session_active})

@app.route('/api/sessions/stopped')
def get_session_stopped():
    session_stopped = session.get('session_stopped', False)
    print(f'session stopped: {session_stopped}')
    return jsonify({'isStopped': session_stopped})

@app.route('/api/sessions/renew_data')
def fetch_supabase():
    global data_obj
    # Get the data from the supabase
    
    # Update the data_obj with new lines from supabase

    # Read specific attributes via GETTER method

    # send to frontend 
    pass

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/favicon'), 'favicon.ico', mimetype='image/vnd.microsoft.icon') 

if __name__ == '__main__':
    app.run(debug=True)