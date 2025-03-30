# Import necessary libraries
import pandas as pd
import numpy as np
from flask import Flask, render_template
from faker import Faker
import os

app = Flask(__name__)

TRANS_NAME_FILE = "transponder_names.xlsx"

def generate_random_name():
    """Generate a random name."""
    fake = Faker()
    return fake.first_name()

def load_transponder_names(transponder_ids):
    """Ensure each transponder has a name and save it to an Excel file."""
    if os.path.exists(TRANS_NAME_FILE):
        name_df = pd.read_excel(TRANS_NAME_FILE, dtype={'transponder_id': str})
    else:
        name_df = pd.DataFrame(columns=['transponder_id', 'name'])
    
    # Convert to set for fast lookup
    existing_ids = set(name_df['transponder_id'].astype(str))
    print(existing_ids)
    # Ensure all transponder_ids have a name
    new_entries = [{'transponder_id': str(tid), 'name': generate_random_name()} 
                   for tid in transponder_ids if str(tid) not in existing_ids]

    if new_entries:
        new_df = pd.DataFrame(new_entries)
        name_df = pd.concat([name_df, new_df], ignore_index=True).drop_duplicates(subset=['transponder_id'])
        # Save the updated file
        name_df.to_excel(TRANS_NAME_FILE, index=False)
    return name_df



