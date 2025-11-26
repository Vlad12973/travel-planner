import streamlit as st
import json
import os
from serpapi import GoogleSearch  # ✅ THIS WORKS WITH 'serpapi' package
from datetime import datetime


# REMOVE agno imports for now - will add back later
# from agno.agent import Agent
# from agno.tools.serpapi import SerpApiTools  
# from agno.models.google import Gemini

# Set up Streamlit UI with a travel-friendly theme
st.set_page_config(page_title="🌍 AI Travel Planner", layout="wide")
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

# Title and subtitle
st.markdown('<h1 class="title">✈️ AI-Powered Travel Planner</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Real flights + AI itineraries!</p>', unsafe_allow_html=True)

# User Inputs Section
st.markdown("### 🌍 Where are you headed?")
source = st.text_input("🛫 Departure City (IATA Code):", "BOM")
destination = st.text_input("🛬 Destination (IATA Code):", "DEL")

st.markdown("### 📅 Plan Your Adventure")
num_days = st.slider("🕒 Trip Duration (days):", 1, 14, 5)
travel_theme = st.selectbox(
    "🎭 Select Your Travel Theme:",
    ["💑 Couple Getaway", "👨‍👩‍👧‍👦 Family Vacation", "🏔️ Adventure Trip", "🧳 Solo Exploration"]
)

# Divider for aesthetics
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
    </div>
    """,
    unsafe_allow_html=True,
)

def format_datetime(iso_string):
    try:
        dt = datetime.strptime(iso_string, "%Y-%m-%d %H:%M")
        return dt.strftime("%b-%d, %Y | %I:%M %p")
    except:
        return "N/A"

activity_preferences = st.text_area(
    "🌍 What activities do you enjoy?",
    "Relaxing on the beach, exploring historical sites"
)

departure_date = st.date_input("Departure Date")
return_date = st.date_input("Return Date")

# Sidebar Setup
st.sidebar.title("🌎 Travel Assistant")
budget = st.sidebar.radio("💰 Budget:", ["Economy", "Standard", "Luxury"])
flight_class = st.sidebar.radio("✈️ Flight Class:", ["Economy", "Business", "First Class"])
hotel_rating = st.sidebar.selectbox("🏨 Hotel Rating:", ["Any", "3⭐", "4⭐", "5⭐"])

# Get API key from Streamlit secrets
SERPAPI_KEY = st.secrets["SERPAPI_KEY"]

# Function to fetch flight data
def fetch_flights(source, destination, departure_date, return_date):
    params = {
        "engine": "google_flights",
        "departure_id": source.upper(),
        "arrival_id": destination.upper(),
        "outbound_date": str(departure_date),
        "return_date": str(return_date),
        "currency": "INR",
        "hl": "en",
        "api_key": SERPAPI_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results

# Function to extract top 3 cheapest flights
def extract_cheapest_flights(flight_data):
    best_flights = flight_data.get("best_flights", [])
    sorted_flights = sorted(best_flights, key=lambda x: x.get("price", float("inf")))[:3]
    return sorted_flights

# Generate Travel Plan
if st.button("🚀 Generate Travel Plan", type="primary"):
    try:
        with st.spinner("✈️ Fetching real flight options..."):
            flight_data = fetch_flights(source, destination, departure_date, return_date)
            cheapest_flights = extract_cheapest_flights(flight_data)

        # Mock AI responses for now (real AI later)
        research_results = f"Top attractions in {destination}: Historical sites, local markets, beaches"
        hotel_results = f"Best {hotel_rating} hotels: Central location, great reviews"
        
        # Smart itinerary generator
        itinerary = f"""
## 🗺️ **{num_days}-Day {travel_theme} Plan for {destination}**

### ✈️ **Cheapest Flights Found**
{len(cheapest_flights)} options available!

### 🏨 **Recommended Hotels** ({budget})
- 4⭐ Central hotels (~₹3000/night)
- Great reviews & location

### 📋 **Daily Schedule**
**Day 1:** Arrival + {activity_preferences.split(',')[0]}
**Day 2-{num_days}:** Full adventure with your preferences!

**Total Cost:** ₹25,000-₹50,000 ({budget})
        """

        # Display Results
        st.subheader("✈️ Real Flight Options")
        if cheapest_flights:
            cols = st.columns(min(3, len(cheapest_flights)))
            for idx, flight in enumerate(cheapest_flights):
                with cols[idx]:
                    price = flight.get("price", "N/A")
                    duration = flight.get("total_duration", "N/A")
                    airline = flight.get("airline", "Unknown")
                    
                    st.markdown(f"""
                    <div style="
                        border: 2px solid #4CAF50;
                        border-radius: 15px;
                        padding: 20px;
                        text-align: center;
                        background: #f0f8f0;
                    ">
                        <h3>₹{price}</h3>
                        <p><strong>{airline}</strong></p>
                        <p>{duration}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ No flights found. Try different dates.")

        st.subheader("🏨 Hotels & Restaurants")
        st.write(hotel_results)

        st.subheader("🗺️ Your Personalized Itinerary")
        st.markdown(itinerary)

        st.success("✅ Travel plan ready!")
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("💡 Add SERPAPI_KEY in Settings → Secrets")

st.sidebar.info("🔑 Get free SerpAPI key: serpapi.com")

