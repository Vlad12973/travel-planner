import os
from datetime import datetime

import streamlit as st
from serpapi import GoogleSearch
from openai import OpenAI

# ============== CONFIG & KEYS ==============

st.set_page_config(page_title="🌴 Travel Planner", layout="wide")

SERPAPI_KEY = st.secrets.get("SERPAPI_KEY", "")
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")

if not SERPAPI_KEY:
    st.warning("⚠️ SERPAPI_KEY not set in secrets. Flight search will fail.")
if not OPENAI_API_KEY:
    st.warning("⚠️ OPENAI_API_KEY not set in secrets. AI itinerary will fail.")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ============== CITY → IATA MAPPING ==============

CITY_IATA_MAP = {
    "hyderabad": [("Hyderabad - Rajiv Gandhi International", "HYD")],
    "mumbai": [("Mumbai - Chhatrapati Shivaji Maharaj", "BOM")],
    "delhi": [("Delhi - Indira Gandhi International", "DEL")],
    "bangalore": [("Bengaluru - Kempegowda International", "BLR")],
    "bengaluru": [("Bengaluru - Kempegowda International", "BLR")],
    "chennai": [("Chennai International", "MAA")],
    "kolkata": [("Kolkata - Netaji Subhas Chandra Bose", "CCU")],
    "pune": [("Pune Airport", "PNQ")],
}

def get_airport_options(city_name: str):
    return CITY_IATA_MAP.get(city_name.strip().lower(), [])


# ============== GLOBAL STYLES ==============

