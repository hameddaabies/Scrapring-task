# Web Scraping & Data Processing Task

## Overview
This project includes two web scrapers targeting real e-commerce websites that sell smart toilets.
Each scraper extracts structured product data, cleans it, and stores it in JSON format.

### Scrapers:
- **ROCA Scraper:** Extracts detailed technical product specs from https://www.us.roca.com
- **WoodBridge Scraper:** Extracts pricing, availability, product images, and user reviews from https://www.woodbridgebath.com

## Project Structure
web-scraping-task/
├── ROCA/
│   ├── Roca_script.py               # Roca product scraper
│   └── output.json                  # Cleaned output data
├── WoodBridge/
│   ├── WB_script.py                 # Woodbridge product scraper
│   └── output.json                  # Cleaned output data
├── requirements.txt                 # Python dependencies
└── README.md                        # Project documentation

## Setup Instructions
1. Clone the repository:
   git clone https://github.com/yourusername/web-scraping-task.git
   cd web-scraping-task

2. Create and activate a virtual environment:
   python -m venv venv
   source venv/bin/activate      # On Windows: venv\Scripts\activate

3. Install dependencies:
   pip install -r requirements.txt

## Usage
Run Roca scraper:
cd ROCA
python Roca_script.py

Run WoodBridge scraper:
cd WoodBridge
python WB_script.py

## Output
Modify the output path in the code in saving the json data at the end of main function 
Each scraper will generate a structured `.json` file containing all extracted product data.

- roca_products.json – includes title, dimensions, color, reference code, specs, technical drawings, BIM files, and links.
- woodbridge_products.json – includes title, price, old price, discount, availability, images, features, description, documents, and reviews.

## Libraries Used
- beautifulsoup4
- selenium
- webdriver-manager
- requests
- lxml
- json (built-in)

## Author
- Hamed Daabies
- GitHub: https://github.com/yourusername
