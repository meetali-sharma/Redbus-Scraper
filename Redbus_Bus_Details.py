import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import glob
import mysql.connector
from sqlalchemy import create_engine, text


# Function to scroll to the bottom of the page
def scroll_to_bottom(driver, max_tries=15):
    last_height = driver.execute_script("return document.body.scrollHeight")
    tries = 0
    while tries < max_tries:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        tries += 1


# Function to click all instances of the "View Buses" button
def click_view_buses_buttons(driver):
    try:
        # Locate all buttons with class name 'button'
        view_buses_buttons = driver.find_elements(By.XPATH, "//div[@class='button']")

        if view_buses_buttons:
            print(f"Found {len(view_buses_buttons)} 'View Buses' buttons. Clicking them...")

            for button in view_buses_buttons:
                # Scroll the button into view using JavaScript to ensure it's clickable
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(1)  # Small delay to ensure the scroll completes

                try:
                    # Click the button using JavaScript to avoid interception issues
                    driver.execute_script("arguments[0].click();", button)
                    print("Clicked on 'View Buses' button to reveal RTC buses.")
                    time.sleep(3)  # Wait for buses to load after each click
                except Exception as e:
                    print(f"Error clicking the button: {e}")
        else:
            print("No 'View Buses' buttons found.")
    except NoSuchElementException:
        print("View Buses buttons not found on the page.")


# Set up WebDriver
Driver = webdriver.Chrome()
Driver.maximize_window()

# List to hold all the scraped data
all_scraped_data = []

# Load all Excel files
file_list = glob.glob("*.xlsx")

#For extracting only numerical value from text using regular expression
def extract_seats(seats_text):
    seats = re.findall(r'\d+', seats_text)
    return int(seats[0]) if seats else 0


def extract_price(price_text):
    price = re.findall(r'\d+', price_text)
    return float("".join(price)) if price else 0.0


def extract_rating(rating_text):
    rating = re.findall(r'\d+', rating_text)
    return float("".join(rating)) if rating else 0.0


# Iterate through each file
for file_name in file_list:
    print(f"Processing file: {file_name}...")

    # Load the href values and route names from the current Excel file
    file = pd.read_excel(file_name)
    links = file['Route_link'].tolist()
    route_names = file['Route_name'].tolist()

    # List to hold scraped data for the current file
    scraped_data = []

    # Loop through each href and route name and scrape data
    for href, route_name in zip(links, route_names):
        try:
            print(f"Opening {href} for route {route_name}...")
            Driver.get(href)
            time.sleep(3)  # Give time for the page to load

            # Click on all "View Buses" buttons to reveal hidden buses
            click_view_buses_buttons(Driver)

            # Scroll down to load dynamic content
            scroll_to_bottom(Driver)

            # Wait until the rows are loaded (increased timeout to 45 seconds)
            try:
                rows = WebDriverWait(Driver, 45).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[class*="clearfix"]'))
                )
            except TimeoutException:
                print(f"Timeout while waiting for rows to load on {href}")
                continue  # Skip to the next link if rows are not found

            seen_rows = set()

            # Loop through each row
            for row in rows:
                try:
                    travels = row.find_element(By.CLASS_NAME, 'travels').text
                except NoSuchElementException:
                    travels = 'N/A'

                try:
                    bus_type = row.find_element(By.CLASS_NAME, 'bus-type').text
                except NoSuchElementException:
                    bus_type = 'N/A'

                try:
                    dp_time = row.find_element(By.CLASS_NAME, 'dp-time').text
                except NoSuchElementException:
                    dp_time = 'N/A'

                try:
                    duration = row.find_element(By.CLASS_NAME, 'dur').text
                except NoSuchElementException:
                    duration = 'N/A'

                try:
                    bp_time = row.find_element(By.CLASS_NAME, 'bp-time').text
                except NoSuchElementException:
                    bp_time = 'N/A'

                try:
                    fare = row.find_element(By.CLASS_NAME, 'fare.d-block').text
                    fare = extract_price(fare)
                except NoSuchElementException:
                    fare = 0.0

                try:
                    star_rating = row.find_element(By.CLASS_NAME, 'rating rat-red ').text
                    star_rating = extract_rating(star_rating)
                except NoSuchElementException:
                    star_rating = 0.0

                try:
                    seat_left = row.find_element(By.CLASS_NAME, 'seat-left').text
                    seat_left = extract_seats(seat_left)
                except NoSuchElementException:
                    seat_left = 0

                row_key = (travels, bus_type, dp_time, duration, bp_time, fare, star_rating, seat_left)

                if travels != 'N/A' and bus_type != 'N/A' and dp_time != 'N/A' and duration != 'N/A' and bp_time != 'N/A':
                    if row_key not in seen_rows:
                        seen_rows.add(row_key)
                        scraped_data.append({
                            'route_name': route_name,
                            'route_link': href,
                            'busname': travels,
                            'bustype': bus_type,
                            'departing_time': dp_time,
                            'duration': duration,
                            'reaching_time': bp_time,
                            'price': fare,
                            'star_rating': star_rating,
                            'seats_available': seat_left
                        })

        except Exception as e:
            print(f"Error scraping {href}: {str(e)}")

    # Append the scraped data for the current file to the master list
    all_scraped_data.extend(scraped_data)

# Quit the WebDriver after finishing all tasks
Driver.quit()

# Convert the scraped data to a Pandas DataFrame
df = pd.DataFrame(all_scraped_data)
df.to_excel("Combined_scraped_bus.xlsx", index=False)

print("Data successfully saved to 'Combined_scraped_bus.xlsx'")

# Database connection
# Enter the required hostname, username, password and database name 
connection = mysql.connector.connect(
    host="",
    user="",
    password="",
    database="redbus",
)

# Create a cursor object
cursor = connection.cursor()

# Truncate the existing records in the bus_routes table
truncate_query = "TRUNCATE TABLE bus_routes"
cursor.execute(truncate_query)
connection.commit()
print("Existing records truncated successfully.")

# Create an SQLAlchemy engine
engine = create_engine("mysql+mysqlconnector://Meetali:Passw0rd#@DESKTOP-NCF2KBL/redbus")

record_count = 0
with engine.connect() as conn:
    trans = conn.begin()
    try:
        for index, row in df.iterrows():
            sql = text("""
            INSERT INTO bus_routes (route_name, route_link, busname, bustype, departing_time, duration, reaching_time, price, star_rating, seats_available)
            VALUES (:route_name, :route_link, :busname, :bustype, :departing_time, :duration, :reaching_time, :price, :star_rating, :seats_available)
            """)
            conn.execute(sql, {
                'route_name': row['route_name'],
                'route_link': row['route_link'],
                'busname': row['busname'],
                'bustype': row['bustype'],
                'departing_time': row['departing_time'],
                'duration': row['duration'],
                'reaching_time': row['reaching_time'],
                'price': row['price'],
                'star_rating': row['star_rating'],
                'seats_available': row['seats_available']
            })
            record_count += 1
            print(f"Record {index + 1} inserted successfully.")

        trans.commit()
        print("All records inserted and transaction committed successfully.")
    except Exception as e:
        print(f"Error inserting records: {e}")
        trans.rollback()
    finally:
        conn.close()

# Print a summary of the total number of inserted records
print(f"\nTotal records inserted: {record_count}")
