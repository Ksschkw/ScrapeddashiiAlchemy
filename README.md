
# ScrapeddashiiAlchemy 🔮

**Turning raw HTML into structured health data — with a little DevTools wizardry.**

This repo scrapes all condition pages from [ada.com/conditions](https://ada.com/conditions), extracting every `<h2>`-based feature and its corresponding content blocks beneath it. The results are saved in both JSON and CSV formats, ready for analysis, modeling, or medical NLP tasks.

---

## 🧠 Origin Story

While exploring [ada.com](https://ada.com), I wanted structured data on medical conditions. Here's how the alchemy happened:

1. **Fired up Chrome DevTools** 🔍  
   Inspected the layout of a few condition pages. I noticed a **consistent pattern**:
   - Feature sections (e.g., *Symptoms*, *Causes*, *Types of X*) were always inside `<h2>` tags.
   - The content under each was wrapped in `<div class="Text_wrapper__rP9t7">` blocks.

2. **Discovered the HTML rhythm** 🎼  
   Under each `<h2>`, the relevant text was grouped into these styled `div` elements — up until the next `<h2>`.

3. **Built the parser** 🧰  
   Scraped each condition page, looping over all `<h2>` headers and capturing all following `Text_wrapper__rP9t7` content.

4. **Exported it all** ✍️  
   Saved the scraped content into a cleanly structured `conditions.json` and `conditions.csv`.

---

## 🚀 Features

- **DevTools-Inspired DOM Mapping**  
  Designed based on real-world inspection of Ada’s frontend structure.

- **Flexible `<h2>` Extraction**  
  Auto-detects any feature section — no hardcoded "Symptoms", "Causes", etc.

- **Content-Aware Scraping**  
  Pulls all relevant paragraphs under each section until the next begins.

- **Dual Output Formats**  
  - **JSON**: nested, flexible, clean
  - **CSV**: flat, tabular, analysis-ready

- **Stealth Mode**  
  Random User-Agent headers and respectful delays to avoid detection.

---

## 🛠️ Installation

1. **Clone this repo**

   ```bash
   git clone https://github.com/YourUserName/ScrapeddashiiAlchemy.git
   cd ScrapeddashiiAlchemy
    ````

2. **Create a virtualenv (optional but smart)**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the ingredients**

   ```bash
   pip install -r requirements.txt
   ```

   > Requirements: `requests`, `beautifulsoup4`, `pandas`

---

## 🎯 Usage

Run the script with:

```bash
python scrape_ada_extended.py
```

This will generate:

* `conditions.json`: Each condition with all its feature sections and text blocks.
* `conditions.csv`: Tabular form, one row per condition. Dynamically expanding columns as more features are detected.

---

## 🧬 Sample Output

```json
{
  "condition": "Sepsis",
  "url": "https://ada.com/conditions/sepsis/",
  "overview": "Sepsis is a potentially life-threatening condition...",
  "symptoms": "High fever, confusion, rapid heart rate...",
  "treatment": "Hospitalization, IV fluids, antibiotics..."
}
```

---

## ⚙️ Configuration

* **Delays & Headers**
  Tweak `time.sleep()` and `USER_AGENTS` list in `scrape_ada_extended.py`.

* **Feature Key Normalization**
  Custom rules inside `normalize_header_to_key()` (e.g., `"Symptoms of X"` → `"symptoms"`).

* **Slug-based URLs?**
  You can optionally use your own list of slugs instead of crawling the entire `/conditions` index.

---

## 🧪 Ideas for Next Experiments

* 🧠 Symptom clustering via NLP
* 📊 Auto-profiling datasets with `pandas-profiling`
* 🌍 Translate scraped text using DeepL API
* 🔎 Semantic search with embedding vectors (OpenAI, HuggingFace)

---

## 🤝 Contributing

Found a weird condition page? Wanna help extend the scraper for images or diagrams?
Fork it, improve it, and send a PR 💫

---

> “Alchemy isn't magic. It's structured parsing wrapped in mystery.”
> — ScrapeddashiiAlchemy

