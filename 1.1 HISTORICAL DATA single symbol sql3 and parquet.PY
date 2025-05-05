# Import the required module from the fyers_apiv3 package
from fyers_apiv3 import fyersModel
import pandas as pd
import os
import xlwings as xw
from datetime import datetime, timedelta, timezone
import sqlite3



def start_sql():
    global conn
    # Connect to SQLite database (creates the file if it doesn't exist)
    database_path = r'C:\Users\asifa\OneDrive\python\API\FYERS APIs\historical data\single symbol historical data\DATABASE\SYMBOL DATA.db'
    conn = sqlite3.connect(database_path)

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # Create a table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historical_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER
        )
    ''')
    # Commit and close
    conn.commit()


def login_Credentials(): #to hide my credentials 

    app_id = "X8K3EI61DV-100"
    secret_id = "D7ZDCAXY47"
    return app_id,secret_id

app_id,secret_id = login_Credentials()

def login():
    if not os.path.exists('access_token.txt'): 

        # Replace these values with your actual API credentials
        client_id = app_id
        secret_key = secret_id
        redirect_uri = "https://trade.fyers.in/api-login/redirect-uri/index.html"
        response_type = "code"  
        state = "sample_state"

        # Create a session model with the provided credentials
        session = fyersModel.SessionModel(
            client_id=client_id,
            secret_key=secret_key,
            redirect_uri=redirect_uri,
            response_type=response_type
        )

        # Generate the auth code using the session model
        response = session.generate_authcode()

        # Print the auth code received in the response
        print(response)
        auth_code = input("Enter Auth Code : ")
        grant_type = "authorization_code"  
        session = fyersModel.SessionModel(
            client_id=client_id,
            secret_key=secret_key, 
            redirect_uri=redirect_uri, 
            response_type=response_type, 
            grant_type=grant_type
        )
        session.set_token(auth_code)
        access_token = session.generate_token()
        access_token = access_token['access_token']
        print(access_token)
        with open("access_token.txt","w") as f:
            f.write(access_token)
    else:
        with open("access_token.txt","r") as f:
            access_token = f.read()
    return access_token

def convert_to_kolkata_time(utc_timestamp): # to convert epoch time in readable format

    # Convert the timestamp to a timezone-aware UTC datetime
    utc_time = datetime.fromtimestamp(utc_timestamp, timezone.utc)
    # Convert UTC time to Kolkata time
    kolkata_time = utc_time.astimezone(timezone(timedelta(hours=5, minutes=30)))
    return kolkata_time


def historical_data(): # core of data fetching 
    global exchange,symbol_1,symbol_2,time_frame,start_date,end_date
    fyers = fyersModel.FyersModel(client_id=app_id, is_async=False, token=login(), log_path="")

    data = {
        "symbol":f"{exchange}:{symbol_1}",
        "resolution":time_frame,
        "date_format":"1",
        "range_from":start_date,
        "range_to":end_date,
        "cont_flag":"1"
    }

    response = fyers.history(data=data)
    print(response)
    df = pd.DataFrame(response)

    

    # Split the 'candles' column into separate columns which is coming from response
    df[['DATE/TIME', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']] = pd.DataFrame(df['candles'].tolist(), index=df.index)
    df.drop(columns=['candles',"code","message","s"], inplace=True)
    # WITH THE USE OF FUNCTION CONVERT DATE TIME INTO GMT FROM EPOCH
    df['DATE/TIME'] = df['DATE/TIME'].apply(lambda x: convert_to_kolkata_time(x))

    if time_frame == "1D":
        # Convert to short date format (YYYY-MM-DD)
        df['DATE/TIME'] = df['DATE/TIME'].dt.strftime('%Y-%m-%d')
    else:
        pass

    # Convert DATE/TIME to datetime and set as index
    df["DATE/TIME"] = pd.to_datetime(df["DATE/TIME"])
    df.set_index("DATE/TIME", inplace=True)

    # Resample to weekly (Friday to Thursday)
    weekly_data = df.resample('W-THU').agg({
        'OPEN': 'first',
        'HIGH': 'max',
        'LOW': 'min',
        'CLOSE': ['last', 'mean', 'min', 'max']
    })

    # Print columns before renaming to debug
    print("Columns before renaming:", weekly_data.columns)

    # Rename columns correctly based on the actual number of columns
    weekly_data.columns = ['OPEN', 'HIGH', 'LOW', 'CLOSE', 'AVG_CLOSE', 'MIN_CLOSE', 'MAX_CLOSE']

    # Compute difference between max and min close of the week
    weekly_data['DIFF_CLOSE'] = weekly_data['MAX_CLOSE'] - weekly_data['MIN_CLOSE']

    # Reset index
    weekly_data.reset_index(inplace=True)

    #---- to save sql ------
    # df.to_sql("historical_data", conn, if_exists="replace", index=False)

    #---- to save in parquet file format ----
    # weekly_data.to_parquet(f"f{symbol_2} st_date {start_date} ed_date {end_date}.parquet", engine="pyarrow", compression="snappy")


# user variable for funcitons
exchange = "NSE" #its for both data one and data two
symbol_1 = "NIFTY2540323600CE"  #this is for option chain data and for extract_close_price
symbol_2 = "NIFTY"
time_frame = "5S" 
start_date = "2024-03-28"
end_date = "2025-04-03"
# expiry = "24805"
# expiry = '24801'


start_sql()
historical_data()
