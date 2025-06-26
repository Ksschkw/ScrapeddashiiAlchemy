import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from urllib.parse import urljoin

# List of user agents to mimic human browsing
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'MHI-SymptomChecker/1.0 (hello@mhi.ng)'  # Identify MHI for transparency
]

def get_random_user_agent():
    """Return a random user agent to mimic human behavior."""
    return random.choice(USER_AGENTS)

def get_condition_urls(base_url):
    """Crawl the A-to-Z index to get condition page URLs."""
    headers = {'User-Agent': get_random_user_agent()}
    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Adjust selector based on Ada’s A-to-Z index structure (e.g., links to condition pages)
        links = soup.select('a[href^="/conditions/"]')  # Target condition links
        urls = [urljoin(base_url, link['href']) for link in links if '/conditions/' in link['href'] and link['href'] != '/conditions/']
        return list(set(urls))  # Remove duplicates
    except Exception as e:
        print(f"Error fetching index: {e}")
        return []

def scrape_condition_page(url):
    """Scrape a single condition page for disease, symptoms, causes, treatments."""
    headers = {'User-Agent': get_random_user_agent()}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract disease name (adjust selector based on your screenshots)
        disease = soup.find('h1', class_='condition-title').text.strip() if soup.find('h1', class_='condition-title') else soup.title.text.split('|')[0].strip() if soup.title else 'Unknown'
        
        # Extract symptoms (adjust selector based on your screenshots)
        symptoms_section = soup.find('section', id='symptoms') or soup.find('div', class_='symptoms-list')
        symptoms = [li.text.strip() for li in symptoms_section.find_all('li')] if symptoms_section and symptoms_section.find('ul') else [span.text.strip() for span in symptoms_section.find_all('span', class_='symptom')] if symptoms_section else ['N/A']
        symptoms = ';'.join(symptoms)  # Join for CSV compatibility
        
        # Extract causes
        causes_section = soup.find('section', id='causes') or soup.find('div', class_='causes')
        causes = causes_section.text.strip() if causes_section else 'N/A'
        
        # Extract treatments
        treatments_section = soup.find('section', id='treatment') or soup.find('div', class_='treatment-options')
        treatments = treatments_section.text.strip() if treatments_section else 'N/A'
        
        return {
            'Disease': disease,
            'Symptoms': symptoms,
            'Causes': causes,
            'Treatment': treatments
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def main():
    """Main function to scrape Ada conditions and save to CSV."""
    base_url = 'https://ada.com/conditions'
    print(f"Starting scrape at {time.ctime()} WAT")
    condition_urls = get_condition_urls(base_url)
    print(f"Found {len(condition_urls)} condition URLs")
    data = []
    
    for i, url in enumerate(condition_urls):
        print(f"Scraping {url} ({i+1}/{len(condition_urls)})")
        result = scrape_condition_page(url)
        if result:
            data.append(result)
        time.sleep(random.uniform(1, 3))  # Polite delay to avoid overloading
    
    # Save to CSV
    df = pd.DataFrame(data)
    df.to_csv('ada_conditions.csv', index=False, encoding='utf-8')
    print(f"Data saved to ada_conditions.csv at {time.ctime()} WAT")
    print(f"Total conditions scraped: {len(df)}")

if __name__ == "__main__":
    main()