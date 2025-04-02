# Class for the database
class TransponderDataBase():
    def __init__(self):
        self._database = {}
    def update(self, dataDict):
        for transponder_ID, name in dataDict.items():
            self._database[transponder_ID] = name
    
    @property
    def get_database(self):
        return self._database
