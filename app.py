# # app.py
# from fastapi import FastAPI
# from agents.travel_agent import TravelAgent

# app = FastAPI()
# travel_agent = TravelAgent()

# @app.get("/")
# def home():
#     return {"message": "🌍 AI Travel Assistant API is Running!"}

# @app.get("/flights/{origin}/{destination}/{date}")
# def search_flights(origin: str, destination: str, date: str):
#     flights = travel_agent.amadeus.flight_search(origin, destination, date)
#     return {"route": f"{origin} to {destination}", "flights": flights}

# @app.get("/hotels/{city}/{check_in}/{check_out}")
# def search_hotels(city: str, check_in: str, check_out: str):
#     hotels = travel_agent.amadeus.hotel_search(city, check_in, check_out)
#     return {"city": city, "hotels": hotels}

# @app.get("/test-agent")
# def test_agent():
#     tools = travel_agent.get_tools()
#     return {"agent_status": "active", "tools_available": len(tools)}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Travel Assistant", version="1.0.0")

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AmadeusService:
    def flight_search(self, origin, destination, date):
        return {
            "flights": [
                {"airline": "PIA", "price": "PKR 25,000", "date": date, "route": f"{origin} to {destination}"},
                {"airline": "Emirates", "price": "PKR 45,000", "date": date, "route": f"{origin} to {destination}"},
                {"airline": "Air Blue", "price": "PKR 30,000", "date": date, "route": f"{origin} to {destination}"}
            ]
        }
    
    def hotel_search(self, city, check_in, check_out):
        return {
            "hotels": [
                {"name": "Pearl Continental", "price": "PKR 8,000/night", "city": city},
                {"name": "Nishat Hotel", "price": "PKR 12,000/night", "city": city},
                {"name": "Avari Hotel", "price": "PKR 15,000/night", "city": city}
            ]
        }

# Create service instance
amadeus = AmadeusService()

@app.get("/")
def home():
    return {"message": "🌍 AI Travel Assistant API is Running!", "status": "success"}

@app.get("/flights/{origin}/{destination}/{date}")
def search_flights(origin: str, destination: str, date: str):
    flights = amadeus.flight_search(origin, destination, date)
    return {
        "route": f"{origin} to {destination}",
        "date": date,
        "results": flights
    }

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
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)