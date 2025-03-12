# Import necessary libraries
import pandas as pd
from flask import Flask
from data_analysis import remove_initial_lap, preprocess_lap_times

app = Flask(__name__)

MIN_LAP_TIME = 13
MAX_LAP_TIME = 50

def load_file(file):
    try:
        df = pd.read_csv(file, delimiter=',', on_bad_lines='skip')
    except:
        df = pd.read_csv(file, delimiter=';', on_bad_lines='skip')
    return df

def remove_outliers(df: pd.DataFrame):
    Q1 = df['lapTime'].quantile(0.25)
    Q3 = df['lapTime'].quantile(0.75)
    IQR = Q3 - Q1
    df = df[(df['lapTime'] >= (Q1 - 1.5 * IQR)) & (df['lapTime'] <= (Q3 + 1.5 * IQR))]
    return df

class DataAnalysis:
    def __init__(self, new_file, debug=True):
        self.file = pd.read_csv(new_file,nrows = 1000)     # Working fine
        self.newlines = self.file.copy()    
        
        # if debug:
        #     print(self.file.head())
        self.debug = debug
        self.cleanup()

        # Dataframes that are used to store the important parameters for the screen
        self.average_lap = pd.DataFrame()
        self.fastest_lap = pd.DataFrame()
        self.slowest_lap = pd.DataFrame()
        self.badman = pd.DataFrame()
        self.diesel = pd.DataFrame()
        self.electric = pd.DataFrame()

        # Call the functions that calculate the important parameters for the screen
        self.average_lap_time()
        self.fastest_lap_time()
        self.find_badman()
        self.diesel_engine()
        self.electric_motor()

    def cleanup(self):
        # Convert timestamps to datetime
        self.file['utcTimestamp'] = pd.to_numeric(self.file['utcTimestamp'], errors='coerce')
        self.file.drop_duplicates(inplace = True)
        self.file.dropna(subset=['transponder_id', 'loop', 'utcTimestamp'], inplace=True)
        self.file = preprocess_lap_times(self.file)
        self.file = self.file.sort_values(by=['transponder_id','utcTime'])

        # self.newlines['utcTimestamp'] = pd.to_numeric(self.newlines['utcTimestamp'], errors='coerce')
        # self.newlines.drop_duplicates(inplace = True)
        # self.newlines.dropna(subset=['transponder_id', 'loop', 'utcTimestamp'], inplace=True)
        # self.newlines = preprocess_lap_times(self.newlines)
        # self.newlines = self.newlines.sort_values(by=['transponder_id','utcTime'])
        if self.debug:
            print('cleanup done')

    def update(self, changed_file):
        # Contains the new datarows
        # changed_file_pd = load_file(changed_file)
        changed_file_pd = changed_file

        # Concatenate the new datarows with the existing data, and drop duplicates based on transponder_id and utcTimestamp
        self.file = pd.concat([self.file, changed_file_pd]).drop_duplicates(subset=['transponder_id', 'utcTimestamp'], keep='last')
        self.newlines = pd.merge(changed_file_pd, self.file, how='outer', indicator=True, on=['transponder_id', 'utcTimestamp']).loc[lambda x : x['_merge']=='left_only']
        self.cleanup()  
        # TODO: does the whole file needs to be cleaned up/sorted after an update, or is cleanup from the newlines enough?
        # call all functions that need to be updated
        self.average_lap_time()
        self.fastest_lap_time()
        self.find_badman()
        self.diesel_engine()
        self.electric_motor()
        if self.debug:
            print('update done')
    
    def average_lap_time(self):
        """
        Function that calculates the average laptime of all the transponders

    Parameters:
        file (str): The file path of the CSV recording context data

    Returns:
        DataFrame: A DataFrame containing the transponder IDs and their respective average lap times

        """
        # Sort the data by TransponderID for better visualization and analysis
        df_sorted = self.file.loc[self.file['loop'] == 'L01']
        
        # Calculate the average lap time for each transponder ID
        average_lap_time = df_sorted.groupby('transponder_id')['lapTime'].mean().reset_index()
        self.average_lap = average_lap_time.sort_values(by = 'lapTime')
        self.average_lap.columns = ['transponder_id', 'average_lap_time']
        if self.debug:
            # print(average_lap_time.head())
            print("average_lap_time done.")
            print(self.average_lap.head())
    
    def fastest_lap_time(self):
        """
        Function that calculates the fastest lap time for each transponder

        Parameters:
            file (str): The file path of the CSV recording context data
        
        Returns:
            DataFrame: A DataFrame containing the transponder IDs and their respective fastest lap times
        """

        # Sort the data by TransponderID for better visualization and analysis
        df_sorted = self.file.loc[self.file['loop'] == 'L01']

        # Optionally, remove outliers based on IQR or other method
        df_sorted = remove_outliers(df_sorted)
        
        # Calculate the fastest lap time for each transponder ID
        self.fastest_lap = df_sorted.groupby('transponder_id')['lapTime'].min().reset_index()
        self.fastest_lap.columns = ['transponder_id', 'fastest_lap_time']
        if self.debug:
            print("fastest_lap_time done.")
            print(self.fastest_lap.head())

    def find_badman(self):
        """
        Function that calculates the worst lap time for each transponder

        Returns:
            slowest_lap_time (DataFrame): A DataFrame containing the transponder IDs and their respective worst lap times
            badman (DataFrame): A DataFrame containing the transponder ID and the respective absolute worst lap time of the file
        """
        # Properly filter the DataFrame
        df_sorted = self.file.loc[self.file['loop'] == 'L01']

        # Optionally, remove outliers based on IQR
        df_sorted = remove_outliers(df_sorted)

        # Calculate the slowest lap time for each transponder ID
        self.slowest_lap_time = df_sorted.groupby('transponder_id')['lapTime'].max().reset_index()
        self.slowest_lap_time.columns = ['transponder_id', 'slowest_lap_time']

        # Construct the BADMAN dataframe
        self.badman = df_sorted.loc[df_sorted['lapTime'].idxmax(), ['transponder_id', 'lapTime']].to_frame().T
        self.badman.columns = ['transponder_id', 'worst_lap_time']

        if self.debug:
            print("find_badman done.")

    
    def diesel_engine(self,minimum_incalculated = 10,window = 20):
        # Filter only laps recorded at loop 'L01' to focus on complete laps
        df_filtered = self.file.loc[self.file['loop'] == 'L01']
        
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
        self.diesel = most_consistent_riders.nsmallest(1, 'CV')

        if self.debug:
            print("diesel_engine done.")
    
    def electric_motor(self, window=5, lap_distance=250):
        # Filter only laps recorded at loop 'L01' for complete lap measurements
        df_filtered = self.file.loc[self.file['loop'] == 'L01']
        
        # Drop any rows where 'lapTime' is missing
        df_filtered.dropna(subset=['lapTime'], inplace=True)
        
        # Convert 'lapTime' to numeric values for calculation
        df_filtered['lapTime'] = pd.to_numeric(df_filtered['lapTime'])
        
        # Calculate lap speed (assuming lap distance is provided or normalized)
        df_filtered['lapSpeed'] = lap_distance / df_filtered['lapTime']
        
        # Select relevant columns and drop NaN values
        df_filtered = df_filtered[['transponder_id', 'utcTimestamp', 'lapSpeed']].dropna()
        
        # Convert relevant columns to numeric values
        df_filtered['utcTimestamp'] = pd.to_numeric(df_filtered['utcTimestamp'])
        df_filtered['lapSpeed'] = pd.to_numeric(df_filtered['lapSpeed'])
        
        # Sort by transponder and timestamp to ensure correct time sequence
        df_filtered.sort_values(by=['transponder_id', 'utcTimestamp'], inplace=True)
        
        # Calculate speed differences over time
        df_filtered['speed_diff'] = df_filtered.groupby('transponder_id')['lapSpeed'].diff()
        df_filtered['time_diff'] = df_filtered.groupby('transponder_id')['utcTimestamp'].diff()
        
        # Calculate acceleration (change in speed over change in time)
        df_filtered['acceleration'] = df_filtered['speed_diff'] / df_filtered['time_diff']
        
        # Compute rolling maximum acceleration for each transponder
        df_filtered['rolling_acceleration'] = df_filtered.groupby('transponder_id')['acceleration'].transform(lambda x: x.rolling(window=window, min_periods=1).max())
        
        # Find the transponder with the highest peak acceleration
        peak_acceleration = df_filtered.groupby('transponder_id')['rolling_acceleration'].max().reset_index()
        peak_acceleration.columns = ['transponder_id', 'peak_acceleration']
        
        # Identify the transponder with the absolute highest acceleration
        self.electric = peak_acceleration.nlargest(1, 'peak_acceleration')

        if self.debug:
            print("electric_motor done.")


# TODO: 
# 1.  df_filtered can be done centrally and does not need to be repeated