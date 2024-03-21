import pandas as pd
import datetime

def read_records(startdate, enddate):
    # Read the CSV file into a DataFrame
    df = pd.read_csv('2023.csv')

    # Convert the 'date' column to datetime type
    df['date'] = pd.to_datetime(df['date'])

    # Filter records based on start date and end date
    filtered_df = df[(df['date'] >= startdate) & (df['date'] <= enddate)]

    # Convert the filtered DataFrame to a list of dictionaries
    records = filtered_df.to_dict('records')

    return records
startdate =  datetime.datetime(2023, 1, 2, 9, 15, tzinfo=datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
enddate =  datetime.datetime(2023, 2, 1, 15, 15, tzinfo=datetime.timezone(datetime.timedelta(hours=5, minutes=30)))

rec=read_records(startdate,enddate)
print(rec)
