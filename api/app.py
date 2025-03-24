from flask import Flask, render_template, request, url_for, redirect, session, jsonify,send_file
from api.extra_functions import limit_numeric_to_2_decimals
from api.data_analysis_classes import DataAnalysis
from api.data_analysis import remove_initial_lap, preprocess_lap_times
from api.Read_supabase_data import *
import pandas as pd
import os
from fpdf import FPDF

app = Flask(__name__, template_folder='templates')
data_objects = {}
PER_PAGE = 10
app.secret_key = os.urandom(24)

# Macro for report generation
REPORTS_DIR = "reports"  # Folder to store PDFs
os.makedirs(REPORTS_DIR, exist_ok=True)

@app.route('/') 
def index():
    return render_template('index.html')

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

@app.route('/start_session', methods=['POST', 'GET'])
def start_session():
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
        
        # Print the data in the server console
        print("Competition started with the following details:")
        print(f"Start Date: {start_date}")
        print(f"Start Time: {start_time}")
        print(f"Duration: {duration} hours")
        print(f"Participants: {participants}")

        # Redirect to another page, such as the leaderboard or home page
        return redirect(url_for('home'))

    return render_template('start_session.html')

@app.route('/stop_session', methods=['GET', 'POST'])
def stop_session():
    if request.method == 'POST':
        decision_bool = request.form.get('decision') == 'true'
        session['generate_pdf'] = decision_bool # Opslaan in sessie

        print(f"Session stopped. Generate PDF: {session['generate_pdf']}")  # Debugging

        # Optioneel: Redirect naar een andere pagina (bijv. home)
        return redirect(url_for('home'))

    return render_template('stop_session.html')

@app.route('/generate_report', methods=['GET'])
def show_generate_report():
    return render_template('generate_report.html')

# 📄 API to generate the PDF report
@app.route('/generate_report', methods=['POST'])
def generate_pdf_report():
    filename = f"track_report.pdf"
    pdf_path = os.path.join(REPORTS_DIR, filename)

    # Generate PDF using FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Track Cycling Report", ln=True, align='C')
    pdf.ln(10)
    pdf.output(pdf_path)

    # Store the latest generated report path in a session variable
    return jsonify({"pdf_path": filename})

# 📥 API to download the latest generated PDF
@app.route('/download_report')
def download_report():
    latest_file = sorted(os.listdir(REPORTS_DIR))[-1]
    pdf_path = os.path.join(REPORTS_DIR, latest_file)
    return send_file(pdf_path, as_attachment=True)

@app.route('/names')
def names():
    return render_template('names.html')

@app.route('/home')
def home():
    competition_data = session.get('competition', None)
    return render_template('index.html', competition=competition_data)


if __name__ == '__main__':
    app.run(debug=True)