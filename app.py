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
def index():
    fileName = 'RecordingContext_20250214.csv'
    # Load data
    _,fastest_lap_times,average_lap_times = get_lap_times(fileName)

    # Convert dataFrame to correct shape
    avg_lap = average_lap_times.values.tolist()
    
    # Get top 5 fastest laps
    fast_lap = fastest_lap_times.head(5).values.tolist()
    # BADMAN
    slow_lap = data_analysis.badman(fileName)[0].values.tolist()    # This is a dataFrame
    badman = data_analysis.badman(fileName)[1].values.tolist()            
    diesel = data_analysis.diesel_engine(fileName).values.tolist()

    # Limit all of the numeric values to 2 decimals
    avg_lap = limit_numeric_to_2_decimals(avg_lap)
    fast_lap = limit_numeric_to_2_decimals(fast_lap)
    slow_lap = limit_numeric_to_2_decimals(slow_lap)
    badman = limit_numeric_to_2_decimals(badman)
    diesel = limit_numeric_to_2_decimals(diesel)
    
    return render_template('index.html', 
                           averages=avg_lap, 
                           top_laps=fast_lap, 
                           slow_lap=slow_lap, 
                           badman_lap=badman,
                           diesel=diesel)

if __name__ == '__main__':
    app.run(debug=True)
