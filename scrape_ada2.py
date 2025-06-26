import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import random
import re
from urllib.parse import urljoin


BASE_URL = "https://ada.com/conditions"
OUTPUT_JSON = "conditions.json"
# OUTPUT_CSV = "conditions.csv"

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'MHI-SymptomChecker/1.0 (hello@mhi.ng)'  
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def get_condition_urls(base_url=BASE_URL):
    headers = {'User-Agent': get_random_user_agent()}
    try:
        resp = requests.get(base_url, headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Could not fetch index page {base_url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    # Select all links that look like /conditions/<slug>
    links = soup.select('a[href^="/conditions/"]')
    urls = set()
    for a in links:
        href = a.get('href')
        # Skip the index itself
        if not href:
            continue
        # Avoid plain "/conditions/" link
        if href.rstrip('/') == "/conditions":
            continue
        # Build full URL
        full = urljoin(base_url, href)
        urls.add(full)
    urls_list = sorted(urls)
    print(f"[INFO] Found {len(urls_list)} unique condition URLs.")
    return urls_list

def normalize_header_to_key(header_text: str) -> str:
    text = header_text.strip().lower()
    m = re.match(r'^(.*?)(?:\s+of\b.*)?$', text)
    if m:
        core = m.group(1)
    else:
        core = text
    # Replace non-alphanumeric with underscore
    key = re.sub(r'[^0-9a-z]+', '_', core)
    key = key.strip('_')
    if not key:
        # Fallback: use full header lowercased, underscores
        key = re.sub(r'[^0-9a-z]+', '_', text).strip('_')
    return key

def scrape_condition_page(url: str) -> dict:
    headers = {'User-Agent': get_random_user_agent()}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"[WARN] Failed to fetch {url}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract condition name
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        cond_name = h1.get_text(strip=True)
    else:
        # Fallback: from <title>
        if soup.title and soup.title.string:
            cond_name = soup.title.string.split('|')[0].strip()
        else:
            cond_name = url.rstrip('/').split('/')[-1].replace('-', ' ').title()

    result = {
        "condition": cond_name,
        "url": url
    }

    # Iterate all <h2> tags
    h2_tags = soup.find_all("h2")
    if not h2_tags:
        return result

    for h2 in h2_tags:
        header_text = h2.get_text(separator=" ").strip()
        if not header_text:
            continue
        key = normalize_header_to_key(header_text)
        # Avoid duplicate keys within same page: if key exists, append index
        if key in result:
            # find a unique suffix
            i = 2
            new_key = f"{key}_{i}"
            while new_key in result:
                i += 1
                new_key = f"{key}_{i}"
            key = new_key

        # Collect following siblings until next <h2>
        contents = []
        for sib in h2.find_next_siblings():
            if sib.name == "h2":
                break
            # We only gather <div class="Text_wrapper__rP9t7"> blocks
            if sib.name == "div":
                classes = sib.get("class", [])
                # class may be a list like ["Text_wrapper__rP9t7", ...]
                if any("Text_wrapper__rP9t7" == cls for cls in classes):
                    txt = sib.get_text(separator=" ", strip=True)
                    if txt:
                        contents.append(txt)
        if contents:
            # Join paragraphs with blank line between
            result[key] = "\n\n".join(contents)

    return result

def main():
    print(f"[START] Scraping Ada conditions: {time.ctime()}")
    # Step 1: get all URLs
    condition_urls = get_condition_urls(BASE_URL)
    if not condition_urls:
        print("[ERROR] No condition URLs found; exiting.")
        return

    all_data = []
    for idx, url in enumerate(condition_urls, start=1):
        print(f"[{idx}/{len(condition_urls)}] Scraping: {url}")
        data = scrape_condition_page(url)
        if data:
            all_data.append(data)
        # Polite delay
        time.sleep(random.uniform(1.0, 3.0))

    if not all_data:
        print("[ERROR] No data scraped; exiting.")
        return

    # Step 2: Save JSON
    try:
        with open(OUTPUT_JSON, "w", encoding="utf-8") as jf:
            json.dump(all_data, jf, ensure_ascii=False, indent=2)
        print(f"[OK] JSON saved to {OUTPUT_JSON} (total conditions: {len(all_data)})")
    except Exception as e:
        print(f"[ERROR] Could not write JSON: {e}")

    # # Step 3: Save CSV
    # try:
    #     df = pd.DataFrame(all_data)
    #     # Fill NaN with empty
    #     df = df.fillna("")
    #     # Reorder columns: put "condition","url" first if present
    #     cols = list(df.columns)
    #     cols_sorted = []
    #     if "condition" in cols:
    #         cols_sorted.append("condition")
    #     if "url" in cols and "url" not in cols_sorted:
    #         cols_sorted.append("url")
    #     # Remaining columns in alphabetical order
    #     others = [c for c in cols if c not in cols_sorted]
    #     others.sort()
    #     cols_sorted.extend(others)
    #     df = df[cols_sorted]
    #     df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    #     print(f"[OK] CSV saved to {OUTPUT_CSV}")
    # except Exception as e:
    #     print(f"[ERROR] Could not write CSV: {e}")

    print(f"[DONE] Completed at {time.ctime()}")

if __name__ == "__main__":
    main()
