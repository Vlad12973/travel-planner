import streamlit as st
from datetime import datetime
import json

st.set_page_config(page_title="🌍 AI Travel Planner", layout="wide")

# Beautiful theme
st.markdown("""
<style>
.title {text-align: center; font-size: 48px; font-weight: bold; color: #ff5733;}
.subtitle {text-align: center; font-size: 24px; color: #555;}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="title">✈️ AI Travel Planner</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Plan your dream trip - No API keys needed!</p>', unsafe_allow_html=True)

# Inputs
col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🌍 Trip Details")
    source = st.text_input("🛫 From (e.g., BOM)", "BOM")
    destination = st.text_input("🛬 To (e.g., DEL)", "DEL")
    
with col2:
    st.markdown("### 📅 Dates")
    departure_date = st.date_input("Departure")
    return_date = st.date_input("Return")

st.markdown("### 🎯 Preferences")
num_days = st.slider("Trip Duration", 1, 14, 5)
travel_theme = st.selectbox("Travel Style", ["Couple", "Family", "Adventure", "Solo"])
budget = st.selectbox("Budget", ["Economy", "Standard", "Luxury"])
activities = st.text_area("Activities you love", "beach, sightseeing, food")

# Sidebar
st.sidebar.title("✨ Quick Tips")
st.sidebar.info("✅ No login required\n✅ Works worldwide\n✅ Share with friends!")

if st.button("🚀 Generate My Travel Plan", type="primary"):
    st.balloons()
    
    # Mock flight data (realistic prices)
    flights = [
        {"airline": "IndiGo", "price": "₹4500", "duration": "2h 15m", "time": "08:00-10:15"},
        {"airline": "Air India", "price": "₹5200", "duration": "2h 30m", "time": "11:30-14:00"},
        {"airline": "Vistara", "price": "₹6800", "duration": "2h 45m", "time": "15:00-17:45"}
    ]
    
    # Personalized itinerary
    itinerary = f"""
## ✈️ **Best Flights Found**
| Airline | Price | Duration | Timing |
|---------|-------|----------|--------|
| {flights[0]['airline']} | {flights[0]['price']} | {flights[0]['duration']} | {flights[0]['time']} |
| {flights[1]['airline']} | {flights[1]['price']} | {flights[1]['duration']} | {flights[1]['time']} |
| {flights[2]['airline']} | {flights[2]['price']} | {flights[2]['duration']} | {flights[2]['time']} |

## 🏨 **Recommended Hotels** ({budget})
- **4⭐ Hotel**: Clean, central location (~₹4000/night)
- **3⭐ Hotel**: Budget-friendly (~₹2000/night)

## 🗺️ **{num_days}-Day {travel_theme} Itinerary**
### Day 1: Arrival & Exploration
- Morning: Land in {destination}, check-in hotel
- Afternoon: {activities.split(',')[0]} 
- Evening: Local dinner (₹800/person)

### Day 2-{num_days}: Adventure Time
- Morning activities: {activities}
- Cultural sites & shopping
- Nightlife or relaxation

**Total Estimated Cost**: ₹25,000 - ₹45,000 ({budget})
    """
    
    st.markdown("### ✅ **Your Personalized Plan**")
    st.markdown(itinerary)
    st.success("✨ Plan ready! Share this link with friends 👇")
