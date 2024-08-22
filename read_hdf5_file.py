import h5py
import json

def read_from_hdf5(filename='scraped_data/data.h5'):
    with h5py.File(filename, 'r') as f:
        for date_str in f.keys():
            print(f"Date: {date_str}")
            date_group = f[date_str]
            for description in date_group.keys():
                print(f"  Stock Description: {description}")
                stock_group = date_group[description]
                for scrape_time in stock_group.keys():
                    stock_subgroup = stock_group[scrape_time]
                    print(f"    Scrape Time: {scrape_time}")
                    print(f"      Stock Price: {stock_subgroup['stock_price'][()]}")
                    print(f"      Price Change: {stock_subgroup['price_change'][()]}")
                    print(f"      Price Change Percent: {stock_subgroup['price_change_percent'][()]}")
                    print(f"      URL: {stock_subgroup.attrs['url']}")

                    # Read and print metadata descriptions
                    descriptions_json = stock_subgroup.attrs.get('description', '{}')
                    descriptions = json.loads(descriptions_json)
                    print("      Metadata Descriptions:")
                    for key, desc in descriptions.items():
                        print(f"        {key}: {desc}")

                    # Print general notes
                    note = stock_subgroup.attrs.get('note', 'No notes available.')
                    print(f"      Notes: {note}")

if __name__ == "__main__":
    read_from_hdf5()
