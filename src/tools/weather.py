"""
Weather tool for AI Agent
"""
import aiohttp
from typing import Dict, Any, Optional
from .base_tool import BaseTool, ToolResult
from ..config import settings

class WeatherTool(BaseTool):
    """Tool for getting weather information"""
    
    def __init__(self):
        super().__init__(
            name="get_weather",
            description="Get current weather information for any city or location"
        )
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    async def execute(self, location: str, units: str = "metric") -> ToolResult:
        """
        Execute weather lookup
        
        Args:
            location: City name or location
            units: Temperature units (metric, imperial, kelvin)
            
        Returns:
            ToolResult with weather information
        """
        try:
            if not self.api_key:
                # Use free weather service as fallback
                return await self._get_weather_fallback(location)
            
            weather_data = await self._get_weather_openweather(location, units)
            
            if not weather_data:
                return ToolResult(
                    success=False,
                    result=None,
                    error="Weather data not found for the specified location"
                )
            
            return ToolResult(
                success=True,
                result=weather_data,
                metadata={"source": "openweathermap", "units": units}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"Weather lookup failed: {str(e)}"
            )
    
    async def _get_weather_openweather(self, location: str, units: str) -> Optional[Dict[str, Any]]:
        """
        Get weather from OpenWeatherMap API
        
        Args:
            location: Location to get weather for
            units: Temperature units
            
        Returns:
            Weather data dictionary
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Get current weather
                params = {
                    'q': location,
                    'appid': self.api_key,
                    'units': units
                }
                
                async with session.get(
                    f"{self.base_url}/weather",
                    params=params
                ) as response:
                    if response.status != 200:
                        return None
                    
                    data = await response.json()
                    
                    # Format weather data
                    weather_info = {
                        "location": f"{data['name']}, {data['sys']['country']}",
                        "temperature": data['main']['temp'],
                        "feels_like": data['main']['feels_like'],
                        "humidity": data['main']['humidity'],
                        "pressure": data['main']['pressure'],
                        "description": data['weather'][0]['description'].title(),
                        "wind_speed": data.get('wind', {}).get('speed', 0),
                        "visibility": data.get('visibility', 0) / 1000,  # Convert to km
                        "units": units,
                        "timestamp": data['dt']
                    }
                    
                    # Add temperature unit symbol
                    if units == "metric":
                        weather_info["temp_unit"] = "°C"
                        weather_info["speed_unit"] = "m/s"
                    elif units == "imperial":
                        weather_info["temp_unit"] = "°F"
                        weather_info["speed_unit"] = "mph"
                    else:
                        weather_info["temp_unit"] = "K"
                        weather_info["speed_unit"] = "m/s"
                    
                    return weather_info
                    
        except Exception:
            return None
    
    async def _get_weather_fallback(self, location: str) -> ToolResult:
        """
        Fallback weather service when API key is not available
        
        Args:
            location: Location to get weather for
            
        Returns:
            ToolResult with limited weather information
        """
        try:
            # Use a free weather service (wttr.in)
            async with aiohttp.ClientSession() as session:
                url = f"http://wttr.in/{location}?format=j1"
                
                async with session.get(url) as response:
                    if response.status != 200:
                        return ToolResult(
                            success=False,
                            result=None,
                            error="Weather service unavailable"
                        )
                    
                    data = await response.json()
                    
                    # Extract current weather
                    current = data['current_condition'][0]
                    location_info = data['nearest_area'][0]
                    
                    weather_info = {
                        "location": f"{location_info['areaName'][0]['value']}, {location_info['country'][0]['value']}",
                        "temperature": int(current['temp_C']),
                        "feels_like": int(current['FeelsLikeC']),
                        "humidity": int(current['humidity']),
                        "description": current['weatherDesc'][0]['value'],
                        "wind_speed": int(current['windspeedKmph']),
                        "visibility": int(current['visibility']),
                        "temp_unit": "°C",
                        "speed_unit": "km/h",
                        "units": "metric"
                    }
                    
                    return ToolResult(
                        success=True,
                        result=weather_info,
                        metadata={"source": "wttr.in", "note": "Free weather service"}
                    )
                    
        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"Fallback weather service failed: {str(e)}"
            )
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get parameters schema for weather tool"""
        return {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name or location to get weather for (e.g., 'London', 'New York', 'Jakarta, Indonesia')"
                },
                "units": {
                    "type": "string",
                    "description": "Temperature units: 'metric' (Celsius), 'imperial' (Fahrenheit), or 'kelvin'",
                    "enum": ["metric", "imperial", "kelvin"],
                    "default": "metric"
                }
            },
            "required": ["location"]
        }
