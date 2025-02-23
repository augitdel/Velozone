from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import data_analysis
import json
import time

# Initialize Flask app and SocketIO
app = Flask(__name__, template_folder='frontend')
app.secret_key = "your_secret_key"
socketio = SocketIO(app)
fast_lap_json = json.dumps([])  # Placeholder JSON data

# Configure SQLAlchemy for database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Database Model - Single Row within the db
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(25), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        if password:
            self.password_hash = generate_password_hash(password)
        else:
            raise ValueError("Password cannot be empty.")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Functions for calculating lap times
def get_lap_times(file):
    fastest_lap_times = data_analysis.fastest_lap(file)
    average_lap_times = data_analysis.average_lap_time(file)
    lap_times = pd.merge(fastest_lap_times, average_lap_times, on='transponder_id')
    lap_times.columns = ['transponder_id', 'fastest_lap_time', 'average_lap_time']
    return lap_times, fastest_lap_times, average_lap_times

def limit_numeric_to_2_decimals(data):
    if isinstance(data, list):
        return [limit_numeric_to_2_decimals(item) for item in data]
    elif isinstance(data, dict):
        return {key: limit_numeric_to_2_decimals(value) for key, value in data.items()}
    elif isinstance(data, float):
        return round(data, 2)
    else:
        return data

# Routes
@app.route("/")
def home():
    if "email" in session:
        return redirect(url_for('dashboard'))
    return render_template("login.html")

# Login Route
@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    if email and password:
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['email'] = email
            return redirect(url_for('dashboard'))
    return render_template("login.html", error="Invalid login credentials")

# Register Route
@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    if not username or not email or not password:
        return render_template("login.html", errors="All fields are required.")
    user = User.query.filter_by(email=email).first()
    if user:
        return render_template("login.html", error="User already exists!")
    else:
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session["email"] = email
        return redirect(url_for('dashboard'))

# Dashboard Route
@app.route("/dashboard")
def dashboard():
    if "email" in session:
        user = User.query.filter_by(email=session["email"]).first()
        fileName = 'RecordingContext_20250214.csv'
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

        return render_template("Website_V1.0.html", 
                               username=user.username, 
                               averages=avg_lap, 
                               top_laps=fast_lap, 
                               slow_lap=slow_lap, 
                               badman_lap=badman, 
                               diesel=diesel)
    return redirect(url_for('home'))

# Logout Route
@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('home'))

# SocketIO events
@socketio.on('connect')
def handle_connect():
    print("Client connected")
    socketio.emit('fast_lap_data', fast_lap_json)

def send_fast_lap_times():
    while True:
        socketio.emit('fast_lap_data', fast_lap_json)
        time.sleep(1)  # Simulate real-time updates

# Main entry point
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create all tables
    socketio.run(app, debug=True)
