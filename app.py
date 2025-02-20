from flask import Flask, render_template
import pandas as pd
import data_analysis

app = Flask(__name__,template_folder='frontend')

def get_lap_times(file):
    """
    Function that calculates the fastest lap and average lap time for each transponder
    """
    fastest_lap_times = data_analysis.fastest_lap(file)
    average_lap_times = data_analysis.average_lap_time(file)

    # Merge data for display
    lap_times = pd.merge(fastest_lap_times, average_lap_times, on='transponder_id')
    lap_times.columns = ['transponder_id', 'fastest_lap_time', 'average_lap_time']
    
    return lap_times,fastest_lap_times,average_lap_times

@app.route('/')
def index():
    # Load data
    _,fastest_lap_times,average_lap_times = get_lap_times('RecordingContext_20250214.csv')

    # Convert dataFrame to correct shape
    average_lap_times = average_lap_times.values.tolist()
    # Get top 5 fastest laps
    top_5_laps = fastest_lap_times.head(5).values.tolist()

    return render_template('index.html', averages=average_lap_times, top_laps=top_5_laps)

if __name__ == '__main__':
    app.run(debug=True)
