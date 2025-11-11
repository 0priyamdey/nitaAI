import requests
from bs4 import BeautifulSoup 
import os
import re

# --- Configuration (YOU MUST CHANGE THIS) ---
URLS_TO_SCRAPE = [
    "https.nita.ac.in/about/vision-mission",
    "https.nita.ac.in/academics/departments",
    #... add all other pages [4]
]
TARGET_SELECTORS = [
    "div#main-content",          # Example: <div id="main-content">...</div>
    "div.content",             # Example: <div class="content">...</div>
    #... find your real selectors by Inspecting the page [6]
]
# --- End Configuration ---

# --- CORRECTED PATH ---
OUTPUT_DIR = "backend/data/web_text"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Starting web scrape for {len(URLS_TO_SCRAPE)} URLs...")

for url in URLS_TO_SCRAPE:
    try:
        page = requests.get(url, timeout=10)
        page.raise_for_status()
        
        soup = BeautifulSoup(page.content, "html.parser")
        
        content_found = False
        full_text = ""
        
        for selector in TARGET_SELECTORS:
            containers = soup.select(selector) [6]
            
            if containers:
                for container in containers:
                    full_text += container.get_text(separator=" ", strip=True) [6]
                
                if full_text.strip():
                    content_found = True
                    break
        
        if content_found:
            filename = url.replace('https://', '').replace('http://', '').replace('/', '_').replace('.', '_')
            filename = re.sub(r'[^a-zA-Z0-9_]', '', filename)
            filename = f"{filename}.txt"
            
            output_path = os.path.join(OUTPUT_DIR, filename)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"Source URL: {url}\n\n")
                f.write(full_text)
                
            print(f"  Scraped and saved: {url}")
        else:
            print(f"  Warning: No target content selectors found for {url}")
            
    except requests.RequestException as e:
        print(f"  Error fetching {url}: {e}")

print("Web scraping complete.")