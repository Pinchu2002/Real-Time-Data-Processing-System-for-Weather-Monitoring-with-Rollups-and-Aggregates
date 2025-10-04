from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional
from itertools import groupby
from operator import itemgetter

from app import app, db
from app.models import WeatherData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_alerts(threshold: Optional[float] = None, 
                consecutive_count: Optional[int] = None,
                time_window_hours: int = 24) -> List[Dict]:
    """
    Check for weather alerts based on temperature thresholds.
    
    Args:
        threshold: Temperature threshold in Celsius. If None, uses value from app config.
        consecutive_count: Number of consecutive readings above threshold to trigger alert.
                         If None, uses value from app config.
        time_window_hours: Look back period in hours for checking alerts.
        
    Returns:
        List of alert dictionaries with city, current_temp, threshold, 
        consecutive_count, and timestamps of violations.
    """
    try:
        # Get configuration
        threshold = threshold or app.config.get('ALERT_THRESHOLD_TEMP', 30.0)
        consecutive = consecutive_count or app.config.get('ALERT_CONSECUTIVE_COUNT', 3)
        
        # Calculate time window
        time_threshold = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        # Query recent data, ordered for groupby
        results = db.session.query(
            WeatherData.city, 
            WeatherData.temp, 
            WeatherData.timestamp
        ).filter(
            WeatherData.timestamp >= time_threshold
        ).order_by(
            WeatherData.city,
            WeatherData.timestamp.asc()
        ).all()
        
        if not results:
            logger.info("No weather data found in the specified time window.")
            return []
        
        alerts = []
        # Group results by city
        for city, group in groupby(results, key=itemgetter(0)):
            consecutive_violations = 0
            violation_timestamps = []
            last_temp = None

            for _, temp, timestamp in group:
                if temp > threshold:
                    consecutive_violations += 1
                    violation_timestamps.append(timestamp.isoformat())
                else:
                    # Reset if a reading is below the threshold
                    consecutive_violations = 0
                    violation_timestamps = []
                
                last_temp = temp

            if consecutive_violations >= consecutive:
                alerts.append({
                    'city': city,
                    'current_temp': last_temp,
                    'threshold': threshold,
                    'consecutive_count': consecutive_violations,
                    'violation_timestamps': violation_timestamps,
                    'message': (
                        f"{city} has exceeded {threshold}°C "
                        f"for {consecutive_violations} consecutive readings"
                    )
                })

        # Log alerts
        for alert in alerts:
            logger.warning(alert['message'])
            
        return alerts
        
    except Exception as e:
        logger.error(f"Error checking alerts: {str(e)}", exc_info=True)
        raise

def send_alert_notification(alert: Dict) -> bool:
    """
    Send alert notification (placeholder for actual notification logic).
    
    Args:
        alert: Alert dictionary with alert details
        
    Returns:
        bool: True if notification was sent successfully
    """
    try:
        # TODO: Implement actual notification (email, SMS, webhook, etc.)
        print(f"ALERT: {alert['message']}")
        return True
    except Exception as e:
        logger.error(f"Failed to send alert notification: {str(e)}")
        return False
