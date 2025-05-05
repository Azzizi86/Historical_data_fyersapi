# Import the required module from the fyers_apiv3 package
from fyers_apiv3 import fyersModel
import pandas as pd
import os
import xlwings as xw
from datetime import datetime, timedelta, timezone
import datetime as dt
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
                            timestamp DATETIME NOT NULL,
                            open REAL,
                            high REAL,
                            low REAL,
                            close REAL,
                            volume INTEGER,
                            symbol_name TEXT NOT NULL,
                            date DATE,
                            PRIMARY KEY (symbol_name, timestamp)
                        );
    ''')
    # Commit and close
    conn.commit()


def login_credentials():
        
    app_id = 
    secret_id = 
    
    return app_id,secret_id

app_id,secret_id = login_credentials()

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

def convert_to_kolkata_time(utc_timestamp):
    # Convert the timestamp to a timezone-aware UTC datetime
    utc_time = datetime.fromtimestamp(utc_timestamp, timezone.utc)
    # Convert UTC time to Kolkata time
    kolkata_time = utc_time.astimezone(timezone(timedelta(hours=5, minutes=30)))
    return kolkata_time

def historical_data():
    global exchange,symbol_1,symbol_2,time_frame,start_date,end_date
    fyers = fyersModel.FyersModel(client_id=app_id, is_async=False, token=login(), log_path="")

    data = {
        "symbol":symbol_1,
        "resolution":time_frame,
        "date_format":"1",
        "range_from":start_date,
        "range_to":end_date,
        "cont_flag":"1"
    }

    response = fyers.history(data=data)
    # print(response)
    df = pd.DataFrame(response)
    # print(df)

    # Split the 'candles' column into separate columns which is coming from response
    df[['timestamp', 'open', 'high', 'low', 'close', 'volume']] = pd.DataFrame(df['candles'].tolist(), index=df.index)
    df.drop(columns=['candles',"code","message","s"], inplace=True)

    # WITH THE USE OF FUNCTION CONVERT DATE TIME INTO GMT FROM EPOCH
    df['timestamp'] = df['timestamp'].apply(lambda x: convert_to_kolkata_time(x))
    df['symbol_name'] = symbol_1
    df['date'] = df['timestamp'].dt.strftime("%Y-%m-%d")

    data_wrangling(df)

def data_wrangling (df):

    # Check for existing data in the database
    existing_data = pd.read_sql_query(f"SELECT * FROM historical_data WHERE symbol_name = '{df['symbol_name'][0]}' AND date IN ({','.join([f'\'{d}\'' for d in df['date'].unique()])})", conn)

    # Filter out rows that already exist in the database
    if not existing_data.empty:
        df = df[~df['date'].isin(existing_data['date'])]

    # Insert the DataFrame into the SQLite database
    df.to_sql('historical_data', conn, if_exists='append', index=False)


#--------------------------------------------------
############## merged list of stock ###############
#--------------------------------------------------

def scrip_list():
    nse_symbol_list = ["NSE:NIFTY50-INDEX","NSE:FINNIFTY-INDEX","NSE:MIDCPNIFTY-INDEX","NSE:NIFTYIT-INDEX",
                    "NSE:NIFTYBANK-INDEX","NSE:INDIAVIX-INDEX"]
    bse_symbol_list = ["BSE:SENSEX-INDEX","BSE:BANKEX-INDEX"]

    symbols_name_nse_stock = ["KOTAKBANK","HINDUNILVR","TITAN","BRITANNIA","ASIANPAINT","TECHM","CIPLA","RELIANCE","TATAMOTORS",
                    "TCS","INFY","WIPRO","HDFCBANK","GAIL"]

    symbols_list = nse_symbol_list + bse_symbol_list

    for symbol_name in symbols_name_nse_stock:
        exch = "NSE:"
        lst_name = "-EQ"
        scrip_name = f'{exch}{symbol_name}{lst_name}'
        symbols_list.append(scrip_name)

    return symbols_list

def date():

    end_date = dt.date.today()
    # end_date = dt.datetime.strptime('2024-12-31', '%Y-%m-%d').date()
    start_date = end_date - dt.timedelta(days=100)
    
    return start_date,end_date
 
#**************************************************

start_date,end_date = date()
start_sql()

for symbol_1 in scrip_list():

    # user variable for funcitons
    symbol_1 = symbol_1
    symbol_2 = "NIFTY"
    time_frame = "1" 
    start_date = start_date
    end_date = end_date

    historical_data()


# ------------------------------------------------------

############  Testing purpose  #########################

# start_date,end_date = date()

# # user variable for funcitons
# symbol_1 = "NSE:NIFTY50-INDEX"
# symbol_2 = "NIFTY"
# time_frame = "1" 
# start_date = start_date
# end_date = end_date

# historical_data()
