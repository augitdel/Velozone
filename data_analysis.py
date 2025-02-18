# Import necessary libraries
import pandas as pd

def load_file(file):
    try:
        df = pd.read_csv(file, delimiter=',', on_bad_lines='skip')
    except:
        df = pd.read_csv(file, delimiter=';', on_bad_lines='skip')
    
    return df


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
    df = load_file(file)

    # Sort the data by TransponderID for better visualization and analysis
    df_sorted = df.sort_values(by=['transponder_id','utcTime']).where(df['loop'] =='L01')
    df_sorted = df_sorted.dropna(subset='loop')
    print(df_sorted['lapTime'].head())
    average_lap_time = df_sorted.groupby('transponder_id')['lapTime'].mean().reset_index()
    average_lap_time.columns = ['transponder_id', 'average_lap_time']
    return average_lap_time


def fastest_lap(file):
    """
    Function that calculates the fastest lap time for each transponder

    Parameters:
    -----------
    file (str): The file path of the CSV recording context data
    
    Returns:
    --------
    DataFrame: A DataFrame containing the transponder IDs and their respective fastest lap times
    """
    # Load the data
    df = load_file(file)

    # Sort the data by TransponderID for better visualization and analysis
    df_sorted = df.sort_values(by=['transponder_id','utcTime']).where(df['loop'] =='L01')
    df_sorted = df_sorted.dropna(subset='loop')


    # Optionally, remove outliers based on IQR or other method
    Q1 = df_sorted['lapTime'].quantile(0.25)
    Q3 = df_sorted['lapTime'].quantile(0.75)
    IQR = Q3 - Q1
    df_sorted = df_sorted[(df_sorted['lapTime'] >= (Q1 - 1.5 * IQR)) & (df_sorted['lapTime'] <= (Q3 + 1.5 * IQR))]
    
    fastest_lap_time = df_sorted.groupby('transponder_id')['lapTime'].min().reset_index()
    fastest_lap_time.columns = ['transponder_id', 'fastest_lap_time']
    
    return fastest_lap_time


if __name__ == '__main__':
    file = 'RecordingContext_20250214.csv'
    average_lap_times = average_lap_time(file)
    fastest_lap_times = fastest_lap(file)
    
    #aggregate the data
    all_data = pd.merge(average_lap_times, fastest_lap_times, on='transponder_id')
    
    # display the results
    print("Average lap time per transponder:")
    print(all_data.sort_values(by = 'average_lap_time'))
    
    print("\nFastest lap time per transponder:")
    print(all_data.sort_values(by = 'fastest_lap_time'))
    
    # display the results sorted by average lap time and fastest lap time separately
    print("\nAverage lap time per transponder (sorted):")
    print(average_lap_times.sort_values(by = 'average_lap_time'))
    
    print("\nFastest lap time per transponder (sorted):")
    print(fastest_lap_times.sort_values(by = 'fastest_lap_time'))
