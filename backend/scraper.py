import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import sys
import json

def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)





def get_amazon_prices(product, driver):
    url = f"https://www.amazon.in/s?k={product.replace(' ', '+')}"
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='listitem']"))
        )

        containers = driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")[:10]


        results = []

        for container in containers:
            try:
                # More specific selector to avoid picking up wrong span
             
                title_elem = container.find_element(By.CSS_SELECTOR, "h2.a-size-base-plus, h2.a-size-medium") 
                image_elem = container.find_element(By.TAG_NAME, "img")
                image_url = image_elem.get_attribute("src")
                link=container.find_element(By.CSS_SELECTOR, "a.a-link-normal").get_attribute("href")
                title = title_elem.text.strip()

                # Amazon price is usually in this format
                price_elem = container.find_element(By.CSS_SELECTOR, "span.a-price-whole")
                price_text = price_elem.text.replace(",", "")
                price = float(price_text)
    

                results.append({
                    'site': 'Amazon',
                    'title': title,
                    'price': price,
                    'link': link,
                    'image': image_url
                })

                if len(results) >= 5:
                    break
            except Exception as e:
                continue
            
       
        return results

    except Exception as e:
        print("❌ Error fetching Amazon results:", e)
        return []

def get_best_flipkart_result(product, driver,must_inlude=None):
    driver.get(f"https://www.flipkart.com/search?q={product.replace(' ', '+')}")


    results =[]
    try:
    
        containers = driver.find_elements(By.CSS_SELECTOR, "div._75nlfW")[:10]  # Still useful for context


        for item in containers[:5]:
            try:
                title_elem = item.find_element(By.CSS_SELECTOR, "a.wjcEIp, a.WKTcLC, div.KzDlHZ")
                title = title_elem.text
                image_elem = item.find_element(By.TAG_NAME, "img")
                image_url = image_elem.get_attribute("src")
                price_elem = item.find_element(By.CSS_SELECTOR, "div.Nx9bqj")
                price = float(price_elem.text.replace("₹", "").replace(",", ""))
                try:
                    link=title_elem.get_attribute("href")
                except:
                    link = item.find_element(By.CSS_SELECTOR, "a.CGtC98").get_attribute("href")
                results.append({
                    'site': 'Flipkart',
                    'title': title,
                    'price': price,
                    'link': link,
                    'image': image_url
                })
            except:
               
                continue
        if must_inlude:
            results = [item for item in results if must_inlude.lower() in item['title'].lower()]
    except:
       
        pass
    return results



def get_snapdeal_prices(product, driver):
    url = f"https://www.snapdeal.com/search?keyword={product.replace(' ', '%20')}"
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.product-tuple-listing"))
        )

        containers = driver.find_elements(By.CSS_SELECTOR, "div.product-tuple-listing")[:10]
        results = []

        for container in containers:
            try:
                title_elem = container.find_element(By.CSS_SELECTOR, "p.product-title")
                price_elem = container.find_element(By.CSS_SELECTOR, "span.lfloat.product-price")
                link = container.find_element(By.CSS_SELECTOR, "a.dp-widget-link").get_attribute("href")
                image_elem = container.find_element(By.TAG_NAME, "img")
                image_url = image_elem.get_attribute("src")
               
                title = title_elem.text.strip()
                price = float(price_elem.text.strip().replace("Rs. ", "").replace(",", ""))

              

                results.append({
                    'site': 'Snapdeal',
                    'title': title,
                    'price': price,
                    'link': link,
                    'image': image_url
                })

                if len(results) >= 5:
                    break
            except Exception as e:
               
                continue

        return results

    except Exception as e:
       
        return []
    
    

    



if __name__ == "__main__":
    product_name = sys.argv[1]
    driver = create_driver()
    results = {
        "amazon": get_amazon_prices(product_name, driver),
        "flipkart": get_best_flipkart_result(product_name, driver),
        "snapdeal": get_snapdeal_prices(product_name, driver)
    }
    driver.quit()
    print(json.dumps(results))

