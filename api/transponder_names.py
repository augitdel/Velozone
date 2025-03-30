# Class for the database
class DataBase():
    def __init__(self):
        self._database = {}
    def update(self, dataList):
        for data in dataList:
            transponder_ID, name = data
            self._database[transponder_ID] = name
    
    @property
    def get_database(self):
        return self._database
