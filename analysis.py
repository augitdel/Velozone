import pandas as pd

MIN_LAP_TIME = 13
MAX_LAP_TIME = 50

def preprocess_lap_times(df):
    """Operations:
    - Ensure lapTime is numeric
    - Drop rows with NaN in the 'lapTime' column
    - Filter out lap times that are too short or too long"""

    df['lapTime'] = pd.to_numeric(df['lapTime'], errors='coerce')  # Ensure lapTime is numeric
    valid_laps = df[(df['lapTime'] >= MIN_LAP_TIME) & (df['lapTime'] <= MAX_LAP_TIME)]
    valid_laps = valid_laps.dropna(subset=['lapTime']) # Drop rows with NaN in the 'lapTime' column

    return valid_laps

def remove_initial_lap(df):
    '''If df contains multiple events, remove the first lap for each event, for each transponder.
    So only the second appearance of each transponder at each loop shall be considered.

    What if someone continues riding? Ignore for now, we only analyze by session anyway.'''
    dropped_entries = []

    for event in df['eventName'].unique():
        # Loop over all transponders in the event
        for transponder in df[df['eventName'] == event]['transponder_id'].unique():
            # Loop over all loops
            for loop in df['loop'].unique():
                mask = (df['eventName'] == event) & (df['transponder_id'] == transponder) & (df['loop'] == loop)
                # Skip if mask is empty
                if mask.sum() == 0:
                    continue
                try:
                    first_lap_idx = df[mask].index[0]
                    df = df.drop(first_lap_idx)
                    dropped_entries.append(first_lap_idx)
                except:
                    print(f"Could not drop first lap for event {event} and transponder {transponder}.")

    # print(dropped_entries)
    print(f"Dropped {len(dropped_entries)} initial lap entries.")
    return df