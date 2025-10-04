from flask import current_app
from app import db
from app.models import WeatherData
from datetime import datetime
import requests

class WeatherRetriever:
    def __init__(self, api_key, cities, interval):
        self.api_key = api_key
        self.cities = cities
        self.interval = interval
        self.api_url = "https://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast"

    def get_weather_data(self, city, unit='metric'):
        """
        Get current weather data for a city.
        
        Args:
            city (str): City name
            unit (str): Unit of measurement ('metric', 'imperial', or 'standard')
            
        Returns:
            dict: Weather data in the requested unit
        """
        params = {
            'q': city,
            'appid': self.api_key,
            'units': unit  # This will return temperature in the requested unit
        }
        response = requests.get(self.api_url, params=params)
        response.raise_for_status()
        return response.json()

    def get_weather_forecast(self, city, unit='metric'):
        """
        Get weather forecast for a city.
        
        Args:
            city (str): City name
            unit (str): Unit of measurement ('metric', 'imperial', or 'standard')
            
        Returns:
            dict: Forecast data in the requested unit
        """
        params = {
            'q': city,
            'appid': self.api_key,
            'units': unit  # This will return temperature in the requested unit
        }
        response = requests.get(self.forecast_url, params=params)
        response.raise_for_status()
        return response.json()

    def save_weather_data(self, city, data, unit='metric'):
        """
        Save weather data to the database.
        
        Args:
            city (str): City name
            data (dict): Weather data from the API
            unit (str): Unit of measurement used in the data
        """
        try:
            # Convert temperature to Kelvin if needed
            temp = data['main']['temp']
            if unit == 'metric':  # Celsius to Kelvin
                temp_kelvin = temp + 273.15
            elif unit == 'imperial':  # Fahrenheit to Kelvin
                temp_kelvin = (temp - 32) * 5/9 + 273.15
            else:  # Already in Kelvin
                temp_kelvin = temp
            
            # Get weather description (first weather condition)
            weather_main = data['weather'][0]['main'] if data.get('weather') else None
            
            weather = WeatherData(
                city=city,
                main=weather_main,
                temp=temp_kelvin,  # Always store in Kelvin
                feels_like=data['main'].get('feels_like', temp_kelvin),  # Default to temp if not available
                humidity=data['main'].get('humidity'),
                wind_speed=data['wind'].get('speed'),
                timestamp=datetime.utcnow()
            )
            db.session.add(weather)
            db.session.commit()
            return True
        except Exception as e:
            current_app.logger.error(f"Error saving weather data for {city}: {str(e)}")
            db.session.rollback()
            return False
