import requests
from bs4 import BeautifulSoup
import pandas as pd

# List of sections to iterate through
sections = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# Initialize an empty list to store agency data
agencies = []

for section in sections:
    # Step 1: Fetch the USA.gov Agency Index page for each section
    if section == 'A':
        url = f'https://www.usa.gov/agency-index#{section}'
    else:
        url = f'https://www.usa.gov/agency-index/{section.lower()}#{section}'
    
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Step 2: Extract agency names and links
        for item in soup.select('.usa-accordion__heading'):
            # Extract agency name
            name = item.select_one('.usa-accordion__button').text.strip()
            name = ' '.join(name.split())  # Remove extra spaces
            
            # Find the next sibling with class 'usa-accordion__content'
            content = item.find_next_sibling(class_='usa-accordion__content')
            link = 'No link found'
            
            if content:
                # Find the first link after "Website:"
                website_heading = content.find('p', class_='field--name-field-website')
                
                if website_heading:
                    # Extract the link after "Website:"
                    link_element = website_heading.find('a', href=True)
                    if link_element:
                        link = link_element['href']
                    else:
                        print(f"No link found for agency: {name}")
                else:
                    print(f"No 'Website:' heading found for agency: {name}")
            else:
                print(f"No content found for agency: {name}")
            
            # Append to the list
            agencies.append({'Agency Name': name, 'Website': link})
            print(f"Agency: {name}, Website: {link}")  # Debugging statement

# Step 3: Save to CSV
if agencies:
    df = pd.DataFrame(agencies)
    df.to_csv('USA_Gov_Agencies.csv', index=False)
    print("CSV file created successfully!")
else:
    print("No agencies found. Check the selector or webpage structure.")