class DataAnalysis:
    # IMPORTANT: As per convention the class properties and methods prefixed with an underscore are considered private and should not be accessed directly from outside the class.
    # However, some of the properties can be read and set with getters and setters.
    def __init__(self, new_DF, MIN_LAP_TIME=13, MAX_LAP_TIME=50, debug=False):        
        columns_incomming_csv = ['transponder_id','loop','utcTimestamp','utcTime','lapTime','lapSpeed','maxSpeed','cameraPreset','cameraPan','cameraTilt','cameraZoom','eventName','recSegmentId','trackedRider']
        self._file = pd.DataFrame(columns=columns_incomming_csv)
        self._newlines = pd.DataFrame(columns=columns_incomming_csv)

        self.MIN_LAP_TIME = MIN_LAP_TIME
        self.MAX_LAP_TIME = MAX_LAP_TIME

        # self.fileL01 = self.file.loc[self.file['loop'] == 'L01']
        # self.newlinesL01 = self.newlines.loc[self.newlines['loop'] == 'L01']

        self._info_per_transponder = pd.DataFrame(columns=['transponder_id', 'transponder_name', 'L01_laptime_list', 'fastest_lap_time', 'average_lap_time', 'slowest_lap_time', 'total_L01_laps'])
        self._info_per_transponder.set_index('transponder_id', inplace=True)

        self._slowest_rider = pd.DataFrame()
        self._diesel = pd.DataFrame()
        self._electric = pd.DataFrame()
        
        self.debug = debug

        self.update(new_DF)

    def _cleanup(self):
        self._file.drop_duplicates(inplace = True)
        self._newlines.dropna(subset=['transponder_id', 'loop', 'utcTimestamp'], inplace=True).sort_values(by=['transponder_id','utcTime'], inplace=True)

    def preprocess_lap_times(self, df):
        """Operations:
            - Ensure lapTime is numeric
            - Drop rows with NaN in the 'lapTime' column
            - Filter out lap times that are too short or too long"""

        df['lapTime'] = pd.to_numeric(df['lapTime'], errors='coerce')  # Ensure lapTime is numeric
        valid_laps = df[(df['lapTime'] >= self.MIN_LAP_TIME) & (df['lapTime'] <= self.MAX_LAP_TIME)]
        valid_laps.dropna(subset=['lapTime'], inplace=True) # Drop rows with NaN in the 'lapTime' column
        return valid_laps

    def update(self, changed_file):
        """
        Loads the changed lines from the CSV file and appends them to the existing DataFrame.
        Then it updates the following:
        - The transponder names
        - The average lap time for each transponder
        - The fastest lap time for each transponder
        - The badman (the transponder with the highest average lap time)
        - The diesel engine (the transponder with the lowest average lap time)
        - The electric motor (the transponder with the highest average lap time among the electric transponders)

        Parameters:
            changed_file (DF): dataframe containing the changed lines retreived from the supabase
        """
        # load the changed supabase file, check which are the new lines, preprocess them and append them to the file
        # TODO: possible optimalisation: don't check with the whole self.file, but compare with timestamps saved to the self.info_per_transponder df
        self._newlines = self.preprocess_lap_times(pd.merge(changed_file, self._file, how='outer', indicator=True, on=['transponder_id', 'utcTimestamp']).loc[lambda x: x['_merge'] == 'left_only'])
        self._file = pd.concat([self._file, self._newlines])
        
        self._cleanup()  # TODO: does the whole file needs to be cleaned up/sorted after an update, or is cleanup from the newlines enough?
        
        # update the transponder names if necessary
        # TODO: how to do this in a more efficient way? Finish the implementation
        existing_transponders = set(self._info_per_transponder['transponder_id'].astype(str))
        new_transponders = set(self._newlines['transponder_id']).difference(set(existing_transponders))

        if self.debug:
            print('start calling update functions...\n'+'='*40)

        # call all functions that need to be updated
        self._update_L01_laptimes()
        self._update_total_L01_laps()
        self._average_lap_time()
        self._fastest_lap()
        self._badman()
        self._diesel_engine()
        self._electric_motor()

        if self.debug:
            print('update done\n'+'='*40)

    def _update_L01_laptimes(self):
        """
        Function that updates the lap times of the L01 loop for each transponder in self.info_per_transponder DataFrame
        """
        new_laptimes = self._newlines.loc[self._newlines['loop'] == 'L01'].groupby('transponder_id')['lapTime'].apply(list)
        self._info_per_transponder['L01_laptime_list'] = self._info_per_transponder.apply(lambda row: row['L01_laptime_list'] + new_laptimes.get(row.name, []) if row.name in self._newlines['transponder_id'].values else row['L01_laptime_list'], axis=1)
        
        if self.debug:
            print('L01_laptime_list updated\n'+'='*40)

    def _update_total_L01_laps(self):
        """
        Function that updates the total number of (L01) laps each transponder has completed and fills this information in the info_per_transponder DataFrame.
        """
        # TODO: check if this is equal to the length of the L01_laptime_list
        self._info_per_transponder['total_L01_laps'] += self._info_per_transponder['transponder_id'].isin(self._newlines['transponder_id']).astype(int)
        if self.debug:
            print('total_L01_laps updated\n'+'='*40)

    def _average_lap_time(self):
        """
        Function that updates the average laptime of all the updated transponders.
        """
        self._info_per_transponder['average_lap_time'] = self._info_per_transponder.apply(lambda row: np.mean(row['L01_laptime_list']) if row.name in self._newlines['transponder_id'].values and len(row['L01_laptime_list']) > 0 else np.nan, axis=1)
        if self.debug:
            print('average_lap_time updated\n'+'='*40)

    def _fastest_lap(self):
        """
        Function that updates the fastest lap time for each transponder.
        """
        self._info_per_transponder['fastest_lap_time'] = self._info_per_transponder.apply(lambda row: np.min(row['L01_laptime_list']) if row.name in self._newlines['transponder_id'].values and len(row['L01_laptime_list']) > 0 else np.nan, axis=1)
        if self.debug:
            print('fastest_lap_time updated\n'+'='*40)

    def slowest_lap(self):
        """
        Function that updates the slowest lap time for each transponder.
        
        Returns:
            DataFrame: A DataFrame containing the transponder IDs and their respective slowest lap times
        """
        self._info_per_transponder['slowest_lap_time'] = self._info_per_transponder.apply(lambda row: np.max(row['L01_laptime_list']) if row.name in self._newlines['transponder_id'].values and len(row['L01_laptime_list']) > 0 else np.nan, axis=1)
        if self.debug:
            print('slowest_lap_time updated\n'+'='*40)

    def _badman(self):
        """
            Function that calculates the slowest rider of the session and stores it in self.slowest_rider.
        """
        self._slowest_rider = self._info_per_transponder.loc[self._info_per_transponder['slowest_lap_time'].idxmax()]

        if self.debug:
            print('badman updated\n'+'='*40)
    
    def _diesel_engine(self,minimum_incalculated = 10,window = 20):
        """
        Function that identifies the transponder with the most consistent lap times ("Diesel Engine").
        
        Parameters:
            minimum_incalculated (int, optional): The minimum number of laps required to be considered for the diesel engine.
            window (int, optional): The window size for the rolling standard deviation.
        
        Result:
        ---------
            self.diesel: DataFrame containing the transponder ID, standard deviation on his laptimes, average lap time, CV (Coefficient of Variation) and rolling variability for the most consistent rider.
        """
        # Filter only laps recorded at loop 'L01' to focus on complete laps
        df_filtered = self._file.loc[self._file['loop'] == 'L01']
        
        # Drop any rows where 'lapTime' is missing
        df_filtered.dropna(subset=['lapTime'], inplace=True)
        
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
        self._diesel = most_consistent_riders.nsmallest(1, 'CV')

        # TODO: incorporate name of the rider in some way

        if self.debug:
            print('diesel_engine updated\n'+'='*40)
    
    def _electric_motor(self,  window=5, lap_distance=250):
        """
        Function that calculates the highest acceleration of all the transponders
        
        Parameters:
            window (int, optional): The window size over which the acceleration is calculated.
            lap_distance (float, optional): The length of the lap (in meters) for which the
                acceleration is calculated.
        
        Result:
        ---------
            self.electric: DataFrame containing the transponder ID and peak acceleration for the cyclist with the highest acceleration.
        """
        # Filter only laps recorded at loop 'L01' for complete lap measurements
        df_filtered = self._file.loc[self._file['loop'] == 'L01']
        
        # Drop any rows where 'lapTime' is missing
        df_filtered = df_filtered.dropna(subset=['lapTime'])
        
        # Convert 'lapTime' to numeric values for calculation
        df_filtered.loc[:,'lapTime'] = pd.to_numeric(df_filtered['lapTime'])
        
        # Calculate lap speed (assuming lap distance is provided or normalized)
        df_filtered.loc[:,'lapSpeed'] = lap_distance / df_filtered['lapTime']
        
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
        self._electric = peak_acceleration.nlargest(1, 'peak_acceleration')

        if self.debug:
            print('electric_motor updated\n'+'='*40)
    

    # Getters and Setters
        
    @property
    def get_badman(self):
        return self._slowest_rider
    
    @property
    def get_diesel_engine(self):
        return self._diesel
    
    @property
    def get_electric_motor(self):
        return self._electric
    
    @property
    def get_info_per_transponder(self):
        return self._info_per_transponder
    
    @property
    def get_file(self):
        return self._file
    
    @property
    def get_Min_Lap_Time(self):
        return self.MIN_LAP_TIME
    
    @MIN_LAP_TIME.setter
    def MIN_LAP_TIME(self, new_min_lap_time):
        self.MIN_LAP_TIME = new_min_lap_time
        if self.debug:
            print(f'Minimum lap time set to {new_min_lap_time}')

    @property
    def get_Max_Lap_Time(self):
        return self.MAX_LAP_TIME

    @MAX_LAP_TIME.setter
    def MAX_LAP_TIME(self, new_max_lap_time):
        self.MAX_LAP_TIME = new_max_lap_time
        if self.debug:
            print(f'Maximum lap time set to {new_max_lap_time}')
    
    @property
    def get_debug(self):
        return self.debug
    
    @debug.setter
    def debug(self, new_debug):
        self.debug = new_debug
        if self.debug:
            print(f'Debug mode set to {new_debug}')