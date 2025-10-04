import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

# Set the backend before importing pyplot
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.dates import DateFormatter
import numpy as np
from flask import current_app

from app.data_processing import daily_weather_summary, forecast_summary, get_hourly_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set style - using a more reliable approach
plt.style.use('default')  # Start with default style
sns.set_style("whitegrid")  # Use seaborn's whitegrid style
sns.set_palette("husl")  # Set color palette

# Update rcParams for better default styling
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 16

def plot_weather_summary(save_dir: str = None, days: int = 7) -> List[str]:
    """
    Generate and optionally save weather summary plots for each city.
    
    Args:
        save_dir: Directory to save the plots. If None, displays the plots.
        days: Number of days of historical data to include.
        
    Returns:
        List of file paths where plots were saved, or None if displayed.
    """
    try:
        # Ensure save directory exists
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)
            
        # Get data
        summary = daily_weather_summary()
        if summary is None or summary.empty:
            logger.warning("No data available for visualization")
            return []
            
        # Filter by date if needed
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            summary = summary[pd.to_datetime(summary['Date']) >= cutoff_date]
        
        saved_files = []
        
        # Generate plots for each city
        for city in summary['City'].unique():
            city_data = summary[summary['City'] == city].sort_values('Date')
            
            # Create figure with subplots
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 16), 
                                              gridspec_kw={'height_ratios': [3, 1, 1]})
            
            # Plot 1: Temperature trends
            ax1.plot(city_data['Date'], city_data['Average_Temperature'], 
                    'b-', label='Average', marker='o')
            ax1.fill_between(city_data['Date'], 
                           city_data['Minimum_Temperature'],
                           city_data['Maximum_Temperature'],
                           color='blue', alpha=0.1)
            ax1.set_title(f'{city} - Temperature Trends', fontsize=14, pad=20)
            ax1.set_ylabel('Temperature (°C)')
            ax1.grid(True, linestyle='--', alpha=0.6)
            ax1.legend()
            
            # Format x-axis dates
            date_format = DateFormatter('%m-%d')
            ax1.xaxis.set_major_formatter(date_format)
            
            # Plot 2: Humidity
            ax2.bar(city_data['Date'], city_data['Average_Humidity'], 
                   color='green', alpha=0.6, width=0.8)
            ax2.set_ylabel('Humidity (%)')
            ax2.grid(True, linestyle='--', alpha=0.6, axis='y')
            ax2.xaxis.set_major_formatter(date_format)
            
            # Plot 3: Wind Speed
            ax3.bar(city_data['Date'], city_data['Average_Wind_Speed'], 
                   color='purple', alpha=0.6, width=0.8)
            ax3.set_ylabel('Wind Speed (m/s)')
            ax3.set_xlabel('Date')
            ax3.grid(True, linestyle='--', alpha=0.6, axis='y')
            ax3.xaxis.set_major_formatter(date_format)
            
            # Rotate x-axis labels
            plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
            plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
            plt.setp(ax3.get_xticklabels(), rotation=45, ha='right')
            
            plt.tight_layout()
            
            # Save or show
            if save_dir:
                filename = os.path.join(save_dir, f"{city.lower().replace(' ', '_')}_summary.png")
                plt.savefig(filename, dpi=300, bbox_inches='tight')
                saved_files.append(filename)
                plt.close()
            
        return saved_files if save_dir else None
        
    except Exception as e:
        logger.error(f"Error generating weather summary plots: {str(e)}", exc_info=True)
        return []

def plot_forecast(city: str, save_path: str = None) -> Optional[str]:
    """
    Generate forecast visualization for a specific city.
    
    Args:
        city: Name of the city
        save_path: Path to save the plot. If None, displays the plot.
        
    Returns:
        Path to the saved file if saved, None if displayed.
    """
    try:
        forecast = forecast_summary(city)
        if forecast is None or forecast.empty:
            logger.warning(f"No forecast data available for {city}")
            return None
            
        fig, ax1 = plt.subplots(figsize=(14, 8))
        
        # Temperature plot
        ax1.plot(forecast['datetime'], forecast['temp'], 'r-', label='Temperature (°C)')
        ax1.fill_between(forecast['datetime'], 
                        forecast['temp_min'], 
                        forecast['temp_max'], 
                        color='red', alpha=0.1)
        
        ax1.set_xlabel('Date/Time')
        ax1.set_ylabel('Temperature (°C)', color='r')
        ax1.tick_params(axis='y', labelcolor='r')
        
        # Add humidity as bars on secondary y-axis
        ax2 = ax1.twinx()
        ax2.bar(forecast['datetime'], forecast['humidity'], 
               alpha=0.3, color='blue', width=0.02, label='Humidity (%)')
        ax2.set_ylabel('Humidity (%)', color='b')
        ax2.tick_params(axis='y', labelcolor='b')
        
        # Add weather description as text
        for i, row in forecast.iterrows():
            ax1.text(row['datetime'], row['temp_max'] + 1, 
                   row['weather_description'], 
                   rotation=45, ha='right', fontsize=8)
        
        plt.title(f'Weather Forecast for {city}')
        fig.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            plt.show()
            return None
            
    except Exception as e:
        logger.error(f"Error generating forecast plot: {str(e)}", exc_info=True)
        return None

def plot_heatmap(city: str, save_path: str = None) -> Optional[str]:
    """
    Generate a heatmap of temperature patterns for a city.
    
    Args:
        city: Name of the city
        save_path: Path to save the plot. If None, displays the plot.
        
    Returns:
        Path to the saved file if saved, None if displayed.
    """
    try:
        hourly_data = get_hourly_data(city, days=7)
        if hourly_data.empty:
            logger.warning(f"No hourly data for heatmap for city {city}")
            return None

        # Pivot data for heatmap
        heatmap_data = hourly_data.pivot_table(
            index='day_of_week',
            columns='hour',
            values='temp',
            aggfunc='mean'
        )

        # Order days of the week
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = heatmap_data.reindex(days_order)

        plt.figure(figsize=(16, 8))
        sns.heatmap(heatmap_data, cmap='coolwarm', annot=True, fmt=".1f",
                    cbar_kws={'label': 'Temperature (°C)'})
        
        plt.title(f'Hourly Temperature Patterns - {city}')
        plt.xlabel('Hour of Day')
        plt.ylabel('Day of Week')
        plt.xticks(rotation=0)
        plt.yticks(rotation=0)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            plt.show()
            return None
            
    except Exception as e:
        logger.error(f"Error generating heatmap: {str(e)}", exc_info=True)
        return None

# Example usage
if __name__ == "__main__":
    # Create visualizations for all cities
    plot_weather_summary(save_dir="static/plots")
    
    # Example for a specific city
    # plot_forecast("New York", "static/plots/ny_forecast.png")
    # plot_heatmap("New York", "static/plots/ny_heatmap.png")
