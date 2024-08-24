import streamlit as st
import pandas as pd
from scraper import scrape_data_from_csv

# Streamlit app
st.title('Yahoo Finance Stock Data Scraper')

# File uploader
csv_file = st.file_uploader("Upload CSV file", type=["csv"])

if csv_file is not None:
    # Save the uploaded file
    csv_path = 'temp.csv'
    with open(csv_path, 'wb') as f:
        f.write(csv_file.getvalue())

    # Process the file
    st.write("Scraping data from the uploaded CSV...")
    scraped_data = scrape_data_from_csv(csv_path)

    # Display scraped data
    df = pd.DataFrame(scraped_data)
    st.write("Scraped Data:")
    st.write(df)


