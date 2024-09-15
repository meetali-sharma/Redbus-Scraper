import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime

# Connecting to the database using st.secrets
conn = mysql.connector.connect(
    host=st.secrets["my_database"]["host"],
    user=st.secrets["my_database"]["user"],
    password=st.secrets["my_database"]["password"],
    database=st.secrets["my_database"]["database"]
)

# Creating a cursor object to execute SQL queries
cursor = conn.cursor()

# Creating sidebar for page navigation
page = st.sidebar.radio("Navigation", ['Home', 'Travel Details'])

# Page navigation: Home page
if page == 'Home':
    st.title(':red[RedBus WebScrap Project]')
    st.subheader(':blue[By Meetali Sharma]')
    st.write('This application demonstrates a use case for web scraping.')
    st.write('You can use this application to check bus seats and fare for different RTC.')

    st.image("https://hindi.news24online.com/wp-content/uploads/2023/08/redbus.jpg",width=500)

# Page navigation: Travel Details page
if page == 'Travel Details':
    # Creating drop-down menus
    col1, col2, col3 = st.columns(3, gap='small')

    # Query to get distinct route names
    cursor.execute("SELECT DISTINCT route_name FROM bus_routes ORDER BY 1")
    df = pd.DataFrame(cursor.fetchall(), columns=["route_name"])

    # Extracting the route names as a list
    routes = df['route_name'].tolist()

    # Displaying the select box with route names
    user_route = col1.selectbox('Route', routes)
    user_bustype = col2.selectbox('Seat Type', ['Sleeper', 'Non-sleeper'])

    # Additional select boxes for departing time and price range
    col1, col2 = st.columns(2, gap='small')
    departing_time = col1.selectbox('Departing Time', ['Morning: 6AM-12PM', 'Noon: 12PM - 5PM', 'Evening: 5PM - 9PM', 'Night: 9PM - 6AM'])
    price_range = col2.selectbox('Price range', ['0-500', '500-1000', '1000-2000', '2000-3000', '3000-4000', '4000-5000'])

    # Convert price_range into min and max values
    price_min, price_max = map(int, price_range.split('-'))

    # Display result
    if st.button('Show Available Buses'):
        # SQL query using the user's input as filters
        query = """
           SELECT busname, departing_time, bustype, price, seats_available
           FROM bus_routes
           WHERE route_name = %s
           AND bustype LIKE %s
           AND price BETWEEN %s AND %s
           ORDER BY departing_time, price
           """

        # Define the conditions for the seat type
        seat_condition = f"%{user_bustype}%"

        # Executing the query with user input parameters
        cursor.execute(query, (user_route, seat_condition, price_min, price_max))
        result = cursor.fetchall()

        # If there are results, display them
        if result:
            df_result = pd.DataFrame(result, columns=["Bus Name", "Departure Time", "Bus Type", "Price (INR)", "Seats Available"])

            # Convert 'Departure Time' to 12-hour format, handling Timedelta objects
            def convert_to_12_hour(time_value):
                if isinstance(time_value, str):
                    try:
                        return datetime.strptime(time_value, '%H:%M:%S').strftime('%I:%M %p')
                    except ValueError:
                        return time_value
                elif isinstance(time_value, pd.Timedelta):
                    # Convert Timedelta to total seconds and then to time format
                    seconds = time_value.total_seconds()
                    hours = int(seconds // 3600)
                    minutes = int((seconds % 3600) // 60)
                    return datetime.strptime(f"{hours:02}:{minutes:02}:00", '%H:%M:%S').strftime('%I:%M %p')
                else:
                    return str(time_value)

            # Apply the conversion to the 'Departure Time' column
            df_result["Departure Time"] = df_result["Departure Time"].apply(convert_to_12_hour)

            st.write("Available Buses for your selection:")
            st.dataframe(df_result)
        else:
            st.write("No buses found for the selected criteria.")

# Clean up
cursor.close()
conn.close()
