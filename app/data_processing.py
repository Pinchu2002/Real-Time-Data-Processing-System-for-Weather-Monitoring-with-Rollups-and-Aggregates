import pandas as pd
from datetime import datetime, timedelta
import logging
from app import db
from app.models import WeatherData
from app.data_retrieval import WeatherRetriever
from app.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def daily_weather_summary(days: int = 7):
    """
    Generate daily weather summary statistics for visualization.
    
    Args:
        days: Number of days of historical data to include
        
    Returns:
        DataFrame with columns: City, Date, Average_Temperature, Maximum_Temperature,
        Minimum_Temperature, Average_Humidity, Average_Wind_Speed
    """
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query data from database
        data = WeatherData.query.filter(
            WeatherData.timestamp >= start_date,
            WeatherData.timestamp <= end_date
        ).all()
        
        if not data:
            logger.warning("No weather data found in the database")
            return pd.DataFrame()  # Return empty DataFrame instead of None
            
        # Convert to DataFrame
        records = []
        for entry in data:
            records.append({
                'City': entry.city,
                'Date': entry.timestamp.date(),
                'Temperature': entry.temp,
                'Humidity': entry.humidity,
                'Wind_Speed': entry.wind_speed
            })
            
        df = pd.DataFrame(records)
        
        # Group by city and date
        summary = df.groupby(['City', 'Date']).agg({
            'Temperature': ['mean', 'min', 'max'],
            'Humidity': 'mean',
            'Wind_Speed': 'mean'
        }).reset_index()
        
        # Flatten column names
        summary.columns = ['_'.join(col).strip('_') for col in summary.columns.values]
        
        # Rename columns for consistency
        summary = summary.rename(columns={
            'City_': 'City',
            'Date_': 'Date',
            'Temperature_mean': 'Average_Temperature',
            'Temperature_min': 'Minimum_Temperature',
            'Temperature_max': 'Maximum_Temperature',
            'Humidity_mean': 'Average_Humidity',
            'Wind_Speed_mean': 'Average_Wind_Speed'
        })
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generating daily weather summary: {str(e)}")
        return pd.DataFrame()

def get_hourly_data(city: str, days: int = 7) -> pd.DataFrame:
    """
    Fetch hourly weather data for a specific city for the last N days.
    
    Args:
        city: The city to fetch data for.
        days: The number of past days to fetch data for.
        
    Returns:
        A DataFrame with hourly temperature data.
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        data = WeatherData.query.filter(
            WeatherData.city == city,
            WeatherData.timestamp >= start_date,
            WeatherData.timestamp <= end_date
        ).all()
        
        if not data:
            logger.warning(f"No hourly data found for {city}")
            return pd.DataFrame()
            
        records = [{
            'timestamp': entry.timestamp,
            'temp': entry.temp
        } for entry in data]
        
        df = pd.DataFrame(records)
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.day_name()
        
        return df
        
    except Exception as e:
        logger.error(f"Error fetching hourly data for {city}: {str(e)}")
        return pd.DataFrame()

def forecast_summary(city: str = None):
    """
    Generate forecast summary for visualization.
    
    Args:
        city: Optional city filter
        
    Returns:
        DataFrame with forecast data including temperature, humidity, etc.
    """
    try:
        if not city:
            logger.warning("City is required for forecast summary")
            return pd.DataFrame()

        weather_retriever = WeatherRetriever(Config.OPENWEATHERMAP_API_KEY, [city], 0)
        forecast_response = weather_retriever.get_weather_forecast(city, 'metric')

        if not forecast_response or 'list' not in forecast_response:
            logger.warning(f"No forecast data available for {city}")
            return pd.DataFrame()

        forecast = []
        for entry in forecast_response['list']:
            forecast.append({
                'datetime': datetime.fromtimestamp(entry['dt']),
                'temp': entry['main']['temp'],
                'temp_min': entry['main']['temp_min'],
                'temp_max': entry['main']['temp_max'],
                'humidity': entry['main']['humidity'],
                'weather_description': entry['weather'][0]['description']
            })
        
        return pd.DataFrame(forecast)
            
    except Exception as e:
        logger.error(f"Error generating forecast summary: {str(e)}")
        return pd.DataFrame()