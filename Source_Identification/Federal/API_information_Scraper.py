import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Load the CSV file with government websites
file_path = "/Users/dinghali/Desktop/25 Spring/Runwei/USA_Gov_Agencies.csv"
try:
    df = pd.read_csv(file_path)
    websites = df["Website"].dropna().tolist()
except FileNotFoundError:
    print(f"CSV file not found at {file_path}")
    websites = []

# Expanded keywords for API and RSS detection
api_keywords = ["API key", "API documentation", "developer portal", "developers", 
                "api/docs", "rest api", "web services", "authentication", "access token"]
rss_keywords = ["rss", "feed", "xml"]

results = []

# Set up Selenium WebDriver for bypassing 403 errors
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--log-level=3")  # Suppress logs

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def scrape_website(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
    }
    found_keywords = []
    rss_links = []

    try:
        # First, try using requests
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 403:
            print(f"[!] 403 Forbidden on {url}, switching to Selenium...")
            driver.get(url)
            time.sleep(5)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
        else:
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

        page_text = soup.get_text().lower()
        
        # Check for API-related keywords in page text
        found_keywords.extend([kw for kw in api_keywords if kw.lower() in page_text])
        
        # Extract links for API and RSS
        for link in soup.find_all("a", href=True):
            link_href = link["href"].lower()
            if any(k in link_href for k in ["api", "developer", "docs"]):
                found_keywords.append(f"Link to {link['href']}")
            if any(rss_kw in link_href for rss_kw in rss_keywords):
                rss_links.append(link["href"])
        
        # Check common API subpages
        common_subpaths = ["/developers", "/api", "/documentation"]
        for sub in common_subpaths:
            sub_url = f"{url.rstrip('/')}{sub}"
            try:
                sub_resp = requests.get(sub_url, headers=headers, timeout=10)
                if sub_resp.status_code == 200:
                    found_keywords.append(f"Subpage found: {sub_url}")
            except requests.exceptions.RequestException:
                continue
        
        # Remove duplicates
        found_keywords = list(set(found_keywords))
        rss_links = list(set(rss_links))

        if found_keywords or rss_links:
            results.append({
                "Website": url,
                "Found API Info": ", ".join(found_keywords),
                "RSS Feeds": ", ".join(rss_links)
            })
            print(f"[+] Found API or RSS info on: {url}")
        else:
            print(f"[-] No API or RSS info on: {url}")

    except Exception as e:
        print(f"Error on {url}: {str(e)}")

# Scrape all websites with progress tracking
for site in tqdm(websites, desc="Scraping Websites"):
    scrape_website(site)
    time.sleep(2)

# Close Selenium WebDriver
driver.quit()

# Save results
output_file = "/Users/dinghali/Desktop/25 Spring/Runwei/api_rss_results.csv"
if results:
    pd.DataFrame(results).to_csv(output_file, index=False)
    print(f"✅ Results saved in '{output_file}'.")
else:
    print("❌ No results found.")