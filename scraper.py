import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import h5py

# Function to scrape stock data from Yahoo Finance
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

def save_to_hdf5(data, filename='data.h5'):
    with h5py.File(filename, 'a') as f:
        date_str = datetime.now().strftime('%Y-%m-%d')
        date_group = f.require_group(date_str)

        for item in data:
            scrape_time = item['scrape_time'].replace(':', '-')
            description = item['description']
            stock_group = date_group.require_group(description)

            if scrape_time not in stock_group:
                stock_subgroup = stock_group.create_group(scrape_time)

                stock_price = float(item['stock_price'].replace(',', ''))
                price_change = float(item['price_change'].replace(',', '').replace('+', ''))
                price_change_percent = item['price_change_percent']

                # Save stock price and changes as floats
                stock_subgroup.create_dataset('stock_price', data=stock_price)
                stock_subgroup.create_dataset('price_change', data=price_change)

                # Save price_change_percent as a string
                stock_subgroup.create_dataset(
                    'price_change_percent',
                    data=price_change_percent
                )

                # Store metadata
                stock_subgroup.attrs['url'] = item['url']
                stock_subgroup.attrs['scrape_time'] = item['scrape_time']

    print(f"Data successfully saved to {filename}")

# Function to scrape data from each URL in the CSV file
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
    input_csv = 'URLs.csv'
    scraped_data = scrape_data_from_csv(input_csv)
    save_to_hdf5(scraped_data)
