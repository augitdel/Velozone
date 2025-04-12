from flask import Flask, render_template, request, url_for, redirect, session, send_from_directory, jsonify
from flask_cors import CORS
from flask_session import Session
from data_analysis_branch import DataAnalysis
from report_generator import generate_reports, make_specific_report
from Supabase_table_monitoring import start_monitor_thread, get_and_clear_dataframe
from threading import Thread
import pandas as pd
import os
import redis
import time

# App configuration
app = Flask(__name__, template_folder='templates')
app.secret_key = os.urandom(24)
CORS(app)

#PDF directory configuration
PDF_DIR = os.path.join(app.root_path, "tmp")

# Configure session management
# app.config["SESSION_TYPE"] = "redis"
# app.config["SESSION_PERMANENT"] = True  # Make sessions persistent across browser sessions
# app.config["SESSION_USE_SIGNER"] = True
# app.config["SESSION_KEY_PREFIX"] = "velozone_session:"
# app.config["SESSION_REDIS"] = redis.from_url(os.environ.get("REDIS_URL")) # Configure your Redis URL
# Session(app)

# Initialize the Data Object -> this will contain all of the important data and do the analysis
session_data = DataAnalysis(debug=False)

# Initialize the names dictionary 
names_dict = {}
participants = 0
# PDF-generation
report_dir = None
group_name = 'UGent'  # Default group name
pdf_name = 'rider_report_UGent.pdf'  # Default PDF name

# Home screen
@app.route('/') 
@app.route('/home', methods=['GET', 'POST'])
def home():
    global names_dict
    #Initialize the flags of the active session in the session
    if 'session_active' not in session:
        session['session_active'] = False
    if 'session_closed' not in session:
        session['session_closed'] = False
    if request.method == 'POST':
        data = request.json
        if data:
            names_dict = {item['transponder_id']: item['name'] for item in data}
            print(f'names_dict: {names_dict}')
            # Update the session_data with the new names
            session_data._update_names_dict(names_dict)
            return jsonify({"message": "Transponder data opgeslagen!", "data": names_dict}), 200 
        else:
            return jsonify({"error": "Geen data ontvangen"}), 400
    return render_template('index.html')


@app.route('/leaderboard')
def leaderboard():
    # Initialize the leaderboard
    info_per_transponder = session_data.info_per_transponder
    try:
        # avg_lap : [(name,avg_lap_time)]
        avg_lap_df = info_per_transponder[['average_lap_time']]
        avg_lap_df.reset_index(inplace=True)
        avg_lap = avg_lap_df[['transponder_id', 'average_lap_time']].values.tolist()
        # fast_lap: [(name, fast_lap)]
        fast_lap = info_per_transponder.nsmallest(5, 'fastest_lap_time')[['transponder_name', 'fastest_lap_time']].values.tolist()
        # Slowest_lap: (name, slow_lap)
        slow_lap = info_per_transponder.nlargest(1,'slowest_lap_time')[['transponder_name', 'slowest_lap_time']].values.tolist()
        # Badman --> check how the data enters
        badman = session_data.slowest_rider.values.tolist()
        # Diesel --> check how the data enters
        diesel = session_data.diesel.values.tolist()
        # Electric --> check how the data enters
        electric = session_data.electric.values.tolist()
    except:
        avg_lap = None
        fast_lap = None
        slow_lap = None
        badman = None
        diesel = None
        electric = None
    return render_template('leaderboard.html', averages=avg_lap, top_laps=fast_lap, slow_lap=slow_lap, badman_lap=badman, diesel=diesel,
                           electric=electric)

# Start a new session
@app.route('/start_session', methods=['POST', 'GET'])
def start_session():
    global session_data
    global participants
    global group_name
    if request.method == 'POST':
        # Retrieve data from the form submitted in the frontend (JavaScript)
        start_date = request.form['startDate']
        start_time = request.form['startTime']
        duration = request.form['duration']
        participants = request.form['participants']
        group_name = request.form['groupName']
        print(group_name)
        session['session_active'] = True
        session['session_stopped'] = False
        #Store the data in the session
        session['competition'] = {
              'start_date': start_date,
              'start_time': start_time,
              'duration': duration,
             'participants': participants,
             'group_name': group_name
        }
        # Print the data in the server console if needed
        print("Competition started with the following details:")
        print(f"Start Date: {start_date}")
        print(f"Start Time: {start_time}")
        print(f"Duration: {duration} hours")
        print(f"Participants: {participants}")

        return redirect(url_for('home'))
    # Reset all the variables in the session_data object
    session_data.reset()
    session_active = session.get('session_active', False)
    return render_template('start_session.html',is_session_active = session_active)

# Stop a session
@app.route('/stop_session', methods=['GET', 'POST'])
def stop_session():
    if request.method == 'POST':
        session['stop_message'] = "Session has been stopped successfully." if request.form.get('decision') == 'true' else ""
        session['stop_message'] = "Session has been stopped successfully."  # Store in session
        # Set the bits
        session['session_active'] = False
        session['session_stopped'] = True
        # Save self._file from session_data to a csv-file
        session_data.save_to_csv()
        return redirect(url_for('home'))
    session_active = session.get('session_active', False)
    return render_template('stop_session.html', is_session_active = session_active)

