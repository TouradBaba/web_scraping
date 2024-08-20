import h5py

def read_from_hdf5(filename='data.h5'):
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
                    print(f"      Price Change Percent: {stock_subgroup['price_change_percent'][()].decode('utf-8')}")
                    print(f"      URL: {stock_subgroup.attrs['url']}")
                    print(f"      Scrape Time (Metadata): {stock_subgroup.attrs['scrape_time']}")

if __name__ == "__main__":
    read_from_hdf5()
