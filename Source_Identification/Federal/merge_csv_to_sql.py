import sqlite3
import pandas as pd

# File paths
usa_gov_agencies_csv = "/Users/dinghali/Desktop/25 Spring/Runwei/USA_Gov_Agencies.csv"
api_rss_results_csv = "/Users/dinghali/Desktop/25 Spring/Runwei/api_rss_results.csv"
output_csv = "/Users/dinghali/Desktop/25 Spring/Runwei/USA_Gov_Agencies_API_RSS.csv"

# Load CSV files into DataFrames
df_agencies = pd.read_csv(usa_gov_agencies_csv)
df_api_rss = pd.read_csv(api_rss_results_csv)

# Rename columns to match SQL table
df_agencies.columns = ['Agency_Name', 'Website']
df_api_rss.columns = ['Website', 'API_Info', 'RSS_Feeds']

# Remove duplicate entries based on the 'Website' column
df_agencies = df_agencies.drop_duplicates(subset=['Website'])

# Create a SQLite database in memory
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Create the table to store the merged data
cursor.execute('''
CREATE TABLE USA_Gov_Agencies_API_RSS (
    Agency_Name TEXT,
    Website TEXT PRIMARY KEY,
    API_Info TEXT,
    RSS_Feeds TEXT
)
''')

# Insert data from USA_Gov_Agencies.csv
df_agencies.to_sql('USA_Gov_Agencies_API_RSS', conn, if_exists='append', index=False)

# Update the table with data from api_rss_results.csv
for index, row in df_api_rss.iterrows():
    cursor.execute('''
    UPDATE USA_Gov_Agencies_API_RSS
    SET API_Info = ?, RSS_Feeds = ?
    WHERE Website = ?
    ''', (row['API_Info'], row['RSS_Feeds'], row['Website']))

# Select the merged data
merged_df = pd.read_sql_query('SELECT * FROM USA_Gov_Agencies_API_RSS', conn)

# Save the merged data to a new CSV file
merged_df.to_csv(output_csv, index=False)

# Close the connection
conn.close()

print(f"✅ Merged data saved in '{output_csv}'.")