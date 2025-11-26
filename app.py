import streamlit as st
from serpapi import GoogleSearch
from datetime import datetime
import json

st.set_page_config(page_title="🌍 AI Travel Planner", layout="wide")

st.markdown('<h1 style="text-align: center; color: #ff5733;">✈️ AI-Powered Travel Planner</h1>', unsafe_allow_html=True)

# User Inputs
col1, col2 = st.columns(2)
with col1:
    source = st.text_input("🛫 Departure (IATA):", "BOM")
with col2:
    destination = st.text_input("🛬 Destination (IATA):", "DEL")

col3, col4 = st.columns(2)
with col3:
    departure_date = st.date_input("📅 Departure Date")
with col4:
    return_date = st.date_input("📅 Return Date")

if st.button("🚀 Find Cheapest Flights"):
    # Get API key from secrets
    SERPAPI_KEY = st.secrets["SERPAPI_KEY"]
    
    params = {
        "engine": "google_flights",
        "departure_id": source,
        "arrival_id": destination,
        "outbound_date": str(departure_date),
        "return_date": str(return_date),
        "currency": "INR",
        "api_key": SERPAPI_KEY
    }
    
    with st.spinner("Searching flights..."):
        search = GoogleSearch(params)
        results = search.get_dict()
        
        best_flights = results.get("best_flights", [])
        if best_flights:
            st.success("✅ Found flights!")
            cols = st.columns(3)
            for i, flight in enumerate(best_flights[:3]):
                with cols[i]:
                    price = flight.get("price", "N/A")
                    duration = flight.get("total_duration", "N/A")
                    st.markdown(f"""
                    <div style="border: 2px solid #ddd; padding: 15px; border-radius: 10px; text-align: center;">
                        <h3>₹{price}</h3>
                        <p>{duration}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("No flights found. Try different dates/cities.")
