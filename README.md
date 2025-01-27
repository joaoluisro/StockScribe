# Stock Market Data Scraping and Analysis

This repository contains a Python script for scraping and analyzing stock market data from various sources such as Wikipedia and Yahoo Finance. The script is designed to handle multiple stock symbols, process Excel files, and retrieve data for single-symbol queries.

## Features

- **Fetch stock data from Wikipedia:**  
  Retrieve the latest stock listings from public Wikipedia pages.
  
- **Download data from Yahoo Finance:**  
  Fetch historical stock data, including price, volume, and other financial metrics.

- **Excel file processing:**  
  Load and process stock symbols from Excel spreadsheets.

- **Single-symbol queries:**  
  Fetch stock data for individual symbols and perform analysis.

## Requirements

Ensure you have the following dependencies installed before running the script:

```bash
pip install pandas openpyxl requests yfinance beautifulsoup4
```

## Usage

### Running the script

1. **Fetching stock data from Wikipedia:**
   ```python
   from SymbolScraping import fetch_wikipedia_stock_data
   data = fetch_wikipedia_stock_data()
   print(data.head())
   ```

2. **Downloading Yahoo Finance data for a list of symbols:**
   ```python
   from SymbolScraping import fetch_yahoo_finance_data
   symbols = ['AAPL', 'GOOG', 'MSFT']
   stock_data = fetch_yahoo_finance_data(symbols)
   print(stock_data)
   ```

3. **Processing symbols from an Excel file:**
   ```python
   from SymbolScraping import process_excel_file
   filepath = 'stock_symbols.xlsx'
   symbols = process_excel_file(filepath)
   print(symbols)
   ```

4. **Retrieving stock data for a single symbol:**
   ```python
   from SymbolScraping import fetch_single_stock_data
   symbol = 'TSLA'
   tsla_data = fetch_single_stock_data(symbol)
   print(tsla_data)
   ```

## File Structure

```
.
├── SymbolScraping.py    # Main script for scraping and processing stock data
├── README.md            # Documentation and usage guide
├── requirements.txt     # List of dependencies
└── stock_symbols.xlsx   # Example file with stock symbols (not included in repo)
```

## Example Output

```plaintext
Fetching stock data from Wikipedia...
Symbol    Company Name
AAPL      Apple Inc.
GOOG      Alphabet Inc.
MSFT      Microsoft Corporation
```

## Contribution

Contributions are welcome! If you find issues or have suggestions for improvement, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License.

## Contact

For any questions or inquiries, reach out via [your email or GitHub profile].
