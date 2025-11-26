import os
import requests
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from utils.llm import llm
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class FlightQuery(BaseModel):
    origin: str = Field(description="Departure city or airport")
    destination: str = Field(description="Arrival city or airport")
    date: str = Field(description="Travel date in YYYY-MM-DD format if possible")

parser = PydanticOutputParser(pydantic_object=FlightQuery)

prompt = PromptTemplate(
    template=(
        "Extract origin, destination, and date from this user query:\n"
        "{query}\n\n"
        "{format_instructions}"
    ),
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)


class AmadeusService:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://test.api.amadeus.com"
        self.access_token = self.get_access_token()

    def get_access_token(self):
        """Step 1: Get a token from Amadeus"""
        url = f"{self.base_url}/v1/security/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("✅ Access token generated successfully")
            return token
        else:
            print("❌ Token request failed:", response.text)
            return None
        
    
    def parse_flight_query(self,user_query: str):
        input = prompt.format_prompt(query=user_query)
        output = llm.invoke(input.to_messages())
        return parser.parse(output.content)
    

    def flight_search(self, origin, destination, date):
        """Extracts origin, destination, and date from query and searches flights."""
        url = f"{self.base_url}/v2/shopping/flight-offers"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": date,
        "adults": 1,
        "max": 3
        }

        response = requests.get(url, headers=headers, params=params)
        return response.json()


    def hotel_search(self, city, check_in, check_out):
        """Search hotels in a given city"""
        self.get_access_token()  # make sure token is valid
    
        url = f"{self.base_url}/v1/shopping/hotel-offers"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {
            "cityCode": city,
            "checkInDate": check_in,
            "checkOutDate": check_out,
            "adults": 1
        }

        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            print("❌ Error:", response.status_code, response.text)
            return {"error": response.text}
        
        return response.json()



if __name__ == "__main__":
    amadeus = AmadeusService(
        client_id=os.getenv("AMADEUS_CLIENT_ID"),
        client_secret=os.getenv("AMADEUS_CLIENT_SECRET")
    )

    # result = amadeus.hotel_search("PAR", "2025-12-15", "2025-12-20")
    # print(result)

