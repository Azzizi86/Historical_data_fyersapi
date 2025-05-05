from fyers_apiv3 import fyersModel
import pandas as pd
import os
from datetime import datetime, timedelta, timezone
import pytz

def login_credentials(): #
        
    app_id = "X8K3EI61DV-100"
    secret_id = "D7ZDCAXY47"
    return app_id,secret_id

app_id,secret_id = login_credentials() # FOR LOGIN AND DATA FETCHING


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
        "cont_flag":"1",
        "oi_flag": f"{flag}"
    }

    response = fyers.history(data=data)
    print(response)

    df = pd.DataFrame(response)

    # Split the 'candles' column into separate columns which is coming from response
    df[['timestamp', 'open', 'high', 'low', 'close', 'volume','oi']] = pd.DataFrame(df['candles'].tolist(), index=df.index)
    df.drop(columns=['candles',"code","message","s"], inplace=True)

    # WITH THE USE OF FUNCTION CONVERT DATE TIME INTO GMT FROM EPOCH
    df['timestamp'] = df['timestamp'].apply(lambda x: convert_to_kolkata_time(x))
    df['symbol_name'] = symbol_1
    df['date'] = df['timestamp'].dt.strftime("%Y-%m-%d")
    
    #---- to save in parquet file format  OR CSV ----
    # weekly_data.to_parquet(f"f{symbol_2} st_date {start_date} ed_date {end_date}.parquet", engine="pyarrow", compression="snappy")

    return response

exchange = "NSE" #its for both data one and data two
# symbol_1 = "NIFTY50-INDEX"  #this is for option chain data and for extract_close_price # for nifty
symbol_1 = "NSE:NIFTY2550824500CE"  
symbol_2 = "NIFTY"
time_frame = "1" 
start_date = "2025-05-01"
end_date = "2025-05-05"
flag = 1 # if symbol contains oi then 1 else 0

historical_data()