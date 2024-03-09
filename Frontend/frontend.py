import psycopg2
import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly
import streamlit as st
import time
import os

port = int(os.environ.get("PORT", 8088))

def connect_database():
    conn = psycopg2.connect(
        host='/cloudsql/msds432-cbi:us-central1:cbipostgres',
        database='chicago_business_intelligence',
        user='postgres',
        password='root'
    )
    return conn
def check_database():
    try:
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("SELECT EXISTS (SELECT 1 FROM taxi_trips LIMIT 1);")
        exists = cursor.fetchone()[0]
        conn.close()
        return exists
    except Exception as e:
        print(e)
        return False
        
@st.cache
def get_taxi():
    conn = connect_database()
    cursor = conn.cursor()
    
    sql = "SELECT * FROM taxi_trips;"
    
    cursor.execute(sql)
    taxi_trips = cursor.fetchall()
    
    columns = [d[0] for d in cursor.description]
    taxi_df = pd.DataFrame(taxi_trips, columns=columns)
    
    #Trip dates also have time info. Create a field just for the date.
    taxi_df['trip_date'] = taxi_df['trip_start_timestamp'].dt.date
    taxi_df['trip_year'] = taxi_df['trip_start_timestamp'].dt.year
    taxi_df['trip_month'] = taxi_df['trip_start_timestamp'].dt.month
    taxi_df['trip_day'] = taxi_df['trip_start_timestamp'].dt.day
    taxi_df['trip_week'] = taxi_df['trip_start_timestamp'].dt.weekofyear
    taxi_df['trip_dow'] = taxi_df['trip_start_timestamp'].dt.dayofweek
    
    return taxi_df

# Function to create and fit the model based of zip code subset and num of days from user input
def create_forecast(taxi_df, periods=60):
    daily_trip_count = taxi_df.groupby(['trip_start_timestamp'])['trip_id'].count().reset_index(name='total_trips')
    daily_trip_count = daily_trip_count.rename(columns={'trip_start_timestamp':'ds', 'total_trips':'y'})   
    daily_trip_count['ds'] = daily_trip_count['ds'].dt.tz_localize(None)
    model = Prophet(daily_seasonality=True, weekly_seasonality=True)
    model.fit(daily_trip_count)
    future_dates = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future_dates)
    return model, forecast
   
def main():
    # Main page
    st.title('Taxi Trip Forecasting')
    
    if not check_database():
        # If data is not available, display a waiting message and rerun the check after some time
        st.warning('Waiting for data to be available. Please wait...')
        # Delay for a certain amount of time before checking again
        time.sleep(30)  # Adjust sleep time as needed
        st.experimental_rerun()
        
     
    taxi_df = get_taxi()
    # Sidebar for user input:
    st.sidebar.title("Traffic Forecasting Settings")
    # Get the list of unique zip codes from the dataframe, with 'All' option added
    zip_codes = ['All'] + sorted(taxi_df['pickup_zip_code'].unique().tolist())
    selected_zip_code = st.sidebar.selectbox("Select Zip Code for Forecasting", zip_codes, index=0)
    periods_input = st.sidebar.number_input('How many days to forecast?', min_value=30, max_value=365, value=60, step=1)

    # Filter data based on selected zip code, if not 'All'
    if selected_zip_code != 'All':
        slice_for_zip_code = taxi_df.loc[taxi_df['pickup_zip_code'] == selected_zip_code]
    else:
        slice_for_zip_code = taxi_df.copy()
        
    # Generate the forecast plot
    model, forecast = create_forecast(slice_for_zip_code, periods=periods_input)
    st.title(f"Forecast for Zip Code: {selected_zip_code}")
    fig_forecast = plot_plotly(model, forecast)
    st.plotly_chart(fig_forecast, use_container_width=True)
        

    # Generate the components plot
    st.title("Forecast Components")
    fig_components = plot_components_plotly(model, forecast)
    st.plotly_chart(fig_components, use_container_width=True)
    
if __name__ == "__main__":
    main()