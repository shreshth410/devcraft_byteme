"""
Google Maps API Integration for Campus Copilot
"""

import logging
import requests
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import quote

logger = logging.getLogger(__name__)


class GoogleMapsService:
    """Google Maps API service for Campus Copilot"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Google Maps service"""
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api"
        
    def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """Geocode an address to get coordinates"""
        if not self.api_key:
            logger.warning("Google Maps API key not provided, using mock data")
            return self._mock_geocode(address)
            
        try:
            url = f"{self.base_url}/geocode/json"
            params = {
                'address': address,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                result = data['results'][0]
                location = result['geometry']['location']
                
                return {
                    'address': result['formatted_address'],
                    'latitude': location['lat'],
                    'longitude': location['lng'],
                    'place_id': result.get('place_id'),
                    'types': result.get('types', [])
                }
                
            return None
            
        except Exception as e:
            logger.error(f"Error geocoding address '{address}': {e}")
            return None
            
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Reverse geocode coordinates to get address"""
        if not self.api_key:
            logger.warning("Google Maps API key not provided, using mock data")
            return self._mock_reverse_geocode(latitude, longitude)
            
        try:
            url = f"{self.base_url}/geocode/json"
            params = {
                'latlng': f"{latitude},{longitude}",
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                result = data['results'][0]
                
                return {
                    'address': result['formatted_address'],
                    'latitude': latitude,
                    'longitude': longitude,
                    'place_id': result.get('place_id'),
                    'types': result.get('types', [])
                }
                
            return None
            
        except Exception as e:
            logger.error(f"Error reverse geocoding coordinates ({latitude}, {longitude}): {e}")
            return None
            
    def get_directions(self, origin: str, destination: str, mode: str = "walking") -> Optional[Dict[str, Any]]:
        """Get directions between two locations"""
        if not self.api_key:
            logger.warning("Google Maps API key not provided, using mock data")
            return self._mock_directions(origin, destination, mode)
            
        try:
            url = f"{self.base_url}/directions/json"
            params = {
                'origin': origin,
                'destination': destination,
                'mode': mode,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'OK' and data['routes']:
                route = data['routes'][0]
                leg = route['legs'][0]
                
                return {
                    'origin': leg['start_address'],
                    'destination': leg['end_address'],
                    'distance': leg['distance']['text'],
                    'duration': leg['duration']['text'],
                    'mode': mode,
                    'steps': self._format_steps(leg['steps']),
                    'overview_polyline': route['overview_polyline']['points']
                }
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting directions from '{origin}' to '{destination}': {e}")
            return None
            
    def search_nearby_places(self, location: str, place_type: str = "university", 
                           radius: int = 5000) -> List[Dict[str, Any]]:
        """Search for nearby places"""
        if not self.api_key:
            logger.warning("Google Maps API key not provided, using mock data")
            return self._mock_nearby_places(location, place_type)
            
        try:
            # First geocode the location
            geocoded = self.geocode_address(location)
            if not geocoded:
                return []
                
            url = f"{self.base_url}/place/nearbysearch/json"
            params = {
                'location': f"{geocoded['latitude']},{geocoded['longitude']}",
                'radius': radius,
                'type': place_type,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            places = []
            if data['status'] == 'OK':
                for place in data.get('results', []):
                    places.append({
                        'name': place.get('name'),
                        'address': place.get('vicinity'),
                        'rating': place.get('rating'),
                        'place_id': place.get('place_id'),
                        'types': place.get('types', []),
                        'latitude': place['geometry']['location']['lat'],
                        'longitude': place['geometry']['location']['lng'],
                        'open_now': place.get('opening_hours', {}).get('open_now'),
                    })
                    
            return places
            
        except Exception as e:
            logger.error(f"Error searching nearby places: {e}")
            return []
            
    def get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a place"""
        if not self.api_key:
            logger.warning("Google Maps API key not provided, using mock data")
            return self._mock_place_details(place_id)
            
        try:
            url = f"{self.base_url}/place/details/json"
            params = {
                'place_id': place_id,
                'fields': 'name,formatted_address,formatted_phone_number,website,rating,opening_hours,geometry',
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'OK':
                place = data['result']
                
                return {
                    'name': place.get('name'),
                    'address': place.get('formatted_address'),
                    'phone': place.get('formatted_phone_number'),
                    'website': place.get('website'),
                    'rating': place.get('rating'),
                    'latitude': place['geometry']['location']['lat'],
                    'longitude': place['geometry']['location']['lng'],
                    'opening_hours': place.get('opening_hours', {}).get('weekday_text', []),
                    'open_now': place.get('opening_hours', {}).get('open_now'),
                }
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting place details for {place_id}: {e}")
            return None
            
    def _format_steps(self, steps: List[Dict]) -> List[Dict[str, Any]]:
        """Format direction steps for display"""
        formatted_steps = []
        
        for step in steps:
            formatted_steps.append({
                'instruction': step['html_instructions'],
                'distance': step['distance']['text'],
                'duration': step['duration']['text'],
                'travel_mode': step.get('travel_mode', 'WALKING')
            })
            
        return formatted_steps
        
    def generate_maps_url(self, query: str) -> str:
        """Generate a Google Maps URL for a query"""
        encoded_query = quote(query)
        return f"https://www.google.com/maps/search/{encoded_query}"
        
    def generate_directions_url(self, origin: str, destination: str, mode: str = "walking") -> str:
        """Generate a Google Maps directions URL"""
        encoded_origin = quote(origin)
        encoded_destination = quote(destination)
        
        mode_map = {
            "driving": "driving",
            "walking": "walking",
            "transit": "transit",
            "bicycling": "bicycling"
        }
        
        maps_mode = mode_map.get(mode, "walking")
        return f"https://www.google.com/maps/dir/{encoded_origin}/{encoded_destination}/@?travelmode={maps_mode}"
        
    # Mock methods for when API key is not available
    def _mock_geocode(self, address: str) -> Dict[str, Any]:
        """Mock geocoding for demo purposes"""
        # Sample campus locations
        mock_locations = {
            "library": {"lat": 40.7589, "lng": -73.9851, "address": "Campus Library, University Ave"},
            "cafeteria": {"lat": 40.7591, "lng": -73.9849, "address": "Student Cafeteria, University Ave"},
            "gym": {"lat": 40.7587, "lng": -73.9853, "address": "Campus Gymnasium, University Ave"},
            "cs building": {"lat": 40.7593, "lng": -73.9847, "address": "Computer Science Building, University Ave"},
            "main hall": {"lat": 40.7590, "lng": -73.9850, "address": "Main Hall, University Ave"},
        }
        
        # Find closest match
        address_lower = address.lower()
        for key, location in mock_locations.items():
            if key in address_lower:
                return {
                    'address': location['address'],
                    'latitude': location['lat'],
                    'longitude': location['lng'],
                    'place_id': f"mock_place_id_{key}",
                    'types': ['establishment', 'university']
                }
                
        # Default location
        return {
            'address': f"Campus Location: {address}",
            'latitude': 40.7589,
            'longitude': -73.9851,
            'place_id': "mock_place_id_default",
            'types': ['establishment']
        }
        
    def _mock_reverse_geocode(self, lat: float, lng: float) -> Dict[str, Any]:
        """Mock reverse geocoding"""
        return {
            'address': f"Campus Location near ({lat:.4f}, {lng:.4f})",
            'latitude': lat,
            'longitude': lng,
            'place_id': "mock_place_id_reverse",
            'types': ['establishment']
        }
        
    def _mock_directions(self, origin: str, destination: str, mode: str) -> Dict[str, Any]:
        """Mock directions for demo purposes"""
        return {
            'origin': f"Campus: {origin}",
            'destination': f"Campus: {destination}",
            'distance': "0.3 miles",
            'duration': "6 mins",
            'mode': mode,
            'steps': [
                {
                    'instruction': f"Head towards {destination}",
                    'distance': "0.1 miles",
                    'duration': "2 mins",
                    'travel_mode': mode.upper()
                },
                {
                    'instruction': f"Continue straight to {destination}",
                    'distance': "0.2 miles",
                    'duration': "4 mins",
                    'travel_mode': mode.upper()
                }
            ],
            'overview_polyline': "mock_polyline_data"
        }
        
    def _mock_nearby_places(self, location: str, place_type: str) -> List[Dict[str, Any]]:
        """Mock nearby places search"""
        mock_places = [
            {
                'name': 'Campus Library',
                'address': 'University Ave',
                'rating': 4.5,
                'place_id': 'mock_library',
                'types': ['library', 'establishment'],
                'latitude': 40.7589,
                'longitude': -73.9851,
                'open_now': True
            },
            {
                'name': 'Student Center',
                'address': 'University Ave',
                'rating': 4.2,
                'place_id': 'mock_student_center',
                'types': ['establishment'],
                'latitude': 40.7591,
                'longitude': -73.9849,
                'open_now': True
            }
        ]
        
        return mock_places
        
    def _mock_place_details(self, place_id: str) -> Dict[str, Any]:
        """Mock place details"""
        return {
            'name': 'Campus Location',
            'address': 'University Ave, Campus',
            'phone': '(555) 123-4567',
            'website': 'https://university.edu',
            'rating': 4.3,
            'latitude': 40.7589,
            'longitude': -73.9851,
            'opening_hours': [
                'Monday: 8:00 AM – 10:00 PM',
                'Tuesday: 8:00 AM – 10:00 PM',
                'Wednesday: 8:00 AM – 10:00 PM',
                'Thursday: 8:00 AM – 10:00 PM',
                'Friday: 8:00 AM – 8:00 PM',
                'Saturday: 10:00 AM – 6:00 PM',
                'Sunday: 12:00 PM – 8:00 PM'
            ],
            'open_now': True
        }


def create_google_maps_service(api_key: Optional[str] = None) -> GoogleMapsService:
    """Factory function to create Google Maps service"""
    return GoogleMapsService(api_key)

