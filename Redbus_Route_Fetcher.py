#This program when executed get all the bus routes and it's link present for that
# RTC and gives an output in an exel sheet.

import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



Driver = webdriver.Chrome()
wait = WebDriverWait(Driver, 30)

Driver.get('https://www.redbus.in')

Rtc_links=[]
Driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
time.sleep(2)

wait = WebDriverWait(Driver, 20)
#Enter the name of the Road Transport Corporation for which you want to extract the route links.
rtc_name_element = wait.until(EC.element_to_be_clickable((By.XPATH, "//div [contains(text(),'Kerala RTC')]")))

Driver.execute_script("arguments[0].scrollIntoView(true);", rtc_name_element)
time.sleep(1)

Driver.execute_script("arguments[0].click();", rtc_name_element)


def scrape_page():
    # Wait for the routes container to load
    try:
        routes_container = WebDriverWait(Driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "route_link")))

        # Loop through each route to extract details
        for route in routes_container:
            try:
                # Find all anchors with class 'route' inside each route element
                anchors = route.find_elements(By.CSS_SELECTOR, 'a.route')

                # Extract and store href and text of each anchor
                anchor_data = [(anchor.get_attribute('href'), anchor.text) for anchor in anchors]

                for href, text in anchor_data:
                    Rtc_links.append({'Route_name': text, 'Route_link': href})

            except Exception as e:
                print(f"An error occurred while processing a route: {e}")
                continue
    except Exception as e:
        print(f"An error occurred while loading routes container: {e}")

# Update the range for page numbers based on the total number of pages present for that RTC
for page_number in range(1, 4):
    scrape_page()
    if page_number < 4:
        try:
            # Locate the pagination container
            pagination_container = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="root"]/div/div[4]/div[12]')
            ))

            # Locate the next page button within the container
            next_page_button = pagination_container.find_element(
                By.XPATH, f'.//div[contains(@class, "DC_117_pageTabs") and text()="{page_number + 1}"]'
            )

            # Ensure the next page button is in view
            actions = ActionChains(Driver)
            actions.move_to_element(next_page_button).perform()
            time.sleep(1)  # Wait for a bit after scrolling


            # Click the next page button
            next_page_button.click()

            # Wait for the page number to update to the next page
            wait.until(EC.text_to_be_present_in_element(
                (By.XPATH, '//div[contains(@class, "DC_117_pageTabs DC_117_pageActive")]'), str(page_number + 1)))

            time.sleep(3)
        except Exception as e:
            print(f"An error occurred while navigating to page {page_number + 1}: {e}")
            break
for link in Rtc_links:
    print(link)


# Assuming scrape_page() fills Rtc_links with the scraped data
def export_to_excel(file_name):
    # Create a pandas DataFrame from the list of dictionaries (Rtc_links)
    df = pd.DataFrame(Rtc_links)

    # Export the DataFrame to an Excel file
    df.to_excel(file_name, index=False, engine='openpyxl')

# Example usage
scrape_page()  # This will scrape the data into Rtc_links
export_to_excel('Route.xlsx')