# TODO: implement it such that we can reset the variables
@app.route('/refresh')
def refresh_session():
    pass

############## REPORT GENERATION ##############
@app.route('/generate_report', methods=['POST', 'GET'])
def generate_report():
    # Get the status bits
    global report_dir
    global pdf_name
    if request.method == 'POST':
        print("POST request received, start creating the report")
        # Get the selected rider from the form
        data = request.get_json()
        rider_id = data.get('rider_name')
        if rider_id:
            try:
                # Alter the report directory to the correct one
                print(group_name)
                if rider_id == 'GROUP':
                    report_dir = os.path.join(app.root_path, f'tmp/rider_report_{group_name}.pdf')
                    pdf_name = f'rider_report_{group_name}.pdf'
                else:
                    report_dir = os.path.join(app.root_path, f'tmp/rider_report_{rider_id}.pdf')
                    pdf_name = f'rider_report_{rider_id}.pdf'
                # Make the report
                make_specific_report('api/static/csv/lap_times.csv', rider_id)
                return jsonify({'status': 'success', 'message': f'Report generated for {rider_id}'}), 200
            except Exception as e:
                print(f"Error generating report: {e}")
                return jsonify({'status': 'error', 'message': 'Failed to generate report'}), 500
        else:
            return jsonify({'status': 'error', 'message': 'No rider selected'}), 400
    session_active = session.get('session_active', False)
    session_stopped = session.get('session_stopped', False)
    # Get the riders from the session_data object
    riders = ['GROUP'] + session_data.info_per_transponder.index.tolist()
    return render_template('generate_report.html', is_session_active = session_active, is_session_stopped = session_stopped, riders = riders, names_dict = names_dict) 

@app.route('/download_report')
def download_report():
    return render_template('download_report.html')

@app.route('/check_pdf_status')
def check_pdf_status():
    """Check if the PDF file is generated"""
    # Return the pdf if it is generated
    print(report_dir)
    if os.path.exists(report_dir):
        print("report generation done!")
        return jsonify({"status": "ready", "pdf_url": f"{report_dir}"})
    else:
        print("can not find report folder")
        return jsonify({"status": "pending"})

@app.route('/download_pdf')
def download_pdf():
    """Allow users to download the PDF"""
    print("searching for pdf")
    return send_from_directory(PDF_DIR, pdf_name, as_attachment=True)

##############################################

@app.route('/names')
def names():
    session_active = session.get('session_active', False)
    return render_template('names.html',is_session_active = session_active)

@app.route('/api/sessions/active')
def get_session_status():
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
    changed_file = get_and_clear_dataframe()

    # Update with the new data
    if not changed_file.empty:
        session_data.update(changed_file)
        print("New Data found!")

    info_per_transponder = session_data.info_per_transponder
    print(info_per_transponder)
    if not info_per_transponder.empty:
        # avg_lap : [(name,avg_lap_time)]
        avg_lap = info_per_transponder[['average_lap_time', 'total_L01_laps']].sort_values(by='average_lap_time').reset_index().values.tolist()
        # fast_lap: [(name, fast_lap)]
        fast_lap = info_per_transponder.nsmallest(5, 'fastest_lap_time')[['fastest_lap_time']].reset_index().values.tolist()
        #  Slowest_lap: (name, slow_lap)
        slow_lap = info_per_transponder.nlargest(1,'slowest_lap_time')[['slowest_lap_time']].reset_index().values.tolist()
        #  Badman --> check how the data enters
        badman = session_data.badman.reset_index().values.tolist()
        #  Diesel --> check how the data enters
        diesel = session_data.diesel.values.tolist()
        #  Electric --> check how the data enters
        electric = session_data.electric.values.tolist()
        if len(electric) > 0 and pd.isna(electric[0][1]):
            electric = None
    else:
        avg_lap = None
        fast_lap = None
        slow_lap = None
        badman = None
        diesel = None
        electric = None
    print(f"avg_lap: {avg_lap}")
    print(f"fast_lap: {fast_lap}")
    print(f"slow_lap: {slow_lap}")
    print(f"badman: {badman}")
    print(f"diesel: {diesel}")
    print(f"electric: {electric}")

    response_data = {
            'averages': avg_lap if avg_lap is not None else [],
            'top_laps': fast_lap if fast_lap is not None else [],
            'slow_lap': slow_lap if slow_lap is not None else [],
            'badman_lap': badman if badman is not None else [],
            'diesel': diesel if diesel is not None else [],
            'electrical': electric if electric is not None else [],
            'transponder_names' : names_dict if names_dict else {},
            'participants': participants if participants else 0,
        }
    return jsonify(response_data)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/favicon'), 'favicon.ico', mimetype='image/vnd.microsoft.icon') 

if __name__ == '__main__':
    monitor_thread = start_monitor_thread()
    # run_get_and_clear_every(interval=3) 
    app.run(debug=True)
