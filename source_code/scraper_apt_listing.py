# headless mode which runs Chrome without opening a visible browser window
# important: don't let pc sleep otherwise selenium will crash

# run following command in terminal to rin the file:      python .\scraper_apt_listing.py

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

base_url = "https://www.bdhousing.com/homes/listings/Sale/Residential/Apartment"

def scrape_page(page_id, options):
    all_data = []
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(45)
    driver.get(f"{base_url}?page={page_id}")
    containers = driver.find_elements(By.XPATH, '//div[@class="listing-list"]')
    print(f"scraping page {page_id} is started")

    for container in containers:

        p_id = page_id
        
        try:
            title = container.find_element(By.XPATH, './/h1[@class="title fix_title"]').text.strip()
            title = title.strip()[:-5]  # Removes last 5 characters to remove word "sale"
        except NoSuchElementException:
            title = "None"

        try:
            feature_elements = container.find_elements(By.XPATH, './/div[@class="ribbon"]')
            feature = feature_elements[0].text.strip() if feature_elements and feature_elements[0].text.strip() else "None"
        except NoSuchElementException:
            feature = "None"

        try:
            link = container.find_element(By.XPATH, './/div[@class="listing-list-photo"]/a').get_attribute('href')
        except NoSuchElementException:
            link = "None"

        try:
            total_price = container.find_element(By.XPATH, './/label[@class="control-label1 new"]').text.replace("৳", "").strip()
        except NoSuchElementException:
            total_price = "None"

        try:
            per_sqft_price = container.find_elements(By.XPATH, './/span[@class="badge badge-default"]')
            per_sqft_price = per_sqft_price[0].text.replace("৳", "").strip() if per_sqft_price else "None"
        except NoSuchElementException:
            per_sqft_price = "None"

        try:
            address = container.find_element(By.XPATH, './/p[@class="location"]').text
        except NoSuchElementException:
            address = "None"

        try:
            bedrooms = container.find_element(By.XPATH, './/div[@class="listing-info bedroom"]/span[@class="number"]').text
        except NoSuchElementException:
            bedrooms = "None"

        try:
            bathrooms = container.find_element(By.XPATH, './/div[@class="listing-info bath"]/span[@class="number"]').text
        except NoSuchElementException:
            bathrooms = "None"

        
        try:
            size_sqft = container.find_element(By.XPATH, './/div[@class="listing-info size"]/span[@class="number"]').text
        except NoSuchElementException:
            size_sqft = "None"

        try:
            property_owner = container.find_element(By.XPATH, './/h4[@class="media-heading"]').text
        except NoSuchElementException:
            property_owner = "None"

        try:
            property_owner_type = container.find_elements(By.XPATH, './/p[@class="property-owner"]/span')[0].text
        except NoSuchElementException:
            property_owner_type = "None"
        
        try:
            listing_date = container.find_elements(By.XPATH, './/p[@class="property-owner"]/span')[1].text
        except NoSuchElementException:
            listing_date = "None"

        try:
            premium_project = driver.find_element(By.XPATH, '//img[contains(@src, "prem_icon.png")]')
            premium_project = premium_project.get_attribute('data-original-title')
        except NoSuchElementException:
            premium_project = "None"

        property_summary_dict = {}
        property_features_dict = {}

        try:

            driver1 = webdriver.Chrome(options=options)
            driver1.set_page_load_timeout(45)
            driver1.get(link)
            
            containers1 = driver1.find_elements(By.XPATH, '//ul[@class="detail-list"]')
            for ul in containers1:
                items = ul.find_elements(By.TAG_NAME, 'li')
                for item in items:
                    try:
                        label = item.find_element(By.TAG_NAME, 'label').text
                        value = item.find_element(By.TAG_NAME, 'span').text
                        # Cleaning up label text
                        key = label.replace(":", "").strip()
                        property_summary_dict[key] = value.strip()
                    except:
                        # Skip if label or span not found
                        continue
            
            containers2 = driver1.find_elements(By.XPATH, '//div[@class="row content_areamMid"]')
            features = [line for container in containers2 for line in container.text.split('\n')]
            property_features_dict = {feature: 1 for feature in features}

            time.sleep(2)

        except Exception as e:
            print(f"driver1 failed for {link}: {e}")
            property_summary_dict = {}
            property_features_dict = {}

        finally:
            try:
                driver1.quit()
            except Exception as cleanup_error:
                print(f"Driver cleanup failed: {cleanup_error}")


        # Combining all data
        row = {
            "Page": p_id,
            "Title": title,
            "Feature": feature,
            "Link": link,
            "Total Price": total_price,
            "Price per Sqft": per_sqft_price,
            "Address": address,
            "Bedrooms": bedrooms,
            "Bathrooms": bathrooms,
            "Size (sqft)": size_sqft,
            "Owner": property_owner,
            "Owner Type": property_owner_type,
            "Listing Date": listing_date,
            "Premium Project": premium_project,
            "Property_summary_dict": property_summary_dict,
            "Property_features_dict": property_features_dict

        }

        all_data.append(row)

    print(f"scraping page {page_id} is done")
    time.sleep(10)
    # close() only shuts the current tab.
    # quit() shuts down the entire browser and ends the session.
    # Using .quit() avoids lingering sessions that can cause error.

    # driver.close()
    driver.quit()
    return all_data

def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    # Save to DataFrame and CSV
    # Use "utf-8-sig" to ensure Excel opens it correctly with Bangla characters.
    df.to_csv(filename, encoding="utf-8-sig", index=False)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    options = Options()
    options.add_argument("--headless=new")

    new_all_data = []
    # place page range to scrape
    for page_id in range(1, 3):
        page_data = scrape_page(page_id, options)
        new_all_data.extend(page_data)
        time.sleep(10)

    save_to_csv(new_all_data, "E:/9_Tableau_Projects/5_Dhaka_apartment_sale_listings_analysis/scraped_data/apartment_listing_1_page_1_to_5.csv")