import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import h5py

def scrape_stock_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    price_element = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
    change_element = soup.find('fin-streamer', {'data-field': 'regularMarketChange'})
    change_percent_element = soup.find('fin-streamer', {'data-field': 'regularMarketChangePercent'})

    stock_data = {
        'price': price_element.get_text() if price_element else 'Not found',
        'change': change_element.get_text() if change_element else 'Not found',
        'change_percent': change_percent_element.get_text() if change_percent_element else 'Not found'
    }

    return stock_data

def convert_to_numeric(value):
    try:
        if '%' in value:
            return float(value.strip('()%').replace(',', ''))
        else:
            return float(value.replace(',', ''))
    except ValueError:
        return float('nan')

def save_to_hdf5(data, filename='scraped_data/data.h5'):
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

                stock_subgroup.attrs['url'] = item['url']
                stock_subgroup.attrs['scrape_time'] = scrape_time

                # Store metadata as JSON strings
                descriptions = {
                    'stock_price': 'Stock price in USD',
                    'price_change': 'Absolute change in stock price from the previous close. Positive values indicate an increase, negative values indicate a decrease.',
                    'price_change_percent': 'Percentage change in stock price from the previous close, numeric value without percentage sign or parentheses. E.g., -0.37'
                }
                stock_subgroup.attrs['description'] = json.dumps(descriptions)
                stock_subgroup.attrs['note'] = 'Percentage values are stored as float without percentage sign or parentheses.'

    print(f"Data successfully saved to {filename}")

def scrape_data_from_csv(csv_file):
    results = []

    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            url = row['url']
            description = row['description']
            stock_data = scrape_stock_data(url)
            results.append({
                "description": description,
                "url": url,
                "stock_price": stock_data['price'],
                "price_change": stock_data['change'],
                "price_change_percent": stock_data['change_percent'],
                "scrape_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

    return results

if __name__ == "__main__":
    input_csv = 'URLs/URLs.csv'
    scraped_data = scrape_data_from_csv(input_csv)
    save_to_hdf5(scraped_data)
