import requests
from bs4 import BeautifulSoup
import csv
import json

# URL of the website to scrape
url = 'https://www.ca.gov/departments/all/'

# Send a GET request to the website
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the section containing the departments
    departments_section = soup.find('cagovhome-filterlist')
    
    # Find all department entries
    departments = departments_section.find_all('div', {'role': 'listitem'})
    
    # Open a CSV file to write the data
    with open('california_departments.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(['Category', 'Agency', 'Website', 'Description'])
        
        # Iterate over each department entry
        for department in departments:
            category = department.find('p', class_='font-size-14 m-t-md')
            agency = department.find('h3', class_='lead bold m-t-0 m-b')
            website = department.find('a')
            description = department.find('p', class_='department-description')
            
            # Extract text if the element is found, else set to empty string
            category_text = category.text.strip().replace('Topics: ', '').replace('"', '') if category else ''
            agency_text = agency.text.strip() if agency else ''
            website_text = f"https://www.ca.gov{website['href'].strip()}" if website else ''
            description_text = description.text.strip().replace('Topics: ', '').replace('"', '') if description else ''
            
            # Follow the link to get the actual website URL
            if website_text:
                sub_response = requests.get(website_text)
                if sub_response.status_code == 200:
                    sub_soup = BeautifulSoup(sub_response.content, 'html.parser')
                    script_tag = sub_soup.find('script', type='application/ld+json')
                    if script_tag:
                        structured_data = json.loads(script_tag.string)
                        actual_website = structured_data.get('url', '')
                        website_text = actual_website
            
            # Write the department data to the CSV file
            writer.writerow([category_text, agency_text, website_text, description_text])
else:
    print('Failed to retrieve the web page')