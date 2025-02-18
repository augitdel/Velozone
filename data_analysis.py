# Import necessary libraries
import pandas as pd



def average_lap_time(file):
    """
    Function that calculates the average laptime of all the transponders

    Parameters:
    -----------
    file (str): The file path of the CSV recording context data

    Returns:
    --------
    DataFrame: A DataFrame containing the transponder IDs and their respective average lap times
    
    """
    # Load the data
    file_path = 'RecordingContext_20250214.csv'  # Change this to the location of your file
    # Try using different delimiters and handle bad lines gracefully
    try:
        df = pd.read_csv(file_path, delimiter=',', on_bad_lines='skip')
    except:
        df = pd.read_csv(file_path, delimiter=';', on_bad_lines='skip')


    # Sort the data by TransponderID for better visualization and analysis
    df_sorted = df.sort_values(by=['transponder_id','utcTime']).where(df['loop'] =='L01')
    df_sorted = df_sorted.dropna(subset='loop')

    average_lap_time = df_sorted.groupby('transponder_id')['lapTime'].mean().reset_index()
    average_lap_time.columns = ['transponder_id', 'average_lap_time']

    print(average_lap_time.head())
    return average_lap_time