import requests
import os
from dotenv import load_dotenv

load_dotenv()
class WeatherService:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")  
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city: str):
        """Fetch current weather for the given city using OpenWeatherMap API"""
        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()

            if response.status_code == 200:
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                return f"The current weather in {city} is {desc} with a temperature of {temp}°C."
            else:
                return f"⚠️ API error: {data.get('message', 'Unknown error')}"

        except Exception as e:
            return f"Error fetching weather data: {e}"
        
# if __name__ == "__main__":
#     service = WeatherService()
#     print(service.get_weather("Paris"))
