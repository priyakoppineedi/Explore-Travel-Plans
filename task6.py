import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime

with open(r"D:/Docu/pyjunb/API_keys/API_key2_innomatics.txt") as f:
    key = f.read().strip()
genai.configure(api_key=key)

def get_travel_options(source,destination,date):
    model = genai.GenerativeModel("gemini-1.5-pro")  
    prompt = f"""
    You are a travel assistant. Provide structured travel options from {source} to {destination} on {date}.
    Include:
    - Flights (airline, departure time, arrival time, duration, cost)
    - Trains (train name, departure time, arrival time, duration, cost)
    - Buses (operator, departure time, arrival time, duration, cost)
    - Cabs (estimated cost, duration)
    Return ONLY valid JSON. Example:
    {{
        "flights": [{{"airline": "IndiGo", "departure": "06:00", "arrival": "08:05", "duration": "2h 05m", "cost": 12000}}],
        "trains": [{{"name": "Rajdhani Express", "departure": "18:00", "arrival": "08:00", "duration": "14h", "cost": 2500}}],
        "buses": [{{"operator": "VRL Travels", "departure": "21:00", "arrival": "07:00", "duration": "10h", "cost": 1500}}],
        "cabs": [{{"cost": 8000, "duration": "9h"}}]
    }}
    """
    try:
        response = model.generate_content(prompt)
        if response.candidates:
            response_text = response.candidates[0].content.parts[0].text.strip()
        else:
            return {"error":"No response from AI. Please try again."}
        response_text = response_text.replace("```json","").replace("```","").strip()
        travel_data = json.loads(response_text)
        return travel_data
    except Exception as e:
        return {"error":str(e)}

def generate_summary(travel_data):
    summary = "### 🔹 Travel Recommendations Summary:\n"
    all_options = []
    if "flights" in travel_data:
        all_options.extend([("Flight",flight["cost"]) for flight in travel_data["flights"]])
    if "trains" in travel_data:
        all_options.extend([("Train",train["cost"]) for train in travel_data["trains"]])
    if "buses" in travel_data:
        all_options.extend([("Bus",bus["cost"]) for bus in travel_data["buses"]])
    if "cabs" in travel_data:
        all_options.extend([("Cab",cab["cost"]) for cab in travel_data["cabs"]])
    if all_options:
        best_option = min(all_options,key=lambda x:x[1])
        summary += f"✔️ The cheapest option is **{best_option[0]}** at ₹{best_option[1]}.\n"
    if "flights" in travel_data:
        summary += "⚡ The fastest option is **Flight** (around 1-2 hours).\n"
    return summary

st.title("🌍 AI-Powered Travel Planner")
st.write("Find the best travel options between your source and destination.")
source = st.text_input("Enter Source Location")
destination = st.text_input("Enter Destination")
date = st.date_input("Select Travel Date",min_value=datetime.today())

if st.button("Explore Travel Plans",use_container_width=True):
    if source and destination:
        result = get_travel_options(source,destination,date.strftime("%Y-%m-%d"))
        if "error" in result:
            st.error(result["error"])
        else:
            st.write(f"Okay, I have found the best travel options from **{source}** to **{destination}** on **{date.strftime('%B %d, %Y')}**.")
            st.write("---")
            summary = generate_summary(result)
            st.markdown(summary)
            if result.get("flights"):
                st.subheader("✈️ Flights")
                for flight in result["flights"]:
                    st.markdown(f"""
                    - **{flight['airline']}**
                      - 🕒 Departure: {flight['departure']}
                      - 🛬 Arrival: {flight['arrival']}
                      - ⏳ Duration: {flight['duration']}
                      - 💰 Price: ₹{flight['cost']}
                    """)
            if result.get("trains"):
                st.subheader("🚆 Trains")
                for train in result["trains"]:
                    st.markdown(f"""
                    - **{train['name']}**
                      - 🕒 Departure: {train['departure']}
                      - 🛬 Arrival: {train['arrival']}
                      - ⏳ Duration: {train['duration']}
                      - 💰 Price: ₹{train['cost']}
                    """)
            if result.get("buses"):
                st.subheader("🚌 Buses")
                for bus in result["buses"]:
                    st.markdown(f"""
                    - **{bus['operator']}**
                      - 🕒 Departure: {bus['departure']}
                      - 🛬 Arrival: {bus['arrival']}
                      - ⏳ Duration: {bus['duration']}
                      - 💰 Price: ₹{bus['cost']}
                    """)
            if result.get("cabs"):
                st.subheader("🚖 Cabs")
                for cab in result["cabs"]:
                    st.markdown(f"""
                    - **Private Cab**
                      - ⏳ Duration: {cab['duration']}
                      - 💰 Price: ₹{cab['cost']}
                    """)
    else:
        st.error("Please enter both source and destination.")
