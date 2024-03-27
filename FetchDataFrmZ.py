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

start_year=2022
end_year=2023
start_month=1
end_month=12
start_day=1
end_day=28

time_interval="hour"

startdate = datetime.datetime(start_year, start_month, start_day)
enddate = datetime.datetime(end_year, end_month, end_day)

# Initialize an empty list to store the data
all_records = []

# Check if the number of days is greater than or equal to 400
if (enddate - startdate).days >= 400:
    # Iterate over each year from start_year to end_year
    for year in range(start_year, end_year + 1):
        # Define the start and end dates for the current year
        year_start = datetime.datetime(year, 1, 1)
        year_end = datetime.datetime(year, 12, 31)

        # Fetch historical data for the current year
        records = kite.historical_data(token, year_start, year_end, time_interval)

        # Append the records to the list
        if records:
            all_records.extend(records)
            print(f"Data fetched for year {year}")
else:
    # Fetch historical data for the entire duration
    all_records = kite.historical_data(token, startdate, enddate, time_interval)

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame.from_records(all_records)

# Save the DataFrame to a CSV file
filename = f"{start_year}_to_{end_year}.csv"
df.to_csv(filename, index=False)
print(f"Data saved to {filename}")
