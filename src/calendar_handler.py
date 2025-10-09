"""
Calendar Handler - Port/Adapter pattern for calendar integration
Local JSON stub for testing, designed for Google Calendar integration
"""

import json
import os
import logging
from datetime import date, datetime, timedelta
from typing import Protocol, List, Dict, Any, runtime_checkable

logger = logging.getLogger(__name__)

@runtime_checkable
class CalendarPort(Protocol):
    """
    Port interface for calendar operations
    Allows for different calendar implementations (Google, Outlook, etc.)
    """
    
    def find_slots(self, service: str, day: date) -> List[Dict[str, Any]]:
        """
        Find available time slots for a service on a given day
        
        Args:
            service: Service type (e.g., 'haircut', 'styling')
            day: Date to check availability
            
        Returns:
            List of available slots with time and metadata
        """
        ...
    
    def book(self, name: str, service: str, start_iso: str) -> Dict[str, Any]:
        """
        Book an appointment
        
        Args:
            name: Customer name
            service: Service type
            start_iso: Start time in ISO format
            
        Returns:
            Booking confirmation with details
        """
        ...

class GoogleCalendarAdapter(CalendarPort):
    """
    Adapter for Google Calendar integration
    Currently uses local JSON file as stub for testing
    
    TODO: Implement actual Google Calendar API integration
    - Set up OAuth2 authentication
    - Connect to Google Calendar API
    - Handle real availability checking
    - Create actual calendar events
    """
    
    def __init__(self, data_file: str = "data/appointments.json"):
        self.data_file = data_file
        self._ensure_data_file()
        logger.info(f"Google Calendar adapter initialized with data file: {self.data_file}")
    
    def _ensure_data_file(self) -> None:
        """Ensure the data file exists and is properly formatted"""
        data_dir = os.path.dirname(self.data_file)
        if data_dir:  # Only create directory if there is one
            os.makedirs(data_dir, exist_ok=True)
        if not os.path.exists(self.data_file):
            initial_data = {
                "appointments": [],
                "availability": {
                    "monday": ["9:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
                    "tuesday": ["9:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
                    "wednesday": ["9:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
                    "thursday": ["9:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
                    "friday": ["9:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
                    "saturday": ["9:00", "10:00", "11:00", "13:00"],
                    "sunday": []
                }
            }
            with open(self.data_file, 'w') as f:
                json.dump(initial_data, f, indent=2)
            logger.info(f"Created initial data file: {self.data_file}")
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file"""
        if os.getenv('TEST_MODE') != 'true':
            logger.warning("GoogleCalendarAdapter using local file in non-test mode")
        
        try:
            with open(self.data_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    self._ensure_data_file()
                    with open(self.data_file, 'r') as f:
                        return json.load(f)
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading data file: {e}")
            self._ensure_data_file()
            with open(self.data_file, 'r') as f:
                return json.load(f)
    
    def _save_data(self, data: Dict[str, Any]) -> None:
        """Save data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving data file: {e}")
            raise
    
    def find_slots(self, service: str, day: date) -> List[Dict[str, Any]]:
        """
        Find available slots for a service on a given day
        
        TODO: Replace with actual Google Calendar API calls
        - Query real calendar availability
        - Handle timezone conversions
        - Check for conflicts with existing events
        - Respect business rules and service durations
        """
        data = self._load_data()
        day_name = day.strftime('%A').lower()
        
        # Get base availability for the day
        base_slots = data.get('availability', {}).get(day_name, [])
        
        # Get existing appointments for the day
        existing_appointments = [
            apt for apt in data.get('appointments', [])
            if apt.get('date') == day.isoformat()
        ]
        
        # Remove booked slots
        booked_times = {apt.get('time') for apt in existing_appointments}
        available_slots = []
        
        for time_slot in base_slots:
            if time_slot not in booked_times:
                available_slots.append({
                    'time': time_slot,
                    'date': day.isoformat(),
                    'service': service,
                    'duration_minutes': 60,  # Default duration
                    'available': True
                })
        
        logger.info(f"Found {len(available_slots)} available slots for {service} on {day}")
        return available_slots
    
    def book(self, name: str, service: str, start_iso: str) -> Dict[str, Any]:
        """
        Book an appointment
        
        TODO: Replace with actual Google Calendar API calls
        - Create real calendar event
        - Send confirmation emails
        - Handle timezone properly
        - Generate actual confirmation codes
        """
        try:
            # Parse the ISO datetime
            start_dt = datetime.fromisoformat(start_iso.replace('Z', '+00:00'))
            date_str = start_dt.date().isoformat()
            time_str = start_dt.strftime('%H:%M')
            
            # Load current data
            data = self._load_data()
            
            # Generate confirmation code
            import uuid
            confirmation_code = str(uuid.uuid4())[:8].upper()
            
            # Create appointment record
            appointment = {
                'id': len(data.get('appointments', [])) + 1,
                'name': name,
                'service': service,
                'date': date_str,
                'time': time_str,
                'start_iso': start_iso,
                'confirmation_code': confirmation_code,
                'status': 'confirmed',
                'created_at': datetime.now().isoformat()
            }
            
            # Add to appointments
            if 'appointments' not in data:
                data['appointments'] = []
            data['appointments'].append(appointment)
            
            # Save data
            self._save_data(data)
            
            logger.info(f"Booked appointment for {name}: {service} on {date_str} at {time_str}")
            
            return {
                'success': True,
                'confirmation_code': confirmation_code,
                'appointment': appointment
            }
            
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def book_appointment(self, name: str, service: str, date_time: datetime, phone: str = None, email: str = None) -> Dict[str, Any]:
        """
        Convenience method for booking with datetime object
        Delegates to the main book method with ISO format
        
        Args:
            name: Customer name
            service: Service type (e.g., "haircut")
            date_time: Appointment datetime
            phone: Customer phone (optional)
            email: Customer email (optional)
            
        Returns:
            Booking result dictionary
        """
        return self.book(name, service, date_time.isoformat())

def ensure_data_file(data_file: str = "data/appointments.json") -> None:
    """
    Ensure the appointments data file exists and is properly initialized
    
    Args:
        data_file: Path to the data file
    """
    adapter = GoogleCalendarAdapter(data_file)
    logger.info(f"Data file ensured: {data_file}")

def get_calendar_adapter() -> CalendarPort:
    """
    Factory function to get appropriate calendar adapter
    
    Returns:
        CalendarPort implementation based on environment
    """
    # TODO: Add logic to choose implementation based on:
    # - Environment variables (GOOGLE_CALENDAR_CREDENTIALS, etc.)
    # - Feature flags
    # - Service availability
    
    return GoogleCalendarAdapter()