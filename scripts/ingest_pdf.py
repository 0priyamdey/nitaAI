import requests
from bs4 import BeautifulSoup
import os

# --- Configuration ---
# Manually inspect the college website and find the CSS selectors 
# for the main content containers.
TARGET_SELECTORS =[]

# List of URLs to scrape
URLS_TO_SCRAPE =[]

OUTPUT_DIR = "data/web_text"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Scraping Logic ---
for url in URLS_TO_SCRAPE:
    try:
        page = requests.get(url, timeout=10)
        page.raise_for_status()
        
        soup = BeautifulSoup(page.content, "html.parser")
        
        content_found = False
        for selector in TARGET_SELECTORS:
            container = soup.select_one(selector)
            
            if container:
                # Found a matching container, extract its text
                #.get_text() extracts text; strip=True cleans whitespace 
                text = container.get_text(separator=" ", strip=True)
                
                # Create a simple filename
                filename = url.split('/')[-1] or url.split('/')[-2]
                filename = f"{filename}.txt"
                
                output_path = os.path.join(OUTPUT_DIR, filename)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(f"Source URL: {url}\n\n")
                    f.write(text)
                    
                print(f"Successfully scraped and saved: {url}")
                content_found = True
                break # Stop searching for selectors once content is found
        
        if not content_found:
            print(f"Warning: No target content found for {url}")
            
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")