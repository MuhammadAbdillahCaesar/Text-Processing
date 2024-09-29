import os
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re

# Step 1: Define a list of URLs to scrape
urls = [
    'https://en.wikipedia.org/wiki/List_of_wars:_before_1000',
    'https://en.wikipedia.org/wiki/List_of_wars:_1000%E2%80%931499',
    'https://en.wikipedia.org/wiki/List_of_wars:_1500%E2%80%931799',
    'https://en.wikipedia.org/wiki/List_of_wars:_1800%E2%80%931899',
    'https://en.wikipedia.org/wiki/List_of_wars:_1900%E2%80%931944',
    'https://en.wikipedia.org/wiki/List_of_wars:_1945%E2%80%931989',
    'https://en.wikipedia.org/wiki/List_of_wars:_1990%E2%80%932002',
    'https://en.wikipedia.org/wiki/List_of_wars:_2003%E2%80%93present',   
    # Example next page URL
    # Add more URLs as needed for different pages
]

# Define headers that match the expected structure
expected_headers = ["Start", "Finish", "Name of Conflict", "Victorious", "Defeated"]

# Function to extract rows from a given table
def extract_table_rows(table):
    rows = []
    for row in table.find_all('tr')[1:]:  # Skip the header row(s)
        cells = row.find_all(['td', 'th'])
        row_data = [cell.get_text(strip=True) for cell in cells]
        # Only include rows that match the expected column count
        if len(row_data) == len(expected_headers):
            rows.append(row_data)
    return rows

# Output directory for saving the files
output_directory = r'C:\Users\MAbdi\OneDrive\Dokumen\sc_output'
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Step 2: Loop over each URL and scrape data
for url_index, url in enumerate(urls):
    try:
        # Get the page content
        page = requests.get(url)
        
        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(page.text, 'html.parser')
        
        # Find all tables on the page
        tables = soup.find_all('table')
        
        # Step 3: Iterate over all tables and process each
        for index, table in enumerate(tables):
            # Extract rows from the current table
            rows = extract_table_rows(table)

            # If rows are found, create a DataFrame
            if rows:
                df = pd.DataFrame(rows, columns=expected_headers)

                # Clean up the DataFrame if needed (e.g., refine the start and finish columns)
                def refine_row_content(row):
                    combined_value = row["Start"]
                    match = re.match(r'c\.\s*(\d+)\s*BC\s*-\s*(\d+)\s*BC', combined_value)
                    if match:
                        row["Start"] = f"c. {match.group(1)} BC"
                        row["Finish"] = f"c. {match.group(2)} BC"
                    return row

                df_refined = df.apply(refine_row_content, axis=1)

                # Define file paths for CSV and Excel, include page number in filename
                excel_output_path = os.path.join(output_directory, f'wikipedia_table_page_{url_index + 1}_table_{index + 1}.xlsx')

                # Save DataFrame to CSV and Excel
                df_refined.to_excel(excel_output_path, index=False)

                # Output paths for verification
                print(f"Saved:{excel_output_path}")
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")

