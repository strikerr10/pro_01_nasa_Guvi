import streamlit as st
import pymysql
import pandas as pd
from datetime import date
import base64

# Function to connect to the MySQL database
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="gokul",
        password="1234",
        database="neo",
        cursorclass=pymysql.cursors.DictCursor
    )

queries = {
    "1.Count how many times each asteroid has approached Earth":
            """select name, count(*) as no_of_Approaches from asteroids a
            join close_approach ca 
            on a.id = ca.neo_reference_id   
            group by name                    
            order by no_of_Approaches desc""",

    "2.Average velocity of each asteroid over multiple approaches":
        """select name, avg(ca.relative_velocity) as avg_velocity from asteroids a
        join close_approach ca 
        on a.id = ca.neo_reference_id
        group by name
        order by avg_velocity desc""",

    "3.List top 10 fastest asteroids":
        """select name, max(ca.relative_velocity) as Fastest_asteroids from asteroids a
        join close_approach ca 
        on a.id = ca.neo_reference_id
        group by name
        order by Fastest_asteroids DESC
        limit 10""",

    "4.Find potentially hazardous asteroids that have approached Earth more than 3 times":
        """select name, count(*) as approach_count from asteroids a
        join close_approach ca 
        on a.id = ca.neo_reference_id
        where a.is_potentially_hazardous_asteroid = 1 
        group by name                                 
        having approach_count > 3 """,

    "5.Find the month with the most asteroid approaches":
        """select date_format(close_approach_date, '%Y-%m') as month, count(*) as approach_count from close_approach
        group by month
        order by approach_count desc
        limit 1""",

    "6.Get the asteroid with the fastest ever approach speed":
        """select name, ca.relative_velocity as Fast_app_speed from asteroids a
        join close_approach ca
        on a.id = ca.neo_reference_id
        order by Fast_app_speed DESC
        LIMIT 1""",

    "7.Sort asteroids by maximum estimated diameter (descending)":
       """select name, estimated_diameter_km_max from asteroids
        order by estimated_diameter_km_max desc""",

    "8.Asteroids whose closest approach is getting nearer over time":
        """ select name, date_format(ca.close_approach_date, '%Y-%m'), ca.miss_dis_km as miss_distance_km from asteroids a
        join close_approach ca 
        on a.id = ca.neo_reference_id
        order by name, ca.close_approach_date """,

    "9.Display name of each asteroid with date and miss distance of its closest approach":
        """select name, date_format(ca.close_approach_date, '%Y-%m'), ca.miss_dis_km from asteroids a
          join close_approach ca 
          on a.id = ca.neo_reference_id
          where (a.id, ca.miss_dis_km)
          in( select neo_reference_id, min(miss_dis_km) from close_approach
          group by neo_reference_id )""",

    "10.List names of asteroids with velocity > 50,000 km/h":
        """ select distinct a.name from asteroids a
        join close_approach ca 
        on a.id = ca.neo_reference_id
        where ca.relative_velocity > 50000 """,

    "11.Count how many approaches happened per month":
        """ select date_format(close_approach_date, '%Y-%m') as month, COUNT(*) as approach_count from close_approach
        group by month
        order by month """,

    "12.Find asteroid with the highest brightness (lowest magnitude value)":
        """select name, absolute_magnitude_h from asteroids
        order by absolute_magnitude_h asc
        limit 1 """,

    "13.Get number of hazardous vs non-hazardous asteroids":
       """ select is_potentially_hazardous_asteroid, count(*) as count from asteroids
        group by is_potentially_hazardous_asteroid """,

    "14.Asteroids that passed closer than the Moon (miss_dist < 1 LD)":
       """ select a.name,  date_format(ca.close_approach_date, '%Y-%m'), ca.miss_dis_lunar from asteroids a
        join close_approach ca 
        on a.id = ca.neo_reference_id
        where ca.miss_dis_lunar < 1 """,

    "15.Asteroids that came within 0.05 AU":
        """ select name, date_format(ca.close_approach_date, '%Y-%m'), ca.astronomical from asteroids a
        join close_approach ca 
        on a.id = ca.neo_reference_id
        where ca.astronomical < 0.05 """,
    "16.Average estimated diameter of hazardous vs. non-hazardous asteroids":
         """ select is_potentially_hazardous_asteroid,  avg(estimated_diameter_km_min) as avg_diameter_min, avg(estimated_diameter_km_max) as avg_diameter_max from asteroids
        group by is_potentially_hazardous_asteroid """,
    "17.Top 5 brightest hazardous asteroids (lowest magnitude)":
        """ select name, absolute_magnitude_h from asteroids
        where is_potentially_hazardous_asteroid = 1
        order by absolute_magnitude_h ASC
        limit 5 """,
    "18.Asteroids with the greatest difference between estimated min and max diameter":
        """ select name, (estimated_diameter_km_max - estimated_diameter_km_min) as diameter_dif from asteroids
        order by diameter_dif desc
        limit 10 """,
    "19.Top 10 asteroids with the most close approaches in a single month":
        """ select a.name, date_format(ca.close_approach_date, '%Y-%m') as month, count(*) as approaches from asteroids a
        join close_approach ca 
        on a.id = ca.neo_reference_id
        group by a.name, month
        order by approaches DESC
        limit 10 """,
    "20.Q20 Average miss distance per asteroid":
        """ select a.name, avg(ca.miss_dis_km ) as avg_miss_distance_km from asteroids a
        join close_approach ca 
        on a.id = ca.neo_reference_id
        group by a.name
        order by avg_miss_distance_km asc """}