st.markdown(
    """
    <style>
    :root {
        --accent: #09c6f9;
        --accent-soft: rgba(9, 198, 249, 0.16);
        --accent-strong: #ff7b72;
        --bg-deep: #050816;
        --bg-panel: rgba(15, 23, 42, 0.88);
        --text-main: #e5e7eb;
        --text-muted: #9ca3af;
    }

    body {
        background: radial-gradient(circle at top left, #1f2937 0%, #020617 55%, #000 100%);
        color: var(--text-main);
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    /* HERO */
    .hero {
        border-radius: 24px;
        padding: 32px 40px 80px 40px;
        background:
            linear-gradient(115deg, rgba(3, 7, 18, 0.9) 0%, rgba(15, 23, 42, 0.35) 40%, rgba(248, 250, 252, 0.05) 100%),
            url("https://images.pexels.com/photos/457882/pexels-photo-457882.jpeg") center/cover no-repeat;
        color: #fff;
        position: relative;
        margin-bottom: 64px;
        box-shadow: 0 24px 60px rgba(0, 0, 0, 0.55);
    }
    .hero-title {
        font-size: 40px;
        font-weight: 750;
        letter-spacing: 0.01em;
    }
    .hero-sub {
        font-size: 17px;
        margin-top: 10px;
        opacity: 0.92;
    }
    .popular-wrapper {
        margin-top: 28px;
        display: flex;
        gap: 16px;
    }
    .popular-card {
        width: 190px;
        border-radius: 18px;
        background: rgba(248, 250, 252, 0.96);
        color: #111827;
        padding: 10px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.5);
        border: 1px solid rgba(148, 163, 184, 0.4);
        transition: transform 0.18s ease-out, box-shadow 0.18s ease-out;
    }
    .popular-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.7);
    }
    .popular-card img {
        border-radius: 14px;
        width: 100%;
        height: 90px;
        object-fit: cover;
        margin-bottom: 8px;
    }
    .search-card {
        position: absolute;
        left: 40px;
        right: 40px;
        bottom: -42px;
        background: rgba(15, 23, 42, 0.96);
        border-radius: 18px;
        padding: 14px 22px;
        box-shadow: 0 18px 45px rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.5);
        backdrop-filter: blur(14px);
    }
    .search-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--text-muted);
        margin-bottom: 4px;
    }

    /* MAIN AREA */
    .main .block-container {
        padding-top: 32px;
    }

    /* SIDEBAR (LEFT PANEL) */
    section[data-testid="stSidebar"] {
        background: radial-gradient(circle at top, #020617 0%, #020617 40%, #000 100%);
    }
    section[data-testid="stSidebar"] > div {
        padding-top: 18px;
    }
    .sidebar-card {
        background: var(--bg-panel);
        border-radius: 20px;
        padding: 18px 16px 24px 16px;
        box-shadow: 0 18px 50px rgba(0, 0, 0, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.45);
        backdrop-filter: blur(18px);
    }
    .sidebar-title {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 18px;
        font-weight: 600;
        color: var(--text-main);
        margin-bottom: 10px;
    }
    .sidebar-title-pill {
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-strong) 100%);
        border-radius: 999px;
        padding: 4px 10px;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: #0b1120;
        font-weight: 600;
    }
    .sidebar-section-label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--text-muted);
        margin-top: 14px;
        margin-bottom: 4px;
    }
    .sidebar-tag-budget { color: #facc15; }
    .sidebar-tag-flight { color: #38bdf8; }
    .sidebar-tag-essentials { color: #4ade80; }

    .sidebar-card label {
        color: var(--text-main) !important;
        font-size: 14px;
    }
    .sidebar-card .stRadio > label,
    .sidebar-card .stCheckbox > label {
        padding-left: 4px;
    }

    /* PRIMARY BUTTONS */
    .stButton button, .stDownloadButton button {
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-strong) 100%) !important;
        color: #0b1120 !important;
        border-radius: 999px !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 12px 30px rgba(8, 47, 73, 0.75) !important;
        transition: transform 0.14s ease-out, box-shadow 0.14s ease-out, filter 0.14s ease-out;
    }
    .stButton button:hover, .stDownloadButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 16px 40px rgba(8, 47, 73, 0.9) !important;
        filter: brightness(1.05);
    }

    /* HEADINGS */
    h2, h3 {
        color: var(--text-main);
        letter-spacing: 0.02em;
    }

    /* FLIGHT SECTION PILL */
    .flight-section-title {
        background: var(--accent-soft);
        color: var(--accent);
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 999px;
        font-weight: 600;
        margin-bottom: 18px;
        border: 1px solid rgba(56, 189, 248, 0.5);
    }

    /* FLIGHT CARDS */
    .flight-card {
        border-radius: 18px;
        padding: 18px;
        text-align: center;
        background: radial-gradient(circle at top left, #f9fafb 0%, #e5e7eb 40%, #d4d4d8 100%);
        margin-bottom: 20px;
        box-shadow: 0 14px 32px rgba(15, 23, 42, 0.55);
        border: 1px solid rgba(148, 163, 184, 0.7);
        transition: transform 0.18s ease-out, box-shadow 0.18s ease-out;
    }
    .flight-card:hover {
        transform: translateY(-4px) scale(1.01);
        box-shadow: 0 20px 45px rgba(15, 23, 42, 0.8);
    }

    /* FOOTER STRIP */
    .footer-strip {
        margin-top: 32px;
        padding: 10px 14px;
        border-radius: 999px;
        background: rgba(15, 23, 42, 0.92);
        color: var(--text-muted);
        font-size: 12px;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        border: 1px solid rgba(148, 163, 184, 0.5);
        backdrop-filter: blur(12px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============== HERO + SEARCH BAR ==============

# default values (will be overwritten by search card)
source_city_default = "Hyderabad"
destination_city_default = "Delhi"

with st.container():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">Spend your vacation<br>with our activities</div>
            <div class="hero-sub">Mountains • Plains • Beaches – curated trips tailored to your mood.</div>
            <div class="popular-wrapper">
                <div class="popular-card">
                    <img src="https://images.pexels.com/photos/325807/pexels-photo-325807.jpeg" />
                    <strong>Trip to Scotland</strong><br>
                    <span style="font-size:12px;color:#777;">31 people going</span>
                </div>
                <div class="popular-card">
                    <img src="https://images.pexels.com/photos/261102/pexels-photo-261102.jpeg" />
                    <strong>Trip to Egypt</strong><br>
                    <span style="font-size:12px;color:#777;">27 people going</span>
                </div>
                <div class="popular-card">
                    <img src="https://images.pexels.com/photos/460672/pexels-photo-460672.jpeg" />
                    <strong>Trip to Greece</strong><br>
                    <span style="font-size:12px;color:#777;">29 people going</span>
                </div>
            </div>
            <div class="search-card">
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4, c5 = st.columns([2.2, 2.2, 1.6, 1.6, 1.1])
    with c1:
        st.markdown('<div class="search-label">From (city)</div>', unsafe_allow_html=True)
        source_city = st.text_input("from_city", source_city_default, label_visibility="collapsed")
    with c2:
        st.markdown('<div class="search-label">To (city)</div>', unsafe_allow_html=True)
        destination_city = st.text_input("to_city", destination_city_default, label_visibility="collapsed")
    with c3:
        st.markdown('<div class="search-label">Check‑in</div>', unsafe_allow_html=True)
        departure_date = st.date_input("dep_date", label_visibility="collapsed")
    with c4:
        st.markdown('<div class="search-label">Check‑out</div>', unsafe_allow_html=True)
        return_date = st.date_input("ret_date", label_visibility="collapsed")
    with c5:
        st.markdown('<div class="search-label">&nbsp;</div>', unsafe_allow_html=True)
        search_clicked = st.button("Search", use_container_width=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

# below hero: other controls (theme, sidebar, etc.)

st.markdown("")

# ============== REST OF INPUTS ==============

def format_datetime(iso_string: str) -> str:
    try:
        dt = datetime.strptime(iso_string, "%Y-%m-%d %H:%M")
        return dt.strftime("%b-%d, %Y | %I:%M %p")
    except Exception:
        return "N/A"

st.markdown("### 🎭 Trip details")
num_days = st.slider("🕒 Trip Duration (days):", 1, 14, 5)
travel_theme = st.selectbox(
    "Select your travel theme:",
    ["💑 Couple Getaway", "👨‍👩‍👧‍👦 Family Vacation", "🏔️ Adventure Trip", "🧳 Solo Exploration"],
)

activity_preferences = st.text_area(
    "What activities do you enjoy?",
    "Relaxing on the beach, exploring historical sites",
)

# sidebar
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-card">
            <div class="sidebar-title">
                🧭 Travel Assistant
                <span class="sidebar-title-pill">Smart planner</span>
            </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-section-label">'
        '<span class="sidebar-tag-budget">●</span> Budget preference'
        '</div>',
        unsafe_allow_html=True,
    )
    budget = st.radio("", ["Economy", "Standard", "Luxury"], index=0)

    st.markdown(
        '<div class="sidebar-section-label">'
        '<span class="sidebar-tag-flight">●</span> Flight class'
        '</div>',
        unsafe_allow_html=True,
    )
    flight_class = st.radio("", ["Economy", "Business", "First Class"], index=0)

    st.markdown(
        '<div class="sidebar-section-label">Preferred hotel rating</div>',
        unsafe_allow_html=True,
    )
    hotel_rating = st.selectbox("", ["Any", "3⭐", "4⭐", "5⭐"])

    st.markdown(
        '<div class="sidebar-section-label">Packing checklist</div>',
        unsafe_allow_html=True,
    )
    packing_items = {
        "👕 Clothes": True,
        "🩴 Comfortable Footwear": True,
        "🕶️ Sunglasses & Sunscreen": False,
        "📖 Travel Guidebook": False,
        "💊 Medications & First-Aid": True,
    }
    for item, checked in packing_items.items():
        st.checkbox(item, value=checked)

    st.markdown(
        '<div class="sidebar-section-label">'
        '<span class="sidebar-tag-essentials">●</span> Travel essentials'
        '</div>',
        unsafe_allow_html=True,
    )
    visa_required = st.checkbox("🛃 Check Visa Requirements")
    travel_insurance = st.checkbox("🛡️ Get Travel Insurance")
    currency_converter = st.checkbox("💱 Currency Exchange Rates")

    st.markdown("</div>", unsafe_allow_html=True)



# ============== IATA FROM CITY NAMES ==============

def choose_iata(city_name: str, fallback_default: str, key_prefix: str):
    airports = get_airport_options(city_name)
    if airports:
        label = st.selectbox(
            f"{key_prefix}_airport",
            [f"{name} ({code})" for name, code in airports],
            label_visibility="collapsed",
        )
        return label.split("(")[-1].replace(")", "").strip()
    else:
        return st.text_input(f"{key_prefix}_iata", fallback_default, label_visibility="collapsed")

source = choose_iata(source_city, "HYD", "from_iata")
destination = choose_iata(destination_city, "DEL", "to_iata")

# ============== SERPAPI HELPERS ==============

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
    token = flight.get("booking_token")
    if token:
        return f"https://www.google.com/travel/flights?tfs={token}"
    return (
        "https://www.google.com/travel/flights?"
        f"q=flights+from+{source}+to+{destination}"
        f"+on+{departure_date}+return+{return_date}"
    )

# ============== MAIN ACTION ==============

if search_clicked:
    # 1) Flights
    with st.spinner("✈️ Finding the best real-time flight options for you..."):
        try:
            flight_data = fetch_flights(source, destination, departure_date, return_date)
            cheapest_flights = extract_cheapest_flights(flight_data)
        except Exception as e:
            st.error(f"Error fetching flights: {e}")
            cheapest_flights = []

    # Prepare summary + prices
    flight_summary = "No flights found."
    min_price = max_price = avg_price = None
    if cheapest_flights:
        lines, prices = [], []
        for f in cheapest_flights:
            p = f.get("price")
            if isinstance(p, (int, float)):
                prices.append(p)
            lines.append(
                f"- {f.get('airline', 'Airline')} | ₹{p} | {f.get('total_duration', 'N/A')} min"
            )
        flight_summary = "\n".join(lines)
        if prices:
            min_price, max_price = min(prices), max(prices)
            avg_price = sum(prices) / len(prices)

    # 2) AI itinerary
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

Real flight options (from SerpAPI / Google Flights):
{flight_summary}

Cost information:
{budget_hint}

Use the flight price range and budget level to choose realistic hotels, activities,
and total budget in INR.

Return a Markdown-formatted answer with:
- Overview
- Best flight choice + reasoning
- 3 hotel suggestions (area + rough nightly price)
- Day-by-day itinerary ({num_days} days; morning/afternoon/evening)
- Cost breakdown (flights, hotels, food/local travel, activities)
- One-line summary about whether it fits a typical {budget} Indian traveller.
                """
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful, detail-oriented travel planner for Indian travellers.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                )
                ai_itinerary = completion.choices[0].message.content
            except Exception as e:
                ai_itinerary = f"AI Error: {e}"

    # ============== DISPLAY FLIGHTS ==============

    st.markdown('<div class="flight-section-title">✈️ Cheapest Flight Options (Live from SerpAPI)</div>', unsafe_allow_html=True)
    if cheapest_flights:
        cols = st.columns(len(cheapest_flights))
        for i, f in enumerate(cheapest_flights):
            with cols[i]:
                logo = f.get("airline_logo", "")
                airline = f.get("airline", "Unknown Airline")
                price = f.get("price", "Not Available")
                duration = f.get("total_duration", "N/A")
                flights_info = f.get("flights", [{}])
                dep = flights_info[0].get("departure_airport", {})
                arr = flights_info[-1].get("arrival_airport", {})
                dep_time = format_datetime(dep.get("time", "N/A"))
                arr_time = format_datetime(arr.get("time", "N/A"))
                booking_link = build_booking_link(f)

                st.markdown(
                    f"""
                    <div class="flight-card">
                        <img src="{logo}" width="80" alt="Flight Logo" />
                        <h3 style="margin: 10px 0;">{airline}</h3>
                        <p><strong>Departure:</strong> {dep_time}</p>
                        <p><strong>Arrival:</strong> {arr_time}</p>
                        <p><strong>Duration:</strong> {duration} min</p>
                        <h2 style="color: #008000; margin-top: 4px;">💰 {price}</h2>
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
            st.info(f"💡 Flight price summary: min ₹{min_price}, max ₹{max_price}, avg ≈ ₹{int(avg_price)}")
    else:
        st.warning("⚠️ No flight data available. Try changing dates or airports.")

    # ============== DISPLAY ITINERARY ==============

    st.subheader("🗺️ Your AI Itinerary (Budget‑Aware)")
    st.markdown(ai_itinerary)
st.markdown(
    '<div class="footer-strip">✨ Built for Indian travellers • Live fares by SerpAPI • Itineraries by AI</div>',
    unsafe_allow_html=True,
)


