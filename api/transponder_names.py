import pandas as pd

# Class for the database
import pandas as pd
class TransponderDataBase():
    def __init__(self):
        self._database = pd.DataFrame()
    def update(self, dataDict):
        for transponder_ID, name in dataDict.items():
            self._database[transponder_ID] = name
    
    @property
    def get_database(self):
        return self._database
    def to_dataframe(self):
        df = pd.DataFrame(
            list(self._database.items()),
            columns=["transponder_id", "transponder_name"]
        )
        return df
