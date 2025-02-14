import pandas as pd
import re

# File paths
input_csv = "/Users/dinghali/Desktop/25 Spring/Runwei/USA_Gov_Agencies_API_RSS.csv"
output_csv = "/Users/dinghali/Desktop/25 Spring/Runwei/USA_Gov_Agencies_API_RSS_Cleaned.csv"

# Load the CSV file into a DataFrame
try:
    df = pd.read_csv(input_csv)
except FileNotFoundError:
    print(f"File not found: {input_csv}")
    exit(1)

# Function to clean the columns
def clean_column(column_data):
    if pd.isna(column_data):
        return ""
    # Find all URLs starting with https://www.
    urls = re.findall(r'https://www\.[^\s,]+', column_data)
    # Join URLs with ", " separator
    return ", ".join(urls)

# Apply the function to the API_Info and RSS_Feeds columns
df['API_Info'] = df['API_Info'].apply(clean_column)
df['RSS_Feeds'] = df['RSS_Feeds'].apply(clean_column)

# Save the cleaned DataFrame to a new CSV file
df.to_csv(output_csv, index=False)

print(f"✅ Cleaned data saved in '{output_csv}'.")