st.set_page_config(page_title="Asteroid Insights", layout="wide")

def set_background(png_file_path):
    with open(png_file_path, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Use your local file path (raw string to avoid escape issues)
set_background(r"C:\Users\gkstr\OneDrive\PYTHON DATASCIENCE\Guvi projects\project01\thumb-1920-694587.png")

        
# Set up Streamlit

st.title(" NASA Asteroid Tracker 🪐")
st.header("Solar system dynamics")

# Query toggle
if "query" not in st.session_state:
    st.session_state.query = False

st.sidebar.markdown("---")
st.sidebar.markdown("### Query")
if st.sidebar.button("Queries"):
    st.session_state.query = not st.session_state.query

# Query Selection and Execution
if st.session_state.query:
    selected_query = st.selectbox("Choose a query to run:", list(queries.keys()))

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(queries[selected_query])
        results = cursor.fetchall()
        df = pd.DataFrame(results)

        st.subheader("📊 Query Result")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")

# Filter toggle
if "show_filters" not in st.session_state:
    st.session_state.show_filters = False

st.sidebar.markdown("---")
st.sidebar.markdown("### Apply Custom Filters")
if st.sidebar.button("Filter Criteria"):
    st.session_state.show_filters = not st.session_state.show_filters

# Filter UI
if st.session_state.show_filters:
    st.subheader("🔍 Filter Criteria")

    col1, col2, col3 = st.columns(3)

    with col1:
        magnitude_range = st.slider("Magnitude Range", 13.8, 32.6, (13.8, 32.6))
        min_diameter = st.slider("Min Estimated Diameter (km)", 0.0, 4.62, (0.0, 4.62))
        max_diameter = st.slider("Max Estimated Diameter (km)", 0.0, 10.33, (0.0, 10.33))

    with col2:
        velocity_range = st.slider("Relative Velocity (km/h)", 1418.21, 173071.83, (1418.21, 173071.83))
        au_range = st.slider("Astronomical Unit", 0.0, 0.5, (0.0, 0.5))
        hazardous_only = st.selectbox("Only Show Potentially Hazardous", [0, 1])

    with col3:
        start_date = st.date_input("Start Date", value=date(2020, 1, 1))
        end_date = st.date_input("End Date", value=date.today())

    if st.button("Apply Filter"):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Get all filter values
            mag_min, mag_max = magnitude_range
            dia_min_min, dia_min_max = min_diameter
            dia_max_min, dia_max_max = max_diameter
            vel_min, vel_max = velocity_range
            au_min, au_max = au_range
            haz = hazardous_only
            start = start_date.strftime('%Y-%m-%d')
            end = end_date.strftime('%Y-%m-%d')
            # Build SQL query dynamically
            filter_query = f"""
            select a.name, a.absolute_magnitude_h, a.estimated_diameter_km_min, a.estimated_diameter_km_max,
            a.is_potentially_hazardous_asteroid, ca.close_approach_date, ca.relative_velocity,
            ca.astronomical, ca.miss_dis_km
            from asteroids a
            join close_approach ca on a.id = ca.neo_reference_id
            where a.absolute_magnitude_h between {mag_min} and {mag_max}
            and a.estimated_diameter_km_min between {dia_min_min} and {dia_min_max}
            and a.estimated_diameter_km_max between {dia_max_min} and {dia_max_max}
            and ca.relative_velocity BETWEEN {vel_min} and {vel_max}
            and ca.astronomical BETWEEN {au_min} and {au_max}
            and a.is_potentially_hazardous_asteroid = {haz}
            and ca.close_approach_date BETWEEN '{start}' and '{end}'
            order by ca.close_approach_date asc
            """

            cursor.execute(filter_query)
            results = cursor.fetchall()
            df = pd.DataFrame(results)

            if df.empty:
                st.warning("No data found for the applied filters.")
            else:
                st.success("Filtered data displayed below:")
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Error running filter: {e}")   
        finally:
            if 'conn' in locals():
                conn.close()     