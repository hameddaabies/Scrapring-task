"""
woodbridge.py
Scrapes detailed product data from Woodbridgebath.com smart toilet listings.
Extracts structured fields such as pricing, title, specs, image gallery,
documents, and customer reviews.
Data is exported to JSON format.

Used Tools:
- Selenium for dynamic rendering
- BeautifulSoup for parsing
- Webdriver-manager for handling ChromeDriver
"""

from bs4 import BeautifulSoup
import json
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Setup selenium options (Chrome)
options = webdriver.ChromeOptions()
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome(options=options)

# Category link
urls = ["https://www.woodbridgebath.com/can/home/product/index/classid/3//attr/15_86"]


# to get the products lnks from the category url
def extract_product_links(soup):
    return [
        a['href'] for div in soup.find_all('div', class_='img')
        if (a := div.find('a')) and a.get('href')
    ]

# Logic of scraping product images 
def get_images(soup):
    images = []
    try:
        images += [img['src'] for div in soup.select('div.swiper-wrapper div') if (img := div.find('img'))]
        images += [img['src'] for div in soup.select('div.proimgshow01') if (img := div.find('img'))]

        swiper_div = soup.select_one('div.swiper.proimgshow02.J_swiper02_1622')
        if swiper_div and swiper_div.has_attr('data-imgdata'):
            image_data = json.loads(swiper_div['data-imgdata'])
            images += [item['pic'] for item in image_data]
    except:
        pass
    return images

# Logic of scraping product reviews 
def extract_reviews(soup):
    reviews = []
    rev_div = soup.find('div', class_='blist')
    if not rev_div:
        return reviews
    for item in rev_div.find_all('div', class_='item'):
        try:
            name = item.find('div', class_='inf').find('div', class_='nam').text.strip()
            star_rating = len(item.find('div', class_='sta').find_all('i', class_='on'))
            review_content = item.find('div', class_='txt').text.strip()
            review_date = item.find('div', class_='mor').find('div', class_='tim').text.strip()
            reviews.append({
                'Name': name,
                'Star Rating': star_rating,
                'Review Content': review_content,
                'Review Date': review_date
            })
        except:
            continue
    return reviews

# clean the price from any signs and convert the text to float
def clean_price(value):
    """
    Cleans the price string by removing currency symbols and commas.
    Args:
        price_str (str): Price string like "$1,299.00"
    Returns:
        float: Cleaned price as float (e.g., 1299.0)
    """
    try:
        return float(re.sub(r'[^\d.]', '', value))
    except:
        return None

# Logic of scrolling to the reviews and wait js rendering    
def click_next_page():
    try:
        next_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="J_review_page"]/div[3]/a[2]'))
        )
        driver.execute_script("arguments[0].scrollIntoView()", next_btn)
        time.sleep(1)
        next_btn.click()
        time.sleep(2)
        return BeautifulSoup(driver.page_source, 'lxml')
    except:
        return None

# Extract the data after fetching the response
def extract_product_data(product_link):
    driver.get(product_link)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'lxml')

    try:
        title = soup.find('h1', class_='tit').text.strip()
        price_div = soup.find('div', class_='price')
        actual_price = price_div.find('strong').text.strip()
        clean_actual_price = clean_price(actual_price)
        old_price = price_div.find('s').text.strip() if price_div.find('s') else None
        clean_old_price = clean_price(old_price)
        saving = price_div.find('span').text.strip() if price_div.find('span') else None
        rating = soup.find('div', class_='val').text.strip() if soup.find('div', class_='val') else None

        availability = 'in stock'
        if 'Not Available for Shipping' in soup.find('div', class_='tit').text:
            availability = 'out of stock'

        breadcrumb_div = soup.find('div', class_='breadcrumb')
        code = breadcrumb_div.find_all('div')[-1].find('a').text.split(":")[1].strip()

        images = get_images(soup)

        overview = [div.text.strip() for div in soup.select('div.mb01block div.nam')]
        descriptions = [p.text.strip() for p in soup.select('div.mb01list p') if p.text.strip()]

        # Technical Details
        product_details = {}
        try:
            table = soup.find('table', class_='table stable ke-zeroborder')
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) == 2:
                    key = cells[0].text.strip()
                    value = cells[1].text.strip()
                    product_details[key] = value
        except:
            pass

        # Documents
        documents = {
            link.text.strip(): link['href']
            for link in soup.select('.mb08list .item a')
        }

        # Reviews
        reviews = extract_reviews(soup)
        if not soup.find('a', {'class': 'ne no'}):
            while True:
                next_soup = click_next_page()
                if not next_soup:
                    break
                reviews += extract_reviews(next_soup)
                if next_soup.find('a', {'class': 'ne no'}):
                    break

        return {
            'Product URL': product_link,
            'Title': title,
            'Price': clean_actual_price,
            'Old Price': clean_old_price,
            'Currency':"$",
            'Saving': saving,
            'Rating': rating,
            'Availability': availability,
            'Images': images,
            'PRODUCT OVERVIEW': overview,
            'Description': descriptions,
            'Technical Details': product_details,
            'Documents': documents,
            'Customer Reviews': reviews
        }
    except Exception as e:
        print(f"[Error] {e} in product: {product_link}")
        return None

# Handling the requests throw selenium 
def scrape_products_from_url(url):
    driver.get(url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    return extract_product_links(soup)


# HERE THE MAIN LOGIC OF THE SCRAPING
def main():
    # Countainer of the collected data
    all_data = []
    counter = 0
    for url in urls:
        # Here trying fetching the products url from category link
        product_links = scrape_products_from_url(url)
        for link in product_links:
            # Extract the data from each product and some debugging prints for tracking 
            data = extract_product_data(link)
            if data:
                counter += 1
                print(f"[{counter}/{len(product_links)}] Scraped: {data['Title']}")
                print("-" * 70)
                all_data.append(data)
    # Save the output data in json file 
    output_path = r'output.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    # Close the browser
    driver.quit()
    print("Scraping Completed.")

if __name__ == "__main__":
    main()
