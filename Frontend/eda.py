import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly

def connect_database():
    conn = psycopg2.connect(
        host='localhost',
        database='chicago_business_intelligence',
        user='postgres',
        password='root'
    )
    return conn

def get_taxi(connection):
    cursor = connection.cursor()
    
    sql = "SELECT * FROM taxi_trips;"
    
    cursor.execute(sql)
    taxi_trips = cursor.fetchall()
    
    columns = [d[0] for d in cursor.description]
    taxi_df = pd.DataFrame(taxi_trips, columns=columns)
    
    return taxi_df

conn = connect_database()
taxi_df = get_taxi(conn)

#Trip dates also have time info. Create a field just for the date.
taxi_df['trip_date'] = taxi_df['trip_start_timestamp'].dt.date
taxi_df['trip_year'] = taxi_df['trip_start_timestamp'].dt.year
taxi_df['trip_month'] = taxi_df['trip_start_timestamp'].dt.month
taxi_df['trip_day'] = taxi_df['trip_start_timestamp'].dt.day
taxi_df['trip_week'] = taxi_df['trip_start_timestamp'].dt.weekofyear
taxi_df['trip_dow'] = taxi_df['trip_start_timestamp'].dt.dayofweek

print(taxi_df.head())


## EDA- show trip counts by pickup and dropoff  
pickup_zip_count = taxi_df.groupby(['pickup_zip_code'])['trip_id'].count().reset_index(name='total_trips')
dropoff_zip_count = taxi_df.groupby(['dropoff_zip_code'])['trip_id'].count().reset_index(name='total_trips')
zip_count = combined_data = pd.merge(pickup_zip_count, dropoff_zip_count, left_on='pickup_zip_code', right_on='dropoff_zip_code', how='outer')

zip_count.fillna(0, inplace=True)
zip_count.rename(columns={'pickup_zip_code':'zip_code', 'total_trips_x': 'total_trips_pickup', 'total_trips_y': 'total_trips_dropoff'}, inplace=True)
zip_count.drop(columns=['dropoff_zip_code'], inplace=True)
print(zip_count)

zip_plt = zip_count.plot.bar(x='zip_code', y=['total_trips_pickup', 'total_trips_dropoff'], rot=60, title='Total Trips by Zip Code in 2024')
plt.legend(['Pickup Trips', 'Dropoff Trips'])
#plt.show()

# Total number of trips per month
monthly_df = taxi_df.groupby(['trip_month', 'pickup_zip_code'])['taxi_id'].count().reset_index(name="total_trips_per_month")
print(monthly_df)

# Time series for trip pickups in 60666
slice_for_zip_code = taxi_df.loc[taxi_df['pickup_zip_code'] == "60666"]
daily_trip_count_60666 = slice_for_zip_code.groupby(['trip_date'])['trip_id'].count().reset_index(name='total_trips')
fig = px.line(daily_trip_count_60666, x='trip_date', y='total_trips')
fig.update_layout(title_text='Time Series of daily trip counts for zip code: 60666')
#fig.show()
#print(trip_count)

daily_trip_count = taxi_df.groupby(['trip_date'])['trip_id'].count().reset_index(name='total_trips')
daily_trip_count = daily_trip_count.rename(columns={'trip_date':'ds', 'total_trips':'y'})   

model = Prophet(daily_seasonality=True, weekly_seasonality=True, yearly_seasonality=True)
model.fit(daily_trip_count)
future_dates = model.make_future_dataframe(periods=60)
forecast = model.predict(future_dates)
    
# Generate the overall forecast plot
fig_forecast = plot_plotly(model, forecast)
fig_forecast.show()

# Generate the forecast components plot
fig_components = plot_components_plotly(model, forecast)
fig_components.show()