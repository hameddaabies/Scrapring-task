# Web Scraping & Data Processing Task

## 📌 Overview
This project includes two Python-based web scrapers targeting real e-commerce websites that sell smart toilets. Each scraper extracts structured product data, cleans it, and stores it in JSON format.

## 🧠 Scrapers
- ROCA Scraper: Extracts detailed technical product specifications from https://www.us.roca.com  
- WoodBridge Scraper: Extracts pricing, availability, images, and customer reviews from https://www.woodbridgebath.com

## 📁 Project Structure

```text
web-scraping-task/
├── ROCA/
│   ├── Roca_script.py           # Scraper for Roca website
│   └── output.json              # Cleaned Roca product data
│
├── WoodBridge/
│   ├── WB_script.py             # Scraper for WoodBridge website
│   └── output.json              # Cleaned WoodBridge product data
│
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation


## ⚙️ Setup Instructions

1. Clone the repository:
git clone https://github.com/hameddaabies/Scrapring-task.git  
cd Scrapring-task

2. Create & activate a virtual environment:
python -m venv venv  
venv\Scripts\activate  (Windows)  
source venv/bin/activate (Mac/Linux)

3. Install required dependencies:
pip install -r requirements.txt

## ▶️ Usage

Run ROCA scraper:
cd ROCA  
python Roca_script.py

Run WoodBridge scraper:
cd WoodBridge  
python WB_script.py

The output .json file will be saved in the same folder as the script. You can modify the output path inside the script if needed.

## 📦 Output Files
ROCA/output.json: Includes product title, collection, dimensions, color, reference code, specs, technical drawings, and 3D/BIM resources.  
WoodBridge/output.json: Includes product title, price, old price, discount info, availability, product images, features, descriptions, documents, and customer reviews.

## 🛠️ Libraries Used
beautifulsoup4  
selenium  
webdriver-manager  
requests  
lxml  
json (built-in)

## 👤 Author
Hamed Daabies  
GitHub: https://github.com/hameddaabies
