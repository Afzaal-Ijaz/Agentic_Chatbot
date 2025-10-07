import os
import requests
from dotenv import load_dotenv

load_dotenv()

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

    def flight_search(self, origin, destination, date):
        """Step 2: Search flights"""
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

    # def hotel_search(self, city, check_in, check_out):
    #     """Step 3: Search hotels"""
    #     url = f"{self.base_url}/v1/shopping/hotel-offers"
    #     headers = {"Authorization": f"Bearer {self.access_token}"}
    #     params = {
    #         "cityCode": city,
    #         "checkInDate": check_in,
    #         "checkOutDate": check_out
    #     }

    #     response = requests.get(url, headers=headers, params=params)
    #     return response.json()
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
    #------------------------------------------
    #flights search
    #------------------------------------------
    
    # result = amadeus.flight_search('LON', 'PAR', '2025-12-15')

    # flights = result.get("data", [])

    # for flight in flights:
    #     # Basic flight info
    #     price = flight["price"]["total"]
    #     currency = flight["price"]["currency"]
        
    #     # Itinerary info (take first segment only for now)
    #     first_segment = flight["itineraries"][0]["segments"][0]
    #     last_segment = flight["itineraries"][0]["segments"][-1]

    #     origin = first_segment["departure"]["iataCode"]
    #     destination = last_segment["arrival"]["iataCode"]
    #     departure_time = first_segment["departure"]["at"]
    #     arrival_time = last_segment["arrival"]["at"]
    #     airline = first_segment["carrierCode"]

    #     print(f"\n✈️  {airline}: {origin} → {destination}")
    #     print(f"   🕒 Departure: {departure_time}")
    #     print(f"   🕓 Arrival: {arrival_time}")
    #     print(f"   💰 Price: {price} {currency}")
   
    #------------------------------------------
    # hotels search
    #------------------------------------------
    result = amadeus.hotel_search("PAR", "2025-12-15", "2025-12-20")
    print(result)

