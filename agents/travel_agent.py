# agents/travel_agent.py
from langchain.agents import Tool
from services.amadeus_service import AmadeusService

class TravelAgent:
    def __init__(self):
        self.amadeus = AmadeusService()
        self.tools = self.setup_tools()
    
    def setup_tools(self):
        return [
            Tool(
                name="FlightSearch",
                func=self.amadeus.flight_search,
                description="Search for flights between cities. Input: origin, destination, date"
            ),
            Tool(
                name="HotelSearch", 
                func=self.amadeus.hotel_search,
                description="Find hotels in a city. Input: city, check_in_date, check_out_date"
            )
        ]
    
    def get_tools(self):
        return self.tools