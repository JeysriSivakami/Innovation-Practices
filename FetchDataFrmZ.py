import numpy as np
import datetime
from kiteconnect import KiteConnect
from modules import auth
from modules import historical_data
import pandas as pd

userdata = auth.get_userdata()
kite = KiteConnect(api_key=userdata['api_key'])
kite.set_access_token(userdata['access_token'])

token=2754817

year=2018
startdate = datetime.datetime(year, 1, 1)
enddate = datetime.datetime(year, 12, 31)
records = kite.historical_data(token, startdate, enddate, "hour")
#print(records)
# Convert dictionary to DataFrame
if records:
    print('first record:',records[0])
    print('success')
    df = pd.DataFrame.from_dict(records)
    # Save DataFrame to CSV file
    filename = str(start_year) + '.csv'
    df.to_csv(filename, index=False)  
else:
    print(records)
    print('no records found')
