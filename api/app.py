from flask import Flask, render_template, request, url_for, redirect, session, send_from_directory,jsonify
from flask_cors import CORS
from transponder_names import TransponderDataBase
from data_analysis_branch import DataAnalysis
from flask_cors import CORS 
from flask_session import Session
import pandas as pd
import os
import redis
import time


app = Flask(__name__, template_folder='templates')
app.secret_key = os.urandom(24)

PDF_DIR = os.path.join(app.root_path, "tmp")
PDF_PATH = os.path.join(PDF_DIR, "rider_report_UGent.pdf")

CORS(app)

# Configure session management
# app.config["SESSION_TYPE"] = "redis"
# app.config["SESSION_PERMANENT"] = True  # Make sessions persistent across browser sessions
# app.config["SESSION_USE_SIGNER"] = True
# app.config["SESSION_KEY_PREFIX"] = "velozone_session:"
# app.config["SESSION_REDIS"] = redis.from_url(os.environ.get("REDIS_URL")) # Configure your Redis URL

# Session(app)

PER_PAGE = 10
PDF_DIR = os.path.join(app.root_path, "static/tmp")
PDF_PATH = os.path.join(PDF_DIR, "rider_report_UGent.pdf")

# Structures to keep track of the names
names_dict = {}
names_database = TransponderDataBase()
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
            print(data)
            names_dict = {item['transponder_id']: item['name'] for item in data}
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
    # Update the DataFrames
    info_per_transponder = session_data.info_per_transponder
    # avg_lap : [(name,avg_lap_time)]
    avg_lap = info_per_transponder[['transponder_name', 'average_lap_time']] 
    # fast_lap: [(name, fast_lap)]
    fast_lap = info_per_transponder.nsmallest(5, 'fastest_lap_time')[['transponder_name', 'fastest_lap_time']]
    # Slowest_lap: (name, slow_lap)
    slow_lap = info_per_transponder.nlargest(1,'slowest_lap_time')[['transponder_name', 'slowest_lap_time']]
    badman = session_data.slowest_rider
    diesel = session_data.diesel 
    electric = session_data.electric
    
    return render_template('leaderboard.html', 
                           averages=avg_lap, 
                           top_laps=fast_lap, 
                           slow_lap=slow_lap, 
                           badman_lap=badman,
                           diesel=diesel,
                           electric=electric)

# Start a new session
@app.route('/start_session', methods=['POST', 'GET'])
def start_session():
    global session_data
    if request.method == 'POST':
        # Set the flag to True
        session['session_active'] = True

        # Initialize the Data Object -> this will contain all of the important data and do the analysis
        # __INIT__ gets called and dataframes are created
        session_data = DataAnalysis()

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
    # time.sleep(5)
    print(os.path.exists(PDF_PATH))
    # Return the pdf if it is generated
    if os.path.exists(PDF_PATH):
        print("report generation done!")
        return jsonify({"status": "ready", "pdf_url": "/static/tmp/rider_report_UGent.pdf"})
    else:
        print("can not find report folder")
        return jsonify({"status": "pending"})

@app.route('/download_pdf')
def download_pdf():
    """Allow users to download the PDF"""
    print("searching for pdf")
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