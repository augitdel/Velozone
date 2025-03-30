from flask import Flask, render_template, request, url_for, redirect, session, send_from_directory,jsonify
from flask_cors import CORS 
from data_analysis_branch import DataAnalysis
# from extra_functions import limit_numeric_to_2_decimals
# from data_analysis_classes import DataAnalysis
# from data_analysis import remove_initial_lap, preprocess_lap_times
# from Read_supabase_data import *
import pandas as pd
import os
import time

app = Flask(__name__, template_folder='templates')
data_objects = {}
app.secret_key = os.urandom(24)

PER_PAGE = 10
PDF_DIR = os.path.join(app.root_path, "tmp")
PDF_PATH = os.path.join(PDF_DIR, "rider_report_UGent.pdf")

# Store IndexedDB data in-memory (or use a database)
indexeddb_data = []
CORS(app) # Enable CORS for development

# Variable to track if session is active
session_active = False
session_stopped = False

changed_lines
session_data_analysis
names_dict

# Home screen
@app.route('/') 
@app.route('/home', methods=['GET', 'POST'])
def home():
    global names_dict
    competition_data = session.get('competition', None)
    if request.method == 'POST':
        # Receive the data from the transponder_ids and names
        # Create the 
        names_dict = request.form.getlist('names[]')
        pass
    return render_template('index.html', competition=competition_data)


@app.route('/upload', methods=['POST'])
def upload_transponder_data():
    data = request.get_json()
    # print("Received transponder data:")
    # for item in data:
    #     print(f"ID: {item['id']}, Name: {item['name']}")
    #     # Here you can process the data, e.g., store it in a file or database
    return jsonify({"message": "Data received successfully!"}), 200

@app.route('/leaderboard/')
def leaderboard(page = 1):
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

# Start a new session
@app.route('/start_session', methods=['POST', 'GET'])
def start_session():
    global session_active
    global session_stopped
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

        session_active = True
        # Redirect to another page, such as the leaderboard or home page
        # Start fetchhing from the supabase
        # Insert 5s of sleep time before making the first data object   
        time.sleep(5)
        # Aanmaken van data object
        changed_lines = pd.DataFrame()
        session_data_analysis = DataAnalysis()
        session_data_analysis.update(changed_lines)

        return redirect(url_for('home'))
    return render_template('start_session.html',session_active = session_active)

# Stop a session
@app.route('/stop_session', methods=['GET', 'POST'])
def stop_session():
    global session_active
    global session_stopped
    if request.method == 'POST':
        session['generate_pdf'] = request.form.get('decision') == 'true'
        session['stop_message'] = "Session has been stopped successfully."  # Store in session
        session_active = False
        session_stopped = True
        return redirect(url_for('home'))

    return render_template('stop_session.html', is_session_active = session_active)

@app.route('/generate_report')
def generate_report():
    global session_active
    global session_stopped
    return render_template('generate_report.html', session_active = session_active, session_stopped = session_stopped) 

@app.route('/names')
def names():
    return render_template('names.html')

@app.route('/download_report')
def download_report():
    return render_template('download_report.html')

@app.route('/check_pdf_status')
def check_pdf_status():
    """Check if the PDF file is generated"""
    time.sleep(5)
    # Return the pdf if it is generated
    if os.path.exists(PDF_PATH):
        return jsonify({"status": "ready", "pdf_url": "/static/reports/rider_report_UGent.pdf"})
    else:
        return jsonify({"status": "pending"})

@app.route('/download_pdf')
def download_pdf():
    """Allow users to download the PDF"""
    return send_from_directory(PDF_DIR, "rider_report_UGent.pdf", as_attachment=True)

@app.route('/api/sessions/active')
def get_session_status():
    global is_session_active
    # print(f"session_active: {session_active}")
    return jsonify({'isActive': session_active})

@app.route('/api/sessions/stopped')
def get_session_stopped():
    global session_stopped
    return jsonify({'isStopped': session_stopped})

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/favicon'), 'favicon.ico', mimetype='image/vnd.microsoft.icon') 

if __name__ == '__main__':
    app.run(debug=True)