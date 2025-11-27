import os
import json
from datetime import datetime

import streamlit as st
from serpapi import GoogleSearch
from agno.agent import Agent
from agno.tools.serpapi import SerpApiTools
from agno.models.google import Gemini

# ================== CONFIG & API KEYS ==================

st.set_page_config(page_title="🌍 AI Travel Planner", layout="wide")

# Read keys from Streamlit secrets
SERPAPI_KEY = st.secrets.get("SERPAPI_KEY", "")
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", "")

# Configure env for Gemini (agno expects GOOGLE_API_KEY env var)
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

if not SERPAPI_KEY:
    st.warning("⚠️ SERPAPI_KEY not set in secrets. Flight search will fail.")
if not GOOGLE_API_KEY:
    st.warning("⚠️ GOOGLE_API_KEY not set in secrets. AI agents will fail.")

# ================== STYLES & HEADER ==================

st.markdown(
    """
    <style>
        .title {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            color: #ff5733;
        }
        .subtitle {
            text-align: center;
            font-size: 20px;
            color: #555;
        }
        .stSlider > div {
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h1 class="title">✈️ AI-Powered Travel Planner</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Plan your dream trip with AI: real flights, hotels, and a smart itinerary.</p>',
    unsafe_allow_html=True,
)

# ================== USER INPUTS ==================

st.markdown("### 🌍 Where are you headed?")
source = st.text_input("🛫 Departure City (IATA Code):", "BOM")
destination = st.text_input("🛬 Destination (IATA Code):", "DEL")

st.markdown("### 📅 Plan Your Adventure")
num_days = st.slider("🕒 Trip Duration (days):", 1, 14, 5)
travel_theme = st.selectbox(
    "🎭 Select Your Travel Theme:",
    ["💑 Couple Getaway", "👨‍👩‍👧‍👦 Family Vacation", "🏔️ Adventure Trip", "🧳 Solo Exploration"],
)

st.markdown("---")

st.markdown(
    f"""
    <div style="
        text-align: center;
        padding: 15px;
        background-color: #ffecd1;
        border-radius: 10px;
        margin-top: 20px;
    ">
        <h3>🌟 Your {travel_theme} to {destination} is about to begin! 🌟</h3>
        <p>Let's find the best flights, stays, and experiences for your journey.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

def format_datetime(iso_string: str) -> str:
    try:
        dt = datetime.strptime(iso_string, "%Y-%m-%d %H:%M")
        return dt.strftime("%b-%d, %Y | %I:%M %p")
    except Exception:
        return "N/A"

activity_preferences = st.text_area(
    "🌍 What activities do you enjoy? (e.g., relaxing on the beach, exploring historical sites, nightlife, adventure)",
    "Relaxing on the beach, exploring historical sites",
)

departure_date = st.date_input("Departure Date")
return_date = st.date_input("Return Date")

# ================== SIDEBAR ==================

st.sidebar.title("🌎 Travel Assistant")
st.sidebar.subheader("Personalize Your Trip")

budget = st.sidebar.radio("💰 Budget Preference:", ["Economy", "Standard", "Luxury"])
flight_class = st.sidebar.radio("✈️ Flight Class:", ["Economy", "Business", "First Class"])
hotel_rating = st.sidebar.selectbox("🏨 Preferred Hotel Rating:", ["Any", "3⭐", "4⭐", "5⭐"])

st.sidebar.subheader("🎒 Packing Checklist")
packing_list = {
    "👕 Clothes": True,
    "🩴 Comfortable Footwear": True,
    "🕶️ Sunglasses & Sunscreen": False,
    "📖 Travel Guidebook": False,
    "💊 Medications & First-Aid": True,
}
for item, checked in packing_list.items():
    st.sidebar.checkbox(item, value=checked)

st.sidebar.subheader("🛂 Travel Essentials")
visa_required = st.sidebar.checkbox("🛃 Check Visa Requirements")
travel_insurance = st.sidebar.checkbox("🛡️ Get Travel Insurance")
currency_converter = st.sidebar.checkbox("💱 Currency Exchange Rates")

# ================== SERPAPI FLIGHT SEARCH ==================

base_flight_params = {
    "engine": "google_flights",
    "departure_id": source,
    "arrival_id": destination,
    "outbound_date": str(departure_date),
    "return_date": str(return_date),
    "currency": "INR",
    "hl": "en",
    "api_key": SERPAPI_KEY,
}

def fetch_flights(source_code, destination_code, dep_date, ret_date):
    params = {
        "engine": "google_flights",
        "departure_id": source_code,
        "arrival_id": destination_code,
        "outbound_date": str(dep_date),
        "return_date": str(ret_date),
        "currency": "INR",
        "hl": "en",
        "api_key": SERPAPI_KEY,
    }
    search = GoogleSearch(params)
    return search.get_dict()

def extract_cheapest_flights(flight_data):
    best_flights = flight_data.get("best_flights", [])
    sorted_flights = sorted(best_flights, key=lambda x: x.get("price", float("inf")))[:3]
    return sorted_flights

# ================== AGNO AI AGENTS (GEMINI 2.0 FLASH EXP) ==================

researcher = Agent(
    name="Researcher",
    instructions=[
        "Identify the travel destination specified by the user.",
        "Gather detailed information on the destination, including climate, culture, and safety tips.",
        "Find popular attractions, landmarks, and must-visit places.",
        "Search for activities that match the user's interests and travel style.",
        "Prioritize information from reliable sources and official travel guides.",
        "Provide well-structured summaries with key insights and recommendations.",
    ],
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)],
)

planner = Agent(
    name="Planner",
    instructions=[
        "Gather details about the user's travel preferences and budget.",
        "Create a detailed itinerary with scheduled activities and estimated costs.",
        "Ensure the itinerary includes transportation options and travel time estimates.",
        "Optimize the schedule for convenience and enjoyment.",
        "Present the itinerary in a structured format.",
    ],
    model=Gemini(id="gemini-2.0-flash-exp"),
)

hotel_restaurant_finder = Agent(
    name="Hotel & Restaurant Finder",
    instructions=[
        "Identify key locations in the user's travel itinerary.",
        "Search for highly rated hotels near those locations.",
        "Search for top-rated restaurants based on cuisine preferences and proximity.",
        "Prioritize results based on user preferences, ratings, and availability.",
        "Provide direct booking links or reservation options where possible.",
    ],
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)],
)

# ================== MAIN ACTION ==================

if st.button("🚀 Generate Travel Plan"):
    # 1) Flights
    with st.spinner("✈️ Fetching best flight options..."):
        try:
            flight_data = fetch_flights(source, destination, departure_date, return_date)
            cheapest_flights = extract_cheapest_flights(flight_data)
        except Exception as e:
            st.error(f"Error fetching flights: {e}")
            cheapest_flights = []

    # 2) Research
    with st.spinner("🔍 Researching best attractions & activities..."):
        research_prompt = (
            f"Research the best attractions and activities in {destination} for a {num_days}-day "
            f"{travel_theme.lower()} trip. The traveler enjoys: {activity_preferences}. "
            f"Budget: {budget}. Flight Class: {flight_class}. Hotel Rating: {hotel_rating}. "
            f"Visa Requirement: {visa_required}. Travel Insurance: {travel_insurance}."
        )
        try:
            research_results = researcher.run(research_prompt, stream=False)
        except Exception as e:
            st.error(f"Research agent error: {e}")
            research_results = type("obj", (), {"content": "Research unavailable due to an error."})

    # 3) Hotels & restaurants
    with st.spinner("🏨 Searching for hotels & restaurants..."):
        hotel_restaurant_prompt = (
            f"Find the best hotels and restaurants near popular attractions in {destination} for a "
            f"{travel_theme.lower()} trip. Budget: {budget}. Hotel Rating: {hotel_rating}. "
            f"Preferred activities: {activity_preferences}."
        )
        try:
            hotel_restaurant_results = hotel_restaurant_finder.run(hotel_restaurant_prompt, stream=False)
        except Exception as e:
            st.error(f"Hotel/restaurant agent error: {e}")
            hotel_restaurant_results = type("obj", (), {"content": "Hotel & restaurant suggestions unavailable."})

    # 4) Itinerary
    with st.spinner("🗺️ Creating your personalized itinerary..."):
        planning_prompt = (
            f"Based on the following data, create a {num_days}-day itinerary for a {travel_theme.lower()} trip to "
            f"{destination}. The traveler enjoys: {activity_preferences}. Budget: {budget}. "
            f"Flight Class: {flight_class}. Hotel Rating: {hotel_rating}. Visa Requirement: {visa_required}. "
            f"Travel Insurance: {travel_insurance}. Research: {research_results.content}. "
            f"Flights: {json.dumps(cheapest_flights)}. Hotels & Restaurants: {hotel_restaurant_results.content}."
        )
        try:
            itinerary = planner.run(planning_prompt, stream=False)
        except Exception as e:
            st.error(f"Itinerary agent error: {e}")
            itinerary = type("obj", (), {"content": "Itinerary could not be generated due to an error."})

    # ================== DISPLAY RESULTS ==================

    st.subheader("✈️ Cheapest Flight Options")
    if cheapest_flights:
        cols = st.columns(len(cheapest_flights))
        for idx, flight in enumerate(cheapest_flights):
            with cols[idx]:
                airline_logo = flight.get("airline_logo", "")
                airline_name = flight.get("airline", "Unknown Airline")
                price = flight.get("price", "Not Available")
                total_duration = flight.get("total_duration", "N/A")

                flights_info = flight.get("flights", [{}])
                departure = flights_info[0].get("departure_airport", {})
                arrival = flights_info[-1].get("arrival_airport", {})
                airline_name = flights_info[0].get("airline", "Unknown Airline")

                departure_time = format_datetime(departure.get("time", "N/A"))
                arrival_time = format_datetime(arrival.get("time", "N/A"))

                departure_token = flight.get("departure_token", "")
                booking_link = "#"

                try:
                    if departure_token:
                        params_with_token = {
                            **base_flight_params,
                            "departure_token": departure_token,
                        }
                        search_with_token = GoogleSearch(params_with_token)
                        results_with_booking = search_with_token.get_dict()
                        booking_token = results_with_booking["best_flights"][0].get("booking_token", "")
                        if booking_token:
                            booking_link = f"https://www.google.com/travel/flights?tfs={booking_token}"
                except Exception:
                    booking_link = "#"

                st.markdown(
                    f"""
                    <div style="
                        border: 2px solid #ddd;
                        border-radius: 10px;
                        padding: 15px;
                        text-align: center;
                        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
                        background-color: #f9f9f9;
                        margin-bottom: 20px;
                    ">
                        <img src="{airline_logo}" width="100" alt="Flight Logo" />
                        <h3 style="margin: 10px 0;">{airline_name}</h3>
                        <p><strong>Departure:</strong> {departure_time}</p>
                        <p><strong>Arrival:</strong> {arrival_time}</p>
                        <p><strong>Duration:</strong> {total_duration} min</p>
                        <h2 style="color: #008000;">💰 {price}</h2>
                        <a href="{booking_link}" target="_blank" style="
                            display: inline-block;
                            padding: 10px 20px;
                            font-size: 16px;
                            font-weight: bold;
                            color: #fff;
                            background-color: #007bff;
                            text-decoration: none;
                            border-radius: 5px;
                            margin-top: 10px;
                        ">🔗 Book Now</a>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.warning("⚠️ No flight data available.")

    st.subheader("🏨 Hotels & Restaurants")
    st.write(hotel_restaurant_results.content)

    st.subheader("🗺️ Your Personalized Itinerary")
    st.write(itinerary.content)

    st.success("✅ Travel plan generated successfully!")
