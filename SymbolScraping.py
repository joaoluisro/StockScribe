import pandas as pd
import numpy as np
import yfinance as yf
import time
import random

# Dictionary of indices, their Wikipedia URLs, and table indices (0-based) to fetch the list of stocks
index_info = {
    "S&P 500": {"url": "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", "table_index": 0},
    "Dow Jones": {"url": "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average", "table_index": 2},
    "NASDAQ 100": {"url": "https://en.wikipedia.org/wiki/NASDAQ-100", "table_index": 4},
    "Russell 2000": {"url": "https://en.wikipedia.org/wiki/Russell_2000_Index", "table_index": 2}, #Wiki doesnt actually list all Russsel
    "FTSE 100": {"url": "https://en.wikipedia.org/wiki/FTSE_100_Index", "table_index": 4},
    "DAX": {"url": "https://en.wikipedia.org/wiki/DAX", "table_index": 4}
}

def fetch_index_constituents(index_name):
    """The Fetsch Index constituents function is called by the scrape indices function and simply pulls the infomration from teh Index info dictionary
    It uses pandas to scrap the stock lists off Wikipedia (Russel doesnt work not all listed) and returns a dataframe of all of the wikitables contents
    
    FTSE100 Stocks needed to have .L appended to be correctly collected aggreagted by YFinance (DAX doesnt have this problem Wiki already includes .DE)
    Added a check to replace . to - for YFinance (Some wikitables have headers as Ticker or Symbol)
    """
    index_data = index_info.get(index_name)
    if not index_data:
        print(f"Index '{index_name}' is not supported.")
        return None
    url = index_data["url"]
    table_index = index_data["table_index"]
    try:
        tables = pd.read_html(url)
        constituents = tables[table_index]

        # Check if the index name is FTSE 100, and append '.L' to the ticker symbols
        if index_name == "FTSE 100":
            constituents['Ticker'] = constituents['Ticker'].apply(lambda x: str(x) + '.L')

        # Check for 'Ticker' or 'Symbol' column and replace '.' with '-'
        if 'Ticker' in constituents.columns:
            constituents['Ticker'] = constituents['Ticker'].apply(lambda x: str(x).replace('.', '-'))
        elif 'Symbol' in constituents.columns:
            constituents['Symbol'] = constituents['Symbol'].apply(lambda x: str(x).replace('.', '-'))


        return constituents
    except Exception as e:
        print(f"Error fetching data for {index_name}: {e}")
        return None

def fetch_stock_data(symbol, market_returns, start_date, end_date):
    """Fetch stock data for a given symbol. Used by upload symbol script and Single symbol functions. Takes a symbol (Make sure it works on YFinance), a dataframe of SP500 returns, and 2 time frame variables.
    Extracts various information from YFinance API with Delays added to avoid rate limiting, and returns a dictionary of this information.
    """
    try:
        print(f"Fetching data for {symbol}...")
        stock = yf.Ticker(symbol)
        
        # Get the historical data with a broad date range to determine the first available date
        hist = stock.history(period="max")
        
        if hist.empty:
            print(f"No data for {symbol}. Skipping.")
            return None
        
        # Get the first available trading date (this is the earliest date in the historical data)
        first_trading_date = hist.index.min().strftime('%Y-%m-%d')
        
        # If the stock started trading after the specified start date, adjust the start date
        if pd.to_datetime(first_trading_date) > pd.to_datetime(start_date):
            print(f"Stock {symbol} started trading on {first_trading_date}. Adjusting start date.")
            start_date = first_trading_date
        
        # Fetch historical data within the adjusted date range
        hist = stock.history(start=start_date, end=end_date)

        print(f"For {start_date} / {end_date}")
        
        if hist.empty:
            print(f"No data for {symbol} in the given date range. Skipping.")
            return None

        hist.index = hist.index.tz_localize(None)

        delay = 1

        total_volume = hist['Volume'].sum()
        average_yearly_volume = hist['Volume'].mean() * 252
        sector = stock.info.get('sector', 'N/A')
        industry = stock.info.get('industry', 'N/A')
        sector_industry = f"{sector} / {industry}"
        dividend_status = 'Yes' if stock.info.get('dividendYield', 0) > 0 else 'No'
        pe_ratio = stock.info.get('trailingPE', np.nan)
        time.sleep(random.uniform(delay, delay + 1))  # Random delay between 1-2 seconds
        beta = stock.info.get('beta', np.nan)
        pe_yearly = hist['Close'].pct_change().mean() * 252  # Use this to approximate yearly returns
        sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
        sma_200 = hist['Close'].rolling(window=200).mean().iloc[-1]
        rolling_max = hist['Close'].cummax()
        drawdown = (hist['Close'] - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        risk_free_rate = 0.02

        time.sleep(random.uniform(delay, delay + 1))  # Random delay between 1-2 seconds

        # Check if the provided start date is older than the first trade date, then the data is incomplete within the range.
        is_data_incomplete = pd.to_datetime(start_date) > pd.to_datetime(first_trading_date)

        # Calculate the historical range
        first_trading_date_dt = pd.to_datetime(first_trading_date)
        end_date_dt = pd.to_datetime(end_date)
        start_date_dt = pd.to_datetime(start_date)
        
        # Calculate the number of years and months in the historical range 
        years_diff = (end_date_dt - first_trading_date_dt).days // 365
        months_diff = (end_date_dt - first_trading_date_dt).days % 365 // 30

        data_years_diff = (end_date_dt - start_date_dt).days // 365
        data_months_diff = (end_date_dt - start_date_dt).days % 365 // 30
        
        historical_range = f"{years_diff} years, {months_diff} months" if years_diff > 0 else f"{months_diff} months"
        data_range = f"{data_years_diff} years, {data_months_diff} months" if years_diff > 0 else f"{data_months_diff} months"
        

        stock_returns = hist['Close'].pct_change().dropna()
        combined = pd.DataFrame({
            'Stock': stock_returns.squeeze(),
            'Market': market_returns.squeeze()
        }).dropna()

        excess_returns = stock_returns - risk_free_rate / 252  # Convert yearly risk-free rate to daily
        sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252)  # Annualized Sharpe Ratio

        correlation = combined['Stock'].corr(combined['Market'])

        time.sleep(random.uniform(delay, delay + 1))  # Random delay between 1-2 seconds

        print(f"Data fetched for {symbol}.")
        return {
            'Symbol': symbol,
            'Total Volume': total_volume,
            'Average Yearly Volume': average_yearly_volume,
            'Sector/Industry': sector_industry,
            'Correlation with Market': correlation,
            'Beta': beta,
            'Dividend Pays': dividend_status,
            'P/E Ratio': pe_ratio,
            'SMA 50': sma_50,
            'SMA 200': sma_200,
            'Max Drawdown': max_drawdown,
            'Sharpe Ratio': sharpe_ratio,
            'Incomplete Data': is_data_incomplete,
            'Data Range': data_range,
            'First Trading Date': first_trading_date,
            'Historical Range': historical_range

        }
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None
    

