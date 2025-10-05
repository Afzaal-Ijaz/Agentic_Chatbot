# import requests

# class AmadeusService:
#     def _init_(self):
#         self.api_key = "your_amadeus_key"
    
#     def flight_search(self, origin, destination, date):
#         """Pure Amadeus API call - no LangChain here"""
#         # Make actual API request to Amadeus
#         url = "https://test.api.amadeus.com/v1/shopping/flight-destinations"
#         params = {'origin': origin, 'departureDate': date}
#         response = requests.get(url, params=params)
#         return response.json()  # Return raw flight data
    
#     def hotel_search(self, city, check_in, check_out):
#         """Pure Amadeus API call - no LangChain here"""
#         # Make actual API request to Amadeus for hotels
#         url = "https://test.api.amadeus.com/v1/shopping/hotel-offers"
#         params = {'cityCode': city, 'checkInDate': check_in, 'checkOutDate': check_out}
#         response = requests.get(url, params=params)
#         return response.json()  # Return raw hotel data

class AmadeusService:
    def flight_search(self, origin, destination, date):
        # For now, just return fake data to test
        return {
            "flights": [
                {"airline": "PIA", "price": "PKR 25,000", "date": date},
                {"airline": "Emirates", "price": "PKR 45,000", "date": date}
            ]
        }
    
    def hotel_search(self, city, check_in, check_out):
        return {
            "hotels": [
                {"name": "Pearl Continental", "price": "PKR 8,000/night"},
                {"name": "Nishat Hotel", "price": "PKR 12,000/night"}
            ]
        }
