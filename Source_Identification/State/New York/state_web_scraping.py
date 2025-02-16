import requests
from bs4 import BeautifulSoup
import csv

def scrape_ny_agencies():
    base_url = "https://www.ny.gov/agencies?page="
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    agencies_data = []

    for page in range(10):  # Loop through pages 0 to 9
        url = f"{base_url}{page}#views-exposed-form-filter-frame-agencies"
        print(f"Scraping page {page}: {url}")

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Ensure we got a valid response
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch the page: {e}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")

        # Find all agency blocks
        agency_blocks = soup.find_all('div', class_='views-row')

        if not agency_blocks:
            print(f"No agencies found on page {page}.")
            continue

        print(f"Found {len(agency_blocks)} agencies on page {page}.")

        for block in agency_blocks:
            # Extract category
            category_tag = block.find('div', class_='content-category')
            category = " ".join(category_tag.get_text(strip=True).split()) if category_tag else "N/A"

            # Extract agency name
            name_tag = block.find('div', class_='field--name-name')
            name = name_tag.get_text(strip=True) if name_tag else "N/A"

            # Extract description
            desc_tag = block.find('div', class_='field--name-description')
            description = desc_tag.get_text(strip=True) if desc_tag else "N/A"

            # Extract website URL
            website_tag = block.find('a', class_='text-primary-links')
            website = website_tag['href'] if website_tag else "N/A"
            if website and not website.startswith('http'):
                website = f"https://www.ny.gov{website}"

            agencies_data.append({
                "Category": category,
                "Agency": name,
                "Website": website,
                "Description": description
            })

    # Save data to a CSV file
    csv_filename = "ny_agencies.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["Category", "Agency", "Website", "Description"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(agencies_data)

    print(f"Successfully saved {len(agencies_data)} agencies to {csv_filename}")

if __name__ == "__main__":
    scrape_ny_agencies()