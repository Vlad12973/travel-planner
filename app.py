import os
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

# ============== SIMPLE CITY → IATA MAPPING ==============

CITY_IATA_MAP = {
    "hyderabad": [("Hyderabad - Rajiv Gandhi International", "HYD")],
    "mumbai": [("Mumbai - Chhatrapati Shivaji Maharaj", "BOM")],
    "delhi": [("Delhi - Indira Gandhi International", "DEL")],
    "bangalore": [("Bengaluru - Kempegowda International", "BLR")],
    "bengaluru": [("Bengaluru - Kempegowda International", "BLR")],
    "chennai": [("Chennai International", "MAA")],
    "kolkata": [("Kolkata - Netaji Subhas Chandra Bose", "CCU")],
    "pune": [("Pune Airport", "PNQ")],
    "ahmedabad": [("Ahmedabad - Sardar Vallabhbhai Patel", "AMD")],
    "kochi": [("Kochi - Cochin International", "COK")],
    "cochin": [("Kochi - Cochin International", "COK")],
    "goa": [("Goa - Manohar International (North)", "GOX"),
            ("Goa - Dabolim (South)", "GOI")],
    "jaipur": [("Jaipur International", "JAI")],
    "lucknow": [("Lucknow - Chaudhary Charan Singh", "LKO")],
    "visakhapatnam": [("Visakhapatnam Airport", "VTZ")],
    "vizag": [("Visakhapatnam Airport", "VTZ")],
}

def get_airport_options(city_name: str):
    key = city_name.strip().lower()
    return CITY_IATA_MAP.get(key, [])


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
            background-color: #0c1117;
            padding: 10px;
            border-radius: 10px;
        }
        .flight-card {
            border: 2px solid #2b2f3a;
            border-radius: 16px;
            padding: 18px;
            text-align: center;
            background-color: #f9f9f9;
            margin-bottom: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h1 class="title">✈️ AI-Powered Travel Planner</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Real flights via SerpAPI + AI itinerary that respects your budget.</p>',
    unsafe_allow_html=True,
)

# ============== USER INPUTS ==============

st.markdown("### 🌍 Where are you headed?")

source_city = st.text_input("🛫 Departure City (name):", "Hyderabad")
destination_city = st.text_input("🛬 Destination City (name):", "Delhi")

source_airports = get_airport_options(source_city)
destination_airports = get_airport_options(destination_city)

# Departure airport
if source_airports:
    source_choice = st.selectbox(
        "Select departure airport (IATA):",
        [f"{name} ({code})" for name, code in source_airports],
        key="source_airport_select",
    )
    source = source_choice.split("(")[-1].replace(")", "").strip()
else:
    source = st.text_input("Departure IATA code (fallback):", "HYD")

# Destination airport
if destination_airports:
    dest_choice = st.selectbox(
        "Select destination airport (IATA):",
        [f"{name} ({code})" for name, code in destination_airports],
        key="dest_airport_select",
    )
    destination = dest_choice.split("(")[-1].replace(")", "").strip()
else:
    destination = st.text_input("Destination IATA code (fallback):", "DEL")

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
        <h3>🌟 Your {travel_theme} from {source_city} to {destination_city} is about to begin! 🌟</h3>
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

def build_booking_link(flight):
    booking_token = flight.get("booking_token")
    if booking_token:
        return f"https://www.google.com/travel/flights?tfs={booking_token}"
    # Fallback – generic Google Flights search for this route and dates
    return (
        "https://www.google.com/travel/flights?"
        f"q=flights+from+{source}+to+{destination}"
        f"+on+{departure_date}+return+{return_date}"
    )

# ============== MAIN ACTION ==============

