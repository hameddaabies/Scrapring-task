"""
Roca.py
Scrapes product data for two-piece toilets from the Roca USA website (https://www.us.roca.com).
Extracted Fields:
-----------------
- Product Title
- Collection Name
- Product Reference (ref code)
- Dimensions (L/W/H in inches)
- Color
- Product Page URL
- Image URLs (main product + technical drawings)
- Technical Specs (Shape, Rim type, Installation type, etc.)
- Downloadable Resources:
    • 2D Drawings (Top/Side/Front views)
    • 3D Models (DWG, DXF, FBX, 3DS)
    • BIM Files (Revit, ArchiCAD)
    • Technical PDF Sheets

Output:
-------
- roca_products.json — A list of products in structured JSON format
"""

from bs4 import BeautifulSoup
import json
import time
from selenium import webdriver

# Setup selenium options (Chrome)
options = webdriver.ChromeOptions()
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome(options=options)


# Categories links
base_url = "https://www.us.roca.com"
category_urls = [
    "https://www.us.roca.com/products/two-piece-toilets",
    "https://www.us.roca.com/products/wall-hung-toilets-069-1010",
    "https://www.us.roca.com/products/one-piece-toilets"
]

products = []

# Requests throw selenium
def get_soup(url):
    driver.get(url)
    # wait for js rendring
    time.sleep(2)
    return BeautifulSoup(driver.page_source, 'lxml')

# Extract products links from each category
def get_product_urls(category_url):
    soup = get_soup(category_url)
    return [base_url + a['href'] for a in soup.select('a.content-img') if a.get('href')]

# Scrape the skus from each product link * It Will in variant collection logic *   
def get_skus(soup):
    labels = soup.find_all('label', class_='fondo')
    return [label['for'].split('-')[1] for label in labels if label.get('for')]

# By using the skus in the product page can collect the variants according to it's color
def extract_color(soup, sku):
    color_span = soup.select_one(f"span#fin-name-{sku}")
    if not color_span:
        return None
    try:
        return color_span.text.strip().split("- ")[1]
    except:
        return color_span.text.strip()

# Function to extract the specification from each product page
def extract_specs(soup):
    specs = {}
    for p in soup.find_all('p', attrs={'data-code': True}):
        key = p['data-code']
        try:
            value = p.text.strip().split(': ')[1]
        except:
            value = p.text.strip()
        specs[key] = value
    return specs

# Function to extract each documents shared for this product 
def extract_documents(soup):
    sections = []
    for pane in soup.select('.tab-pane'):
        title = (
            pane.select_one('.card-header').text.strip().split('\n')[0]
            if pane.select_one('.card-header')
            else pane.get('aria-labelledby', '').split('-')[1]
        )
        documents = {}

        for item in pane.select('.tabla-ficha, .list-ficha'):
            if item.select_one('.tabla-title'):
                view_type = item.select_one('.tabla-title').text.strip()
                if '2D' in view_type or '3D' in view_type:
                    documents[view_type] = {}
                    for content in item.select('.tabla-content'):
                        view_name = (
                            content.select_one('.tabla-subtitle').text.strip()
                            if content.select_one('.tabla-subtitle')
                            else view_type
                        )
                        documents[view_type][view_name] = {}
                        for a in content.select('a'):
                            icon_class = [cls for cls in a.get('class', []) if 'icon' in cls]
                            format_type = icon_class[0].split('-')[1] if icon_class else "None"
                            documents[view_type][view_name][format_type] = base_url + a['href']
                else:
                    for li in item.select('li'):
                        doc_title = li.a.text.strip()
                        documents[doc_title] = base_url + li.a['href']
            else:
                for li in item.select('li'):
                    doc_title = li.a.text.strip()
                    documents[doc_title] = base_url + li.a['href']
        sections.append({title: documents})
    return sections


# Extracting the full product data
def extract_product_data(base_product_url, sku):
    url = base_product_url.split("?sku=")[0] + f"?sku={sku}"
    soup = get_soup(url)

    title = soup.select_one("h1#prod-name")
    collection = soup.select_one("#collname")
    dim_element = soup.select_one("span#dim-txt")
    image_tag = soup.find('img', {'data-finish': f'n-finished-{sku}'})
    dim_image_tag = soup.find('img', {'alt': 'Esquema de cotas'})
    factsheet_link = soup.select_one("a#productPDFLink")

    return {
        'Product Page URL': url,
        'Title': title.text.strip() if title else None,
        'Collection': collection.text.strip() if collection else None,
        'ref': sku,
        'Color': extract_color(soup, sku),
        'Dimensions (L/W/H)': dim_element.text.strip() if dim_element else None,
        'image': base_url + image_tag['src'] if image_tag else None,
        'diminsion image': base_url + dim_image_tag['src'] if dim_image_tag else None,
        'Factsheet': base_url + factsheet_link['href'] if factsheet_link else None,
        'spec': extract_specs(soup),
        'docs': extract_documents(soup)
    }


# HERE THE MAIN LOGIC OF SCRAPING
def main():
    # Just keeping track of which category we're on
    category_counter = 0
    # This counts *all* products across all categories
    global_product_index = 0

    for category_url in category_urls:
        category_counter += 1
        print(f"\n📁 [Category {category_counter}] Processing: {category_url}")
        
        product_urls = get_product_urls(category_url)
        total_products = len(product_urls)
        print(f"🔎 Found {total_products} product pages.")

        for product_index, product_url in enumerate(product_urls, start=1):
            print(f"\n➡️ Scraping product {global_product_index + 1} of total across categories")
            print(f"   🛒 Product [{product_index}/{total_products}] → {product_url}")
            
            # Load the product page soup
            soup = get_soup(product_url)
            # Get all SKUs (variants) on the product page
            skus = get_skus(soup)

            for sku_index, sku in enumerate(skus, start=1):
                print(f"   🔧 Variant {sku_index}/{len(skus)} → SKU: {sku}")
                try:
                    # Extract the detailed data for this SKU
                    product_data = extract_product_data(product_url, sku)
                    products.append(product_data)
                    print(f"      ✅ Done: {product_data['Title']}")
                except Exception as e:
                    # Something went wrong, print the error but keep going
                    print(f"      ❌ [Error] Failed to scrape SKU {sku}: {e}")
            global_product_index += 1

    # All done – time to save the collected data into a JSON file
    output_path = r'output.json'
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(products, file, indent=4, ensure_ascii=False)

    print("\n✅ All scraping completed.")
    # Close the browser
    driver.quit()


if __name__ == "__main__":
    main()
