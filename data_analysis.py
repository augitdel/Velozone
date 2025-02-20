# Import necessary libraries
import pandas as pd
from flask import Flask, render_template

app = Flask(__name__)

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
        file (str): The file path of the CSV recording context data

    Returns:
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
        file (str): The file path of the CSV recording context data
    
    Returns:
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

def badman(file):
    """
    Function that calculates the worst lap time for each transponder

    Parameters:
        file (str): The file path of the CSV recording context data
    
    Returns:
        slowest_lap_time (DataFrame): A DataFrame containing the transponder IDs and their respective worst lap times
        badman (DataFrame): A DataFrame containing the transponder ID and the respective absolute worst lap time of the file
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
    
    slowest_lap_time = df_sorted.groupby('transponder_id')['lapTime'].max().reset_index()
    slowest_lap_time.columns = ['transponder_id', 'slowest_lap_time']

    badman = df_sorted.loc[df_sorted['lapTime'].idxmax(), ['transponder_id', 'lapTime']].to_frame().T
    badman.columns = ['transponder_id', 'worst_lap_time']
    
    return slowest_lap_time, badman

def diesel_engine(file, minimum_incalculated=10, window=20):
    """
    Identify the transponder with the most consistent lap times ("Diesel Engine") among those with the lowest rolling variability.
    
    Parameters:
        file (str): The file path of the CSV recording lap time data.
    
    Returns:
        DataFrame: A DataFrame containing the transponder ID and consistency metrics.
    """
    # Load data from the CSV file
    df = load_file(file)
    
    # Filter only laps recorded at loop 'L01' to focus on complete laps
    df_filtered = df[df['loop'] == 'L01'].copy()
    
    # Drop any rows where 'lapTime' is missing
    df_filtered.dropna(subset=['lapTime'], inplace=True)
    
    # Convert 'lapTime' to numeric values for calculation
    df_filtered['lapTime'] = pd.to_numeric(df_filtered['lapTime'])
    
    # Exclude transponders with fewer than minimum_incalculated laps
    df_filtered = df_filtered.groupby('transponder_id').filter(lambda x: len(x) > minimum_incalculated)
    
    # Calculate the standard deviation (σ) and mean (μ) of lap times for each transponder
    stats = df_filtered.groupby('transponder_id')['lapTime'].agg(['std', 'mean']).reset_index()
    
    # Compute Coefficient of Variation (CV = std / mean), handling potential division by zero
    stats['CV'] = stats['std'] / stats['mean']
    
    # Calculate rolling standard deviation to measure pacing consistency over time
    df_filtered['rolling_std'] = df_filtered.groupby('transponder_id')['lapTime'].transform(lambda x: x.rolling(window=window, min_periods=1).std())
    
    # Compute the average rolling standard deviation for each transponder
    rolling_consistency = df_filtered.groupby('transponder_id')['rolling_std'].mean().reset_index()
    rolling_consistency.columns = ['transponder_id', 'rolling_variability']
    
    # Merge consistency metrics
    result = stats.merge(rolling_consistency, on='transponder_id')
    
    # First, select the riders with the lowest rolling variability (most stable pacing)
    most_consistent_riders = result.nsmallest(5, 'rolling_variability')  # Selects top 5 with lowest rolling variability
    
    # Then, from this subset, select the rider with the lowest coefficient of variation (CV)
    diesel_engine = most_consistent_riders.nsmallest(1, 'CV')
    
    return diesel_engine

print(f'diesel_engine=\n {diesel_engine("RecordingContext_20250214.csv")}')