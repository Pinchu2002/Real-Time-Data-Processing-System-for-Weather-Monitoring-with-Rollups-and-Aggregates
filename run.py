from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
import os
from pathlib import Path
from requests.exceptions import HTTPError

from app.data_retrieval import WeatherRetriever
from app.config import Config
from app.visualizations import plot_weather_summary, plot_forecast, plot_heatmap
from app import create_app, db

# Create the Flask application
app = create_app()
app.config['UPLOAD_FOLDER'] = 'static/plots'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

API_KEY = Config.OPENWEATHERMAP_API_KEY

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def weather():
    city = request.form.get('city')
    unit = request.form.get('unit')

    if not city:
        return jsonify({'error': 'City cannot be blank.'}), 400
    if not unit:
        return jsonify({'error': 'Unit is required.'}), 400

    try:
        # Initialize weather retriever
        weather_retriever = WeatherRetriever(API_KEY, [city], 0)
        
        # Fetch current weather (always get in metric to ensure consistent conversion)
        weather_response = weather_retriever.get_weather_data(city, 'metric')
        forecast_response = weather_retriever.get_weather_forecast(city, 'metric')
        
        # Save weather data to database (always save in metric)
        weather_retriever.save_weather_data(city, weather_response, 'metric')

        # Set unit symbol and convert temperature if needed
        unit = unit.lower()
        unit_symbol = '°C'
        
        # Convert temperature based on selected unit
        def convert_temp(temp, to_unit):
            if to_unit == 'kelvin':
                return temp + 273.15
            elif to_unit == 'fahrenheit':
                return (temp * 9/5) + 32
            return temp  # Default to Celsius

        # Prepare current weather data
        current_temp = weather_response['main']['temp']
        current_weather = {
            'temperature': round(convert_temp(current_temp, unit), 1),
            'description': weather_response['weather'][0]['description'],
            'humidity': weather_response['main']['humidity'],
            'wind_speed': weather_response['wind']['speed'],
            'icon': weather_response['weather'][0]['icon']
        }

        # Prepare forecast data
        forecast = []
        for entry in forecast_response.get('list', [])[:5]:  # Next 5 time points
            temp = entry['main']['temp']
            forecast.append({
                'date': entry['dt_txt'],
                'temperature': round(convert_temp(temp, unit), 1),
                'description': entry['weather'][0]['description'],
                'icon': entry['weather'][0]['icon']
            })

        # Set unit symbol for display
        if unit == 'kelvin':
            unit_symbol = 'K'
        elif unit == 'fahrenheit':
            unit_symbol = '°F'

        # Generate visualizations
        plot_paths = generate_visualizations(city)

        return jsonify({
            'city': city,
            'unit': unit_symbol,
            'current': current_weather,
            'forecast': forecast,
            'visualizations': plot_paths
        })

    except HTTPError as e:
        if e.response.status_code == 404:
            return jsonify({'error': f'City "{city}" not found. Please check the spelling.'}), 404
        else:
            app.logger.error(f"HTTP error while fetching weather for {city}: {str(e)}")
            return jsonify({'error': 'Could not retrieve weather data.'}), 500
    except Exception as e:
        app.logger.error(f"Error in weather route for {city}: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500

def generate_visualizations(city):
    """Generate visualizations for the given city and return their paths."""
    try:
        # Create a subdirectory for this city's visualizations
        city_slug = city.lower().replace(' ', '_')
        city_dir = os.path.join('static', 'plots', city_slug)
        os.makedirs(city_dir, exist_ok=True)
        
        # Generate and save visualizations
        plot_paths = {}
        
        # 1. Weather summary plot
        try:
            summary_plots = plot_weather_summary(save_dir=city_dir, days=7)
            if summary_plots:
                plot_paths['summary'] = url_for('static', filename=f"plots/{city_slug}/{os.path.basename(summary_plots[0])}")
        except Exception as e:
            app.logger.error(f"Error generating summary plot: {str(e)}")
        
        # 2. Forecast plot
        try:
            forecast_path = os.path.join(city_dir, 'forecast.png')
            if plot_forecast(city, forecast_path):
                plot_paths['forecast'] = url_for('static', filename=f"plots/{city_slug}/forecast.png")
        except Exception as e:
            app.logger.error(f"Error generating forecast plot: {str(e)}")
        
        # 3. Heatmap
        try:
            heatmap_path = os.path.join(city_dir, 'heatmap.png')
            if plot_heatmap(city, heatmap_path):
                plot_paths['heatmap'] = url_for('static', filename=f"plots/{city_slug}/heatmap.png")
        except Exception as e:
            app.logger.error(f"Error generating heatmap: {str(e)}")
        
        return plot_paths
        
    except Exception as e:
        app.logger.error(f"Error in generate_visualizations: {str(e)}")
        return {}

if __name__ == '__main__':
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
    app.run(debug=True)
