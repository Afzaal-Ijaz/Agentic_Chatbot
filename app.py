
# app.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.amadeus_service import AmadeusService

app = FastAPI(title="AI Travel Assistant", version="1.0.0")

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create service instance
amadeus = AmadeusService(
    client_id=os.getenv("AMADEUS_CLIENT_ID"),
    client_secret=os.getenv("AMADEUS_CLIENT_SECRET")
)
  
@app.get("/")
def home():
    return {"message": "🌍 AI Travel Assistant API is Running!", "status": "success"}

#------------------------------
#endpoint to get flights info
#------------------------------
@app.get("/flights/{origin}/{destination}/{date}")
def search_flights(origin: str, destination: str, date: str):
    result = amadeus.flight_search(origin, destination, date)
    flights = result.get("data", [])

    clean_flights = []
    for flight in flights:
        price = flight["price"]["total"]
        currency = flight["price"]["currency"]

        first_segment = flight["itineraries"][0]["segments"][0]
        last_segment = flight["itineraries"][0]["segments"][-1]

        flight_info = {
            "airline": first_segment["carrierCode"],
            "origin": first_segment["departure"]["iataCode"],
            "destination": last_segment["arrival"]["iataCode"],
            "departure_time": first_segment["departure"]["at"],
            "arrival_time": last_segment["arrival"]["at"],
            "price": price,
            "currency": currency
        }
        clean_flights.append(flight_info)

    return {
        "route": f"{origin} → {destination}",
        "date": date,
        "flights": clean_flights
    }

#------------------------------
#endpoint to get hotels info
#------------------------------
@app.get("/hotels/{city}/{check_in}/{check_out}")
def search_hotels(city: str, check_in: str, check_out: str):
    hotels = amadeus.hotel_search(city, check_in, check_out)
    return {
        "city": city,
        "check_in": check_in,
        "check_out": check_out,
        "results": hotels
    }

@app.get("/test")
def test_endpoint():
    return {"status": "working", "message": "API is responding correctly!"}

if __name__ == "__main__":
    import uvicorn
    # uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)