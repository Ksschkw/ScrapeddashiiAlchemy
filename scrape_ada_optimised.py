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
    'MHI-SymptomChecker/1.0 (hello@mhi.ng)'
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
        links = soup.select('a[href^="/conditions/"]')
        urls = [urljoin(base_url, link['href']) for link in links if '/conditions/' in link['href'] and link['href'] != '/conditions/']
        return list(set(urls))
    except Exception as e:
        print(f"Error fetching index: {e}")
        return []

def scrape_condition_page(url):
    """Scrape a single condition page with detailed debugging."""
    headers = {'User-Agent': get_random_user_agent()}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract disease name
        disease = soup.find('h1', class_=['condition-title', 'page-title', 'main-heading', 'title']).text.strip() if soup.find('h1', class_=['condition-title', 'page-title', 'main-heading', 'title']) else soup.title.text.split('|')[0].strip() if soup.title else 'Unknown'
        print(f"Found disease: {disease} at {url}")
        
        # Debug all sections and potential content blocks
        all_sections = soup.find_all(['section', 'article', 'div'])
        print(f"Total sections/divs found: {len(all_sections)}")
        for section in all_sections[:5]:  # Limit to first 5 for brevity
            print(f"Section tag: {section.name}, class: {section.get('class', ['No class'])[0]}, text snippet: {section.text.strip()[:50]}...")
        
        # Extract symptoms
        symptoms_candidates = soup.find_all(['section', 'article', 'div'], class_=['symptoms', 'symptom-list', 'condition-symptoms', 'symptom-section', 'content-block'])
        symptoms = []
        for candidate in symptoms_candidates:
            symptom_items = candidate.find_all(['li', 'p', 'span', 'div'], class_=['symptom', 'symptom-item', 'text'])
            if symptom_items:
                symptoms.extend(item.text.strip() for item in symptom_items if item.text.strip())
        symptoms = ';'.join(symptoms) if symptoms else 'N/A'
        print(f"Symptoms candidates found: {len(symptoms_candidates)}")
        
        # Extract causes
        causes_candidates = soup.find_all(['section', 'article', 'div'], class_=['causes', 'condition-causes', 'cause-section', 'content-block'])
        causes = next((candidate.text.strip() for candidate in causes_candidates if candidate.text.strip()), 'N/A') if causes_candidates else 'N/A'
        print(f"Causes candidates found: {len(causes_candidates)}")
        
        # Extract treatments
        treatments_candidates = soup.find_all(['section', 'article', 'div'], class_=['treatments', 'treatment-options', 'condition-treatment', 'content-block'])
        treatments = next((candidate.text.strip() for candidate in treatments_candidates if candidate.text.strip()), 'N/A') if treatments_candidates else 'N/A'
        print(f"Treatments candidates found: {len(treatments_candidates)}")
        
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
        time.sleep(random.uniform(0.5, 1.5))  # Efficient delay
    
    # Save to CSV
    df = pd.DataFrame(data)
    df.to_csv('ada_conditions_enhanced_debug.csv', index=False, encoding='utf-8')
    print(f"Data saved to ada_conditions_enhanced_debug.csv at {time.ctime()} WAT")
    print(f"Total conditions scraped: {len(df)}")

if __name__ == "__main__":
    main()