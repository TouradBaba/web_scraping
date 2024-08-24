import streamlit as st
import pandas as pd
from scraper import scrape_stock_data, scrape_data_from_csv

# Streamlit app
st.title('Yahoo Finance Stock Data Scraper')

# Section for manual URL entry
st.subheader('Manual URL Entry')

# Input for URL
manual_url = st.text_input("Enter Yahoo Finance stock URL")

if st.button('Scrape Data from URL'):
    if manual_url:
        try:
            # Scrape data from the provided URL
            stock_data = scrape_stock_data(manual_url)

            # Check if the data was successfully scraped
            if stock_data['price'] != 'Not found':
                # Display data in a more formatted way
                st.write("### Data for the specified company:")
                st.write(f"**URL:** {manual_url}")
                st.write(f"**Stock Price:** {stock_data['price']}")
                st.write(f"**Price Change:** {stock_data['change']}")
                st.write(f"**Price Change Percent:** {stock_data['change_percent']}")
            else:
                st.error("No data found for the provided URL. Please check the link or make sure it is a valid Yahoo Finance URL.")
        except Exception as e:
            st.error(f"An error occurred while trying to scrape data. Check the URL.")
    else:
        st.warning("Please enter a URL before clicking the button.")

# Section for CSV file upload
st.subheader('Upload CSV file')

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
    st.dataframe(df)  # Using st.dataframe for better display options
