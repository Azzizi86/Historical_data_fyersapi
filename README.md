
# Historical Data with Fyers API (v3)
My Fyers API v3 Historical Data Pipeline

Note: This is a personal project built for custom historical data extraction. You may need to tailor parts of the code (e.g., saving logic, symbols list) to fit your own use case.

    Before You Begin
    Ensure you have a solid understanding of Pandas, SQL (SQLite3), and Fyers API v3.
    You should also read the official Fyers API v3 documentation for detailed information.
-----------
Overview

This project provides Python scripts to fetch and save historical market data using Fyers API v3. It supports both single and multiple symbols, including equity and options. The data can be saved in Parquet format and/or SQLite3 database based on your configuration.

File Descriptions
# 1.1 - Historical Data: Single Symbol (Equity Only)

Fetches historical data for a single equity symbol.

Set the following variables:

    exchange = "NSE"
    symbol_1 = "NIFTY50-INDEX"
    symbol_2 = "NIFTY"
    time_frame = "5S"          # Timeframes: '5S' = 5 seconds, '1', '2', '3' = minutes, '1D' = daily
    start_date = "2024-03-28"  # Start date (YYYY-MM-DD)
    end_date = "2025-04-03"    # End date (YYYY-MM-DD)

# 1.2 - Historical Data: Multiple Symbols (Equity Only)

Fetches historical data for multiple equity symbols.

Modify the scrip_list() function to include your desired symbols. The script will iterate over each symbol and:

  Download data using Fyers API

  Append it to a local SQLite3 database

  Optionally save in Parquet format (recommended)

Example usage:

    for symbol_1 in scrip_list():
        symbol_1 = symbol_1
        time_frame = "1"
        start_date = "YYYY-MM-DD"
        end_date = "YYYY-MM-DD"

Note: The script appends new data; it does not create duplicate entries.
# 1.3 - Historical Data: Single Option (Derivatives)

Fetches historical data for a single option instrument.

Set the following variables:

    exchange = "NSE"
    symbol_1 = "NSE:NIFTY2550824500CE"  # Example option symbol
    symbol_2 = "NIFTY"
    time_frame = "1"
    start_date = "2025-05-01"
    end_date = "2025-05-05"
    flag = 1  # Use 1 if symbol includes Open Interest (OI), otherwise 0

# Instructions

  1. Set the required variables in the script(s) as shown above.

  2. Find the save file section inside the code and either:

      Uncomment the saving logic, or

      Write your own logic to store the data.

  3. On first run, the script will generate an authorization link.

      Click the link, authorize, and paste the code back into the terminal.

      It will create an access_token.txt file.

  4. On subsequent runs, you don’t need to reauthorize unless the token expires.

      In that case, delete the old access_token.txt and repeat step 3.

# Notes

  -  Only Parquet format is supported for saving historical data (recommended for efficiency).

  - Tailor the scripts to your requirements if you're handling more complex data workflows.