if st.button("🚀 Generate Travel Plan"):
    # 1) Flights
    with st.spinner("✈️ Finding the best real-time flight options for you..."):
        try:
            flight_data = fetch_flights(source, destination, departure_date, return_date)
            cheapest_flights = extract_cheapest_flights(flight_data)
        except Exception as e:
            st.error(f"Error fetching flights: {e}")
            cheapest_flights = []

    # Prepare flight summary + price stats for AI
    flight_summary = "No flights found."
    min_price = max_price = avg_price = None

    if cheapest_flights:
        prices = []
        lines = []
        for f in cheapest_flights:
            price = f.get("price")
            if isinstance(price, (int, float)):
                prices.append(price)
            airline = f.get("airline", "Airline")
            duration = f.get("total_duration", "N/A")
            lines.append(f"- {airline} | ₹{price} | {duration} min")
        flight_summary = "\n".join(lines)

        if prices:
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)

    # 2) AI itinerary via OpenAI (uses price info in budget)
    ai_itinerary = "AI itinerary not available (missing OPENAI_API_KEY)."
    if client:
        with st.spinner("🤖 Our advanced AI is crafting your personalized travel plan..."):
            try:
                budget_hint = (
                    f"Flight price range (from live data): min ₹{min_price}, "
                    f"max ₹{max_price}, avg ₹{int(avg_price)}."
                    if min_price is not None
                    else "No flight price data available."
                )

                prompt = f"""
You are an expert travel planner for Indian travellers.

Create a detailed {num_days}-day itinerary for a {travel_theme.lower()} trip
from {source_city} ({source}) to {destination_city} ({destination}).

Traveller preferences:
- Activities: {activity_preferences}
- Budget level: {budget}
- Flight class: {flight_class}
- Hotel rating preference: {hotel_rating}
- Visa required: {visa_required}
- Travel insurance: {travel_insurance}

Real flight options found (from SerpAPI / Google Flights):
{flight_summary}

Cost information:
{budget_hint}

Use the flight price range and budget level to:
- Suggest a realistic total trip budget in INR (including flights, hotels, food, local travel, and activities).
- Adjust hotel type, daily spending, and activity choices (more premium for Luxury, more value-optimised for Economy).

Please provide:
1. A short 2–3 line overview of the trip.
2. The best flight choice from the above, with reasoning (and approximate cost).
3. 3 hotel suggestions (area + type, approximate nightly price range, no real booking links).
4. A day-by-day itinerary for {num_days} days (morning / afternoon / evening).
5. A realistic total trip cost range in INR, clearly broken down:
   - Flights (based on price range above)
   - Hotels (per night × nights)
   - Food & local travel (per day × days)
   - Activities / tickets
6. A one-line summary like: "This plan fits well within a typical {budget} Indian traveller budget."

Format the response nicely using Markdown with headings, subheadings, and bullet points.
                """

                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful, detail-oriented travel planner "
                                "for Indian travellers. Always think in INR and be realistic on costs."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                )
                ai_itinerary = completion.choices[0].message.content
            except Exception as e:
                ai_itinerary = f"AI Error: {e}"

    # ============== DISPLAY RESULTS ==============

    st.subheader("✈️ Cheapest Flight Options (Live from SerpAPI)")
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

                booking_link = build_booking_link(flight)

                st.markdown(
                    f"""
                    <div class="flight-card">
                        <img src="{airline_logo}" width="80" alt="Flight Logo" />
                        <h3 style="margin: 10px 0;">{airline_name}</h3>
                        <p><strong>Departure:</strong> {departure_time}</p>
                        <p><strong>Arrival:</strong> {arrival_time}</p>
                        <p><strong>Duration:</strong> {total_duration} min</p>
                        <h2 style="color: #008000;">💰 {price}</h2>
                        <a href="{booking_link}" target="_blank" style="
                            display: inline-block;
                            padding: 8px 18px;
                            font-size: 15px;
                            font-weight: 600;
                            color: #fff;
                            background-color: #007bff;
                            text-decoration: none;
                            border-radius: 6px;
                            margin-top: 10px;
                        ">🔗 Book on Google Flights</a>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        if min_price is not None:
            st.info(
                f"💡 Flight price summary (from results): "
                f"min ₹{min_price}, max ₹{max_price}, avg ≈ ₹{int(avg_price)}"
            )
    else:
        st.warning("⚠️ No flight data available for these dates/airports. Try changing dates or airports.")

    st.subheader("🗺️ Your AI Itinerary (Budget-Aware)")
    st.markdown(ai_itinerary)