def scrape_indices(index_choice=None):
    """
    
    """
    if index_choice is None:
        print("\nAvailable indices:")
        for i, name in enumerate(index_info.keys(), 1):
            print(f"{i}. {name}")
        choice = input("\nEnter the number of the index you'd like to fetch (or 'q' to quit): ").strip()
    else:
        choice = str(index_choice)

    if choice.lower() == 'q':
        return
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(index_info):
        print("Invalid choice. Try again.")
        return

    index_name = list(index_info.keys())[int(choice) - 1]
    constituents = fetch_index_constituents(index_name)
    if constituents is not None:
        print(constituents.head())
        save_choice = input("Save constituents to CSV? (y/n): ").strip().lower()
        if save_choice == 'y':
            filename = f"{index_name.replace(' ', '_')}_constituents.csv"
            constituents.to_csv(filename, index=False)
            print(f"Data saved to {filename}")

def upload_symbol_script(file_path="D:/Shares/Leopold/Test Workspace/Symbols_preUpdate.xlsx", sheetname="SP500", start_date="2001-01-01", end_date="2024-12-31", output_file_path="D:/Shares/Leopold/Test Workspace/SP500_New.xlsx"):
    """Fetch stock data for symbols from a provided Excel sheet."""
    if file_path is None:
        file_path = input("Enter the Excel file path: ").strip()
    if sheetname is None:
        sheetname = input("Enter the sheet name: ").strip()
    if start_date is None:
        start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    if end_date is None:
        end_date = input("Enter end date (YYYY-MM-DD): ").strip()

    new_sorting_df = pd.read_excel(file_path, sheet_name=sheetname)
    symbols = new_sorting_df['Symbol'].dropna().unique()

    market_index = '^GSPC'
    market_data = yf.download(market_index, start=start_date, end=end_date)
    market_data.index = market_data.index.tz_localize(None)
    market_returns = market_data['Close'].pct_change().dropna()

    results = []
    for index, symbol in enumerate(symbols):
        data = fetch_stock_data(symbol, market_returns, start_date, end_date)
        if data:
            results.append(data)
        time.sleep(1)

    results_df = pd.DataFrame(results)
    updated_new_sorting_df = new_sorting_df.merge(results_df, on='Symbol', how='left')

    if output_file_path is None:
        output_file_path = input("Enter output Excel file path: ").strip()
    with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
        updated_new_sorting_df.to_excel(writer, sheet_name=sheetname, index=False)

    print(f"Updated file saved to {output_file_path}")

def single_symbol(stock_symbol=None, start_date=None, end_date=None):
    """Fetch data for a single stock symbol."""
    og_symbol = stock_symbol

    if stock_symbol is None:
        stock_symbol = input("Enter stock symbol: ").strip()
    if start_date is None:
        start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    if end_date is None:
        end_date = input("Enter end date (YYYY-MM-DD): ").strip()

    market_index = '^GSPC'
    market_data = yf.download(market_index, start=start_date, end=end_date)
    market_data.index = market_data.index.tz_localize(None)
    market_returns = market_data['Close'].pct_change().dropna()

    stock_data = fetch_stock_data(stock_symbol, market_returns, start_date, end_date)
    if stock_data and og_symbol is None :
        print("\nStock Data:")
        for key, value in stock_data.items():
            print(f"{key}: {value}")
    else:
        print("No data to display.")

    if stock_data and og_symbol is not None :
        output = "\n".join(f"{key}: {value}" for key, value in stock_data.items())
        return output
    else:
        output = "Error"
        return output

    

def main():
    """Main function to choose the operation."""
    while True:
        print("\nChoose an operation:")
        print("1. Updated/Scrape index list")
        print("2. Upload Symbol xlsx list")
        print("3. Fetch data for a single symbol")
        print("4. Quit")

        choice = input("Enter your choice: ").strip()

        if choice == '1':
            scrape_indices()
        elif choice == '2':
            upload_symbol_script()
        elif choice == '3':
            single_symbol()
        elif choice == '4':
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
