import numpy as np
import pandas as pd
from faker import Faker
import random
from api.data_analysis_branch import *

data = {'transponder_id': ['KS98417', 'LR40395', 'KL02453', 'LL39835', 'KS98417', 'LL39835'],
        'loop': ['L02', 'L03', 'L03', 'L01', 'L03', 'L02'],
        'utcTimestamp': [1.744052e+09, 1.744050e+09, 1.744050e+09, 1.744050e+09, 1.744050e+09, 1.744052e+09],
        'utcTime': ['2025-04-07 18:46:25.555000', '2025-04-07 18:16:28.029000', '2025-04-07 18:16:28.237000', '2025-04-07 18:16:27.832000', '2025-04-07 18:16:28.976000', '2025-04-07 18:46:29.916000'],
        'lapTime': [28.496, 27.551, 27.960, 22.520, 28.519, 22.581],
        'lapSpeed': [None, None, None, None, None, None],
        'maxSpeed': [None, None, None, None, None, None],
        'cameraPreset': [None, None, None, None, None, None],
        'cameraPan': [None, None, None, None, None, None],
        'cameraTilt': [None, None, None, None, None, None],
        'cameraZoom': [None, None, None, None, None, None],
        'eventName': ['Vlaamse wielerschool', 'Vlaamse wielerschool', 'Vlaamse wielerschool', 'Vlaamse wielerschool', 'Vlaamse wielerschool', 'Vlaamse wielerschool'],
        'recSegmentId': ['L02', 'L03', 'L03', 'L01', 'L03', 'L02'],
        'trackedRider': [None, None, None, None, None, None]}
df = pd.DataFrame(data)
print(df)

session_data = DataAnalysis(None)
session_data.update(df)
print(session_data.info_per_transponder)