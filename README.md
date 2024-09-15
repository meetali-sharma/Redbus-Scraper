# Redbus-Scraper

This project is a web scraper designed for extracting bus route details from [Redbus](https://www.redbus.in). The tool scrapes all available bus routes, along with bus details such as bus names, types, price ranges, and more. The scraped data is then stored in a SQL database for further use.

## Features
- Scrapes bus routes and details from Redbus.
- Extracts bus name, type, price range, and other bus-specific information.
- Saves the data in a MySQL database.
- Provides a user interface using Streamlit for data interaction.

## Prerequisites
Before you begin, ensure you have met the following requirements:
- Python 3.7 or higher
- MySQL server
- Web browser (for Selenium)
- Install the required Python packages using the command:
  
  ```bash
  pip install -r requirements.txt
  ```

## Packages Used

### 1. **time**
The `time` module is used to introduce delays in the script, primarily with the `sleep()` function to wait for elements on web pages to load.

### 2. **selenium**
Selenium is used for automating the interaction with the Redbus website to scrape data. Key components used:
- **Expected Conditions**: Waits for certain conditions to be met (e.g., element visibility).
- **By**: Locates elements on the web page using various strategies (e.g., ID, class, XPath).
- **WebDriverWait**: Implements explicit waits to handle dynamic web elements.
- **NoSuchElementException**: Handles exceptions when elements cannot be found.
- **TimeoutException**: Catches timeouts when a condition is not met in the specified time.

### 3. **pandas**
Pandas is used for handling and manipulating the scraped data, allowing easy storage and export (e.g., saving as Excel files).

### 4. **re (regular expressions)**
The `re` module is used to search and match patterns in strings to extract specific details from the web content.

### 5. **glob**
The `glob` module is used to search for files in the local system that match a specific pattern (e.g., extracting all `.csv` or `.txt` files in a folder).

### 6. **mysql-connector-python**
This library is used to connect Python to a MySQL database and execute SQL queries for data storage.

### 7. **SQLAlchemy**
SQLAlchemy is used for database interaction, primarily to manage connections to the database and handle SQL queries using Python objects. The `create_engine()` function is used to establish a connection.

### 8. **Streamlit**
Streamlit is used to build an interactive web application that allows users to view and interact with the scraped data.

## Project Steps

1. **Store Route Information**:  
   Gather route names and links into a list using the file Redbus_Route_Fetcher.py

------------------------------------ For Steps 2-6 use the file Redbus_Bus_Details.py -------------------------------------------------------

2. **Extract Bus Details**:  
   Using Selenium, extract bus details such as names, types, and prices from the Redbus website.

3. **Loop through Routes**:  
   Iterate over each route link and scrape bus details for every route.

4. **Save Data Locally**:  
   Store the bus details in lists and export them to Excel for local backup.

5. **Connect to MySQL**:  
   Establish a connection to the MySQL database and create the necessary tables.

6. **Insert Data into Database**:  
   Insert the scraped bus details into the MySQL database.

7. **Create Streamlit App**:  
   Build an interactive web application using Redbus_Streamlit.py to allow users to access and view the bus route data in real time.
