import os
import json
from datetime import datetime

import streamlit as st
from serpapi import GoogleSearch
from openai import OpenAI

# ============== CONFIG & KEYS ==============

st.set_page_config(page_title="🌍 AI Travel Planner", layout="wide")

SERPAPI_KEY = st.secrets.get("SERPAPI_KEY", "")
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")

if not SERPAPI_KEY:
    st.warning("⚠️ SERPAPI_KEY not set in secrets. Flight search will fail.")
if not OPENAI_API_KEY:
    st.warning("⚠️ OPENAI_API_KEY not set in secrets. AI itinerary will fail.")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ============== STYLES & HEADER ==============

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
    '<p class="subtitle">Real flights via SerpAPI + itinerary via OpenAI.</p>',
    unsafe_allow_html=True,
)

# ============== USER INPUTS ==============

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

# ============== SIDEBAR ==============

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

# ============== SERPAPI FLIGHT SEARCH ==============

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

# ============== MAIN ACTION ==============

if st.button("🚀 Generate Travel Plan"):
    # 1) Flights
    with st.spinner("✈️ Fetching best flight options..."):
        try:
            flight_data = fetch_flights(source, destination, departure_date, return_date)
            cheapest_flights = extract_cheapest_flights(flight_data)
        except Exception as e:
            st.error(f"Error fetching flights: {e}")
            cheapest_flights = []

    # Prepare a compact summary of flights for the AI
    flight_summary = "No flights found."
    if cheapest_flights:
        lines = []
        for f in cheapest_flights:
            lines.append(
                f"- {f.get('airline', 'Airline')} | ₹{f.get('price', 'N/A')} | {f.get('total_duration', 'N/A')} min"
            )
        flight_summary = "\n".join(lines)

    # 2) AI itinerary via OpenAI
    ai_itinerary = "AI itinerary not available (missing OPENAI_API_KEY)."
    if client:
        with st.spinner("🤖 Our advanced AI is crafting your personalized travel plan..."):
            try:
                prompt = f"""
You are an expert travel planner.

Create a detailed {num_days}-day itinerary for a {travel_theme.lower()} trip from {source} to {destination}.

Traveler preferences:
- Activities: {activity_preferences}
- Budget: {budget}
- Flight class: {flight_class}
- Hotel rating: {hotel_rating}
- Visa required: {visa_required}
- Travel insurance: {travel_insurance}

Real flight options found:
{flight_summary}

Please provide:
1. A short 2-3 line overview of the trip.
2. The best flight choice from the above, with reasoning.
3. 3 hotel suggestions (area + type, no real bookings).
4. A day-by-day itinerary for {num_days} days (morning/afternoon/evening).
5. Rough total cost range in INR for the whole trip.

Format the response nicely using Markdown with headings and bullet points.
                """

                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful, expert travel planner."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                )
                ai_itinerary = completion.choices[0].message.content
            except Exception as e:
                ai_itinerary = f"AI Error: {e}"

    # ============== DISPLAY RESULTS ==============

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
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.warning("⚠️ No flight data available.")

    st.subheader("🗺️ Your AI Itinerary")
    st.markdown(ai_itinerary)


