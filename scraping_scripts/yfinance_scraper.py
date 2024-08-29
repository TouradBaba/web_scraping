import yfinance as yf
from datetime import datetime
import h5py
import pandas as pd
import json
import os

def scrape_stock_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period='1d')

    if not data.empty:
        last_row = data.iloc[-1]
        stock_data = {
            'price': last_row['Close'],
            'change': last_row['Close'] - last_row['Open'],
            'change_percent': (last_row['Close'] - last_row['Open']) / last_row['Open'] * 100
        }
    else:
        stock_data = {
            'price': 'Not found',
            'change': 'Not found',
            'change_percent': 'Not found'
        }

    return stock_data


def convert_to_numeric(value):
    try:
        return float(value)
    except ValueError:
        return float('nan')


def scrape_data_from_csv(file):
    results = []

    # Read CSV file content into a DataFrame
    df = pd.read_csv(file)

    # Iterate over each row in the DataFrame
    for _, row in df.iterrows():
        ticker = row['ticker']
        description = row['description']
        try:
            stock_data = scrape_stock_data(ticker)
            results.append({
                "description": description,
                "Ticker": ticker,
                "stock_price": stock_data['price'],
                "price_change": stock_data['change'],
                "price_change_percent": stock_data['change_percent'],
                "scrape_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        except Exception as e:
            results.append({
                "description": description,
                "Ticker": ticker,
                "stock_price": 'Error',
                "price_change": 'Error',
                "price_change_percent": 'Error',
                "scrape_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

    return results


def save_to_hdf5(data, filename='../scraped_data/data.h5'):
    with h5py.File(filename, 'a') as f:
        date_str = datetime.now().strftime('%Y-%m-%d')
        date_group = f.require_group(date_str)

        for item in data:
            scrape_time = item['scrape_time'].split(' ')[1]
            description = item['description']
            stock_group = date_group.require_group(description)

            if scrape_time not in stock_group:
                stock_subgroup = stock_group.create_group(scrape_time)

                stock_price = convert_to_numeric(item['stock_price'])
                price_change = convert_to_numeric(item['price_change'])
                price_change_percent = convert_to_numeric(item['price_change_percent'])

                stock_subgroup.create_dataset('stock_price', data=stock_price)
                stock_subgroup.create_dataset('price_change', data=price_change)
                stock_subgroup.create_dataset('price_change_percent', data=price_change_percent)

                stock_subgroup.attrs['Ticker'] = item['Ticker']
                stock_subgroup.attrs['scrape_time'] = scrape_time

                # Store metadata as JSON strings
                descriptions = {
                    'stock_price': 'Stock price in USD',
                    'price_change': 'Absolute change in stock price from the previous close. Positive values indicate an increase, negative values indicate a decrease.',
                    'price_change_percent': 'Percentage change in stock price from the previous close, numeric value without percentage sign or parentheses. E.g., -0.37'
                }
                stock_subgroup.attrs['description'] = json.dumps(descriptions)
                stock_subgroup.attrs[
                    'note'] = 'Percentage values are stored as float without percentage sign or parentheses.'

    print(f"Data successfully saved to {filename}")


if __name__ == "__main__":
    input_csv = os.path.join('..', 'Tickers', 'tickers.csv')
    scraped_data = scrape_data_from_csv(input_csv)
    save_to_hdf5(scraped_data)
