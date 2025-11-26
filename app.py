import streamlit as st
import json
import os
from serpapi import GoogleSearch 
import google.generativeai as genai
from datetime import datetime

# Set up Streamlit UI
st.set_page_config(page_title="🌍 AI Travel Planner", layout="wide")
st.markdown(
    """
    <style>
        .title {text-align: center; font-size: 36px; font-weight: bold; color: #ff5733;}
        .subtitle {text-align: center; font-size: 20px; color: #555;}
        .stButton>button {width: 100%; border-radius: 20px; height: 50px; font-size: 18px;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Title
st.markdown('<h1 class="title">✈️ AI-Powered Travel Planner</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Real flights + AI Itineraries (Stable Version)</p>', unsafe_allow_html=True)

# Inputs
col1, col2 = st.columns(2)
with col1:
    source = st.text_input("🛫 Departure City (IATA):", "BOM")
with col2:
    destination = st.text_input("🛬 Destination (IATA):", "DEL")

col3, col4, col5 = st.columns(3)
with col3:
    num_days = st.slider("Days", 1, 14, 5)
with col4:
    departure_date = st.date_input("Departure Date")
with col5:
    return_date = st.date_input("Return Date")

activity_preferences = st.text_area("What do you like?", "Beaches, Historical sites, Good food")

# Sidebar
st.sidebar.title("⚙️ Preferences")
budget = st.sidebar.radio("Budget:", ["Economy", "Standard", "Luxury"])
hotel_rating = st.sidebar.selectbox("Hotel:", ["3⭐", "4⭐", "5⭐"])

# API Keys from Secrets
try:
    SERPAPI_KEY = st.secrets["SERPAPI_KEY"]
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    st.error("❌ Keys missing! Add SERPAPI_KEY and GOOGLE_API_KEY to Secrets.")
    st.stop()

def fetch_flights():
    params = {
        "engine": "google_flights",
        "departure_id": source,
        "arrival_id": destination,
        "outbound_date": str(departure_date),
        "return_date": str(return_date),
        "currency": "INR",
        "hl": "en",
        "api_key": SERPAPI_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    best_flights = results.get("best_flights", [])
    return sorted(best_flights, key=lambda x: x.get("price", float("inf")))[:3]

if st.button("🚀 Generate Travel Plan"):
    # 1. Fetch Flights
    with st.spinner("✈️ Finding cheapest flights..."):
        try:
            flights = fetch_flights()
        except Exception as e:
            st.error(f"Flight Search Error: {e}")
            flights = []

    # 2. Generate AI Itinerary
    with st.spinner("🤖 AI is building your itinerary..."):
        try:
            # Prepare Flight Info for AI
            flight_summary = "No flights found."
            if flights:
                flight_summary = ""
                for f in flights:
                    flight_summary += f"- {f.get('airline', 'Airline')} : ₹{f.get('price')} ({f.get('total_duration')} min)\n"

            # The Prompt
            prompt = f"""
            Act as an expert travel planner. Create a {num_days}-day trip for a {budget} budget traveler going from {source} to {destination}.
            
            **Trip Details:**
            - Theme: {activity_preferences}
            - Hotel Preference: {hotel_rating}
            
            **Flight Data Found:**
            {flight_summary}
            
            **Please Provide:**
            1. A summary of the best flight option from the data above.
            2. 3 Recommended Hotel areas/names for {destination}.
            3. A day-by-day itinerary ({num_days} days) focusing on: {activity_preferences}.
            4. Estimated total trip cost.
            
            Format nicely with Markdown/Bold text.
            """
            
            # Call Google AI Directly (Stable)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            ai_output = response.text
            
        except Exception as e:
            ai_output = f"AI Error: {e}"

    # 3. Display Results
    st.divider()
    
    # Show Flights Visually
    st.subheader("✈️ Top Flight Options")
    if flights:
        cols = st.columns(3)
        for i, flight in enumerate(flights):
            with cols[i]:
                st.success(f"**₹{flight.get('price')}**")
                st.write(f"{flight.get('airline')}")
                st.caption(f"{flight.get('total_duration')} mins")
    else:
        st.warning("No specific flights found for these dates.")

    # Show AI Plan
    st.divider()
    st.subheader("🗺️ Your AI Itinerary")
    st.markdown(ai_output)
