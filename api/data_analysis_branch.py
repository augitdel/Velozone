# Import necessary libraries
import pandas as pd
import numpy as np
import os

class DataAnalysis:
    # IMPORTANT: As per convention the class properties and methods prefixed with an underscore are considered private and should not be accessed directly from outside the class.
    # However, some of the properties can be read and set with getters and setters.
    def __init__(self, MIN_LAP_TIME=13, MAX_LAP_TIME=50, debug=False):        
        columns_incomming_DF = ['transponder_id','loop','utcTimestamp','utcTime','lapTime','lapSpeed','maxSpeed','cameraPreset','cameraPan','cameraTilt','cameraZoom','eventName','recSegmentId','trackedRider']
        self._file = pd.DataFrame(columns=columns_incomming_DF)
        self._newlines = pd.DataFrame(columns=columns_incomming_DF)
        
        # Macros of the object
        self._min_lap_time = MIN_LAP_TIME
        self._max_lap_time = MAX_LAP_TIME

        # self.fileL01 = self.file.loc[self.file['loop'] == 'L01']
        # self.newlinesL01 = self.newlines.loc[self.newlines['loop'] == 'L01']
        
        # Parameters for the leaderboard
        self._info_per_transponder = pd.DataFrame(columns=['transponder_id', 'transponder_name', 'L01_laptime_list', 'fastest_lap_time', 'average_lap_time', 'slowest_lap_time', 'total_L01_laps'])
        self._info_per_transponder.set_index('transponder_id', inplace=True)
        self._badman = pd.DataFrame()
        self._diesel = pd.DataFrame()
        self._electric = pd.DataFrame()
        # Debug flag
        self._debug = debug

        # if not new_DF.empty:
        #     self.update(new_DF)

    def _cleanup(self):
        self._file.drop_duplicates(inplace = True)
        # These lines have to be split up
        self._newlines = self._newlines.dropna(subset=['transponder_id', 'loop', 'utcTimestamp'])
        self._newlines = self._newlines.sort_values(by=['transponder_id','utcTime'])

    def preprocess_lap_times(self, df):
        """Operations:
            - Ensure lapTime is numeric
            - Drop rows with NaN in the 'lapTime' column
            - Filter out lap times that are too short or too long"""

        df['lapTime'] = pd.to_numeric(df['lapTime'], errors='coerce')  # Ensure lapTime is numeric
        valid_laps = df[(df['lapTime'] >= self._min_lap_time) & (df['lapTime'] <= self._max_lap_time)]
        valid_laps = valid_laps.dropna(subset=['lapTime']) # Drop rows with NaN in the 'lapTime' column
        return valid_laps

    def update(self, changed_file: pd.DataFrame):
        """
        Loads the changed lines from the DF and appends them to the existing DataFrame.
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
        print(f"changed_file:\n {changed_file}")
        if self._file.empty:
            self._newlines = self.preprocess_lap_times(changed_file)
            self._file = self._newlines.copy()  # Initialize with the first data batch
        else:
            new_rows = pd.merge(
                changed_file, self._file, 
                how='outer', indicator=True, 
                on=['transponder_id', 'utcTimestamp']
            ).loc[lambda x: x['_merge'] == 'left_only'].copy()  # Ensure copy to avoid SettingWithCopyWarning

            # Rename `_x` columns to their original names
            columns_to_rename = {col: col.replace('_x', '') for col in new_rows.columns if col.endswith('_x')}
            new_rows = new_rows.rename(columns=columns_to_rename)
            
            # Drop `_y` columns and the `_merge` column
            new_rows = new_rows[[col for col in new_rows.columns if not col.endswith('_y') and col != '_merge']]
            print(f"new_rows:\n {new_rows}")

            self._newlines = self.preprocess_lap_times(new_rows)
            print(f"self._newlines:\n {self._newlines}")
            self._file = pd.concat([self._file, self._newlines], ignore_index=True)
        
        self._cleanup()  # TODO: does the whole file needs to be cleaned up/sorted after an update, or is cleanup from the newlines enough?
        
        # transponder names aren't being updated here as it is more efficient to do this in the frontend.

        if self._debug:
            print('start calling update functions...\n'+'='*40)

        print("NEW UPDATES COMING UP... ")
        print(f"self._newlines:\n {self._newlines[self._newlines['loop'] == 'L01']}")
        # call all functions that need to be updated
        self._update_transponder_id()
        self._update_L01_laptimes()
        self._update_total_L01_laps()
        self._average_lap_time()
        self._fastest_lap()
        self.slowest_lap()
        self._update_badman()
        self._diesel_engine()
        self._electric_motor()
        print("ALL UPDATES DONE")
        if self._debug:
            print('update done\n'+'='*40)

    def _update_transponder_id(self):
        """
        Function that updates the entries (transponder_id's) in the info_per_transponder DataFrame.
        """        
        new_laptime_indices = set(self._newlines.loc[self._newlines['loop'] == 'L01', 'transponder_id'].to_list())
        info_per_transponder_indices = set(self._info_per_transponder.index.to_list())
        diff = new_laptime_indices - info_per_transponder_indices
        # print(diff)
        
        if diff:
            setdf = {'transponder_id': list(diff),
            'transponder_name': ['' for _ in diff], 
            'L01_laptime_list': [[] for _ in diff],
            'fastest_lap_time': [np.nan for _ in diff], 
            'average_lap_time' : [np.nan for _ in diff], 
            'slowest_lap_time': [np.nan for _ in diff],         
            'total_L01_laps': [0 for _ in diff]
            }
            # print(f'setdf:\n {setdf}')
            df_from_setdf = pd.DataFrame(setdf).set_index('transponder_id')
            self._info_per_transponder = pd.concat([self._info_per_transponder, df_from_setdf], ignore_index=False)
 

    def _update_L01_laptimes(self):
        """
        Function that updates the lap times of the L01 loop for each transponder in self.info_per_transponder DataFrame
        """
        new_laptimes = self._newlines.loc[self._newlines['loop'] == 'L01'].groupby('transponder_id')['lapTime'].apply(list)
        self._info_per_transponder['L01_laptime_list'] = self._info_per_transponder.apply(lambda row: row['L01_laptime_list'] + new_laptimes.get(row.name, []) if row.name in self._newlines['transponder_id'].values else row['L01_laptime_list'], axis=1)
       
        if self._debug:
            print('L01_laptime_list updated\n'+'='*40)

    def _update_total_L01_laps(self):
        """
        Function that updates the total number of (L01) laps each transponder has completed and fills this information in the info_per_transponder DataFrame.
        """
        # TODO: check if this is equal to the length of the L01_laptime_list
        if self._info_per_transponder.empty:
            return 
        self._info_per_transponder['total_L01_laps'] = self._info_per_transponder.apply(lambda row: len(row['L01_laptime_list']) if row['L01_laptime_list'] else 0 ,axis = 1)

        if self._debug:
            print('total_L01_laps updated\n'+'='*40)

    def _average_lap_time(self):
        """
        Function that updates the average laptime of all the updated transponders.
        """
        self._info_per_transponder['average_lap_time'] = self._info_per_transponder.apply(lambda row: np.mean(row['L01_laptime_list']) if row.name in self._newlines['transponder_id'].values and len(row['L01_laptime_list']) > 0 else row['average_lap_time'], axis=1)

        if self._debug:
            print('average_lap_time updated\n'+'='*40)

    def _fastest_lap(self):
        """
        Function that updates the fastest lap time for each transponder.
        """
        self._info_per_transponder['fastest_lap_time'] = self._info_per_transponder.apply(
            lambda row: np.min(row['L01_laptime_list']) if row.name in self._newlines['transponder_id'].values and len(row['L01_laptime_list']) > 0 else row['fastest_lap_time'], 
            axis=1
        )
  
        if self._debug:
            print('fastest_lap_time updated\n'+'='*40)

    def slowest_lap(self):
        """
        Function that updates the slowest lap time for each transponder.
        
        Returns:
            DataFrame: A DataFrame containing the transponder IDs and their respective slowest lap times
        """

        self._info_per_transponder['slowest_lap_time'] = self._info_per_transponder.apply(lambda row: np.max(row['L01_laptime_list']) if row.name in self._newlines['transponder_id'].values and len(row['L01_laptime_list']) > 0 else row['slowest_lap_time'], axis=1)

        if self._debug:
            print('slowest_lap_time updated\n'+'='*40)

    def _update_badman(self):
        """
            Function that calculates the slowest rider of the session and stores it in self.slowest_rider.
        """
        print(f"De dataframe is empty: {self._info_per_transponder.empty}")
        if self._info_per_transponder.empty:
            return
        # self._slowest_rider = self._info_per_transponder.loc[self._info_per_transponder['slowest_lap_time'].idxmax()]
        self._badman = self._info_per_transponder.nlargest(1,'slowest_lap_time')[['slowest_lap_time']]
        if self._debug:
            print('badman updated\n'+'='*40)
    


    def _diesel_engine(self,minimum_incalculated = 10,window = 20):
        """
        Function that identifies the transponder with the most consistent lap times ("Diesel Engine").
        
        Parameters:
            minimum_incalculated (int, optional): The minimum number of laps required to be considered for the diesel engine.
            window (int, optional): The window size for the rolling standard deviation.
        
        Result:
        ---------
            self.diesel (DataFrame): DataFrame containing the transponder ID, standard deviation on his laptimes, average lap time, CV (Coefficient of Variation) and rolling variability for the most consistent rider.
        """
        # Filter only laps recorded at loop 'L01' to focus on complete laps
        df_filtered = self._file.loc[self._file['loop'] == 'L01']
        
        # Drop any rows where 'lapTime' is missing
        df_filtered = df_filtered.dropna(subset=['lapTime'])
        
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
        # --> done in the frontend
        if self._debug:
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

        if self._debug:
            print('electric_motor updated\n'+'='*40)
    
    def update_transponder_names(self, transponder_names: pd.DataFrame):
        """
        Update the transponder names in the info_per_transponder DataFrame.

        Parameters:
            transponder_names (pd.DataFrame): DataFrame containing two columns: 'transponder_id' and 'transponder_name'. 'transponder_id' should be set as the index of this dataframe.
        """
        self._info_per_transponder['transponder_name'] = self._info_per_transponder.index.map(transponder_names['transponder_name'])

    def save_to_csv(self):
        """
        Save the current state of the DataFrame to a CSV file.

        Parameters:
            filename (str): The name of the file to save the DataFrame to.
        """
        filename = 'api\static\csv\lap_times.csv'
        if os.path.exists(filename):
            os.remove(filename)  # Remove the existing file
            if self._debug:
                print(f"Existing file {filename} removed.")

        self._file.to_csv(filename, index=False)
        if self._debug:
            print(f'DataFrame saved to {filename}')
    
    # GETTERS AND SETTERS
    @property
    def slowest_rider(self):
        return getattr(self, '_slowest_rider', None)
    
    @property
    def diesel(self):
        return getattr(self,'_diesel', None)
    
    @property
    def electric(self):
        return getattr(self, '_electric', None)
    
    @property
    def info_per_transponder(self):
        return getattr(self, '_info_per_transponder', None)
    
    @property
    def file(self):
        return getattr(self, '_file', None)
    
    @property
    def badman(self):
        return getattr(self, '_badman', None)
    
    @property
    def min_lap_time(self):
        return getattr(self, '_min_lap_time', None)
    
    @min_lap_time.setter
    def min_lap_time(self, new_min_lap_time):
        self._min_lap_time = new_min_lap_time
        if self._debug:
            print(f'Minimum lap time set to {new_min_lap_time}')

    @property
    def max_lap_time(self):
        return getattr(self, '_max_lap_time', None)

    @max_lap_time.setter
    def max_lap_time(self, new_max_lap_time):
        self._max_lap_time = new_max_lap_time
        if self._debug:
            print(f'Maximum lap time set to {new_max_lap_time}')
    
    @property
    def debug(self):
        return getattr(self, '_debug', None)
    
    @debug.setter
    def debug(self, new_debug):
        self._debug = new_debug
        if self._debug:
            print(f'Debug mode set to {new_debug}')