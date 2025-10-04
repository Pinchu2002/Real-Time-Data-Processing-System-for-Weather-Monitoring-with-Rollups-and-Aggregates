# Real-Time Weather Monitoring System

This project is a web-based weather application that retrieves and displays real-time weather data and forecasts for cities around the world. It is built with Flask and leverages the OpenWeatherMap API for data retrieval. The application features a clean, responsive user interface for displaying current weather, 5-day forecasts, and insightful visualizations. It also includes a backend alerting system for monitoring weather conditions.

## Features

- **Real-Time Weather Data:** Get current weather information for any city, including temperature, humidity, and wind speed.
- **5-Day Forecast:** View a 5-day weather forecast with 3-hour intervals.
- **Unit Conversion:** Switch between Celsius, Fahrenheit, and Kelvin.
- **Weather Visualizations:**
    - **Weekly Summary:** A summary of the last 7 days of weather data.
    - **Forecast Plot:** A visual representation of the 5-day forecast.
    - **Temperature Heatmap:** An hourly temperature heatmap for the last 7 days.
- **Expandable Graphs:** Click on any graph to view a larger, more detailed version.
- **Alerting System:** A backend system to check for and log weather alerts based on configurable thresholds.
- **Responsive UI:** A clean and modern user interface that works on both desktop and mobile devices.
- **Error Handling:** User-friendly error handling for invalid or unknown city names.

## Technology Stack

- **Backend:**
    - Python
    - Flask
    - SQLAlchemy (for database interaction)
    - Alembic (for database migrations)
- **Frontend:**
    - HTML
    - CSS
    - JavaScript
- **Database:**
    - SQLite (default)
- **APIs:**
    - OpenWeatherMap API
- **Deployment:**
    - Docker, Docker Compose (optional)

## Architecture Overview

The application follows a standard Flask web application structure:

- **`run.py`:** The main entry point of the application.
- **`app/`:** The main application package.
    - **`__init__.py`:** Initializes the Flask app, extensions, and database.
    - **`routes.py` (implicitly in `run.py`):** Defines the application's routes and view functions.
    - **`models.py`:** Defines the database schema using SQLAlchemy.
    - **`data_retrieval.py`:** Handles communication with the OpenWeatherMap API.
    - **`data_processing.py`:** Performs data aggregation and processing.
    - **`visualizations.py`:** Generates plots and graphs.
    - **`alerting.py`:** Contains the logic for the weather alerting system.
    - **`config.py`:** Manages application configuration.
- **`templates/`:** Contains the HTML templates for the frontend.
- **`static/`:** Contains static assets like CSS, JavaScript, and images.

## File Structure

```
Real-Time-Data-Processing-System-for-Weather-Monitoring-with-Rollups-and-Aggregates
├── app
│   ├── __init__.py
│   ├── alerting.py
│   ├── config.py
│   ├── data_processing.py
│   ├── data_retrieval.py
│   ├── models.py
│   ├── visualizations.py
├── apikey.txt
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run.py
├── static
│   └── styles.css
├── templates
│   └── index.html
└── tests
    └── test_data_retrieval.py
```

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- pip
- An OpenWeatherMap API key

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/Real-Time-Data-Processing-System-for-Weather-Monitoring-with-Rollups-and-Aggregates.git
    cd Real-Time-Data-Processing-System-for-Weather-Monitoring-with-Rollups-and-Aggregates
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the API key:**
    Create a file named `apikey.txt` in the root directory of the project and paste your OpenWeatherMap API key into it.

5.  **Run the application:**
    ```bash
    python run.py
    ```
    The application will be available at `http://127.0.0.1:5000`.

## How It Works

### Data Retrieval

- The `WeatherRetriever` class in `app/data_retrieval.py` is responsible for fetching data from the OpenWeatherMap API.
- It has methods for getting both current weather (`get_weather_data`) and forecast data (`get_weather_forecast`).
- API responses are handled with error checking, including for unknown cities (404 errors).

### Data Processing and Storage

- Fetched weather data is processed in the `/weather` route in `run.py`.
- The `save_weather_data` method in `WeatherRetriever` saves the data to the SQLite database.
- The `WeatherData` model in `app/models.py` defines the structure of the `weather_data` table.
- The `data_processing.py` file contains functions for aggregating data for visualizations, such as `daily_weather_summary` and `get_hourly_data`.

### Visualizations

- The `app/visualizations.py` module uses Matplotlib and Seaborn to generate plots.
- `plot_weather_summary`: Creates a 7-day summary plot.
- `plot_forecast`: Creates a 5-day forecast plot.
- `plot_heatmap`: Creates an hourly temperature heatmap for the last 7 days.
- The generated plots are saved as images in the `static/plots` directory.

### Alerting

- The `check_alerts` function in `app/alerting.py` checks for weather conditions that exceed a configured threshold for a consecutive number of readings.
- The `send_alert_notification` function is a placeholder for sending notifications (e.g., email, SMS).

### Frontend

- The frontend is a single-page application powered by vanilla JavaScript.
- When the user enters a city and clicks "Search", a POST request is made to the `/weather` endpoint.
- The JSON response is then used to dynamically update the UI with the weather data and visualization paths.
- The expandable graph feature is implemented using a modal window.

## API Endpoints

- **`POST /weather`**
    - **Description:** Fetches weather data for a given city.
    - **Request Body:**
        - `city` (string, required): The name of the city.
        - `unit` (string, required): The unit for temperature (`Celsius`, `Fahrenheit`, or `Kelvin`).
    - **Success Response (200):**
        - A JSON object containing current weather, forecast data, and paths to visualizations.
    - **Error Responses:**
        - `400 Bad Request`: If `city` or `unit` is missing.
        - `404 Not Found`: If the city is not found.
        - `500 Internal Server Error`: For other server-side errors.

## Configuration

The application can be configured via `app/config.py` or by setting environment variables.

- `SQLALCHEMY_DATABASE_URI`: The database connection string.
- `OPENWEATHERMAP_API_KEY`: Your OpenWeatherMap API key.
- `ALERT_THRESHOLD_TEMP`: The temperature threshold for alerts (in Celsius).
- `ALERT_CONSECUTIVE_COUNT`: The number of consecutive readings required to trigger an alert.

## Running Tests

To run the included tests, use the following command:

```bash
python -m unittest discover -s tests
```

## Future Enhancements

- **Implement `send_alert_notification`:** Integrate a real notification service (e.g., SendGrid for email, Twilio for SMS).
- **More Visualizations:** Add more types of graphs, such as wind direction plots or precipitation charts.
- **User Accounts:** Allow users to create accounts to save their favorite cities.
- **Geolocation:** Automatically detect the user's location to show local weather.
- **Database Choice:** Add support for other databases like PostgreSQL or MySQL for production environments.
