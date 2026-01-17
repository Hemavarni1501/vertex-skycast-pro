import streamlit as st
import requests
from google import genai

# --- CONFIG ---
st.set_page_config(page_title="Vertex SkyCast AI", page_icon="🌤️", layout="wide")

# --- API SETUP ---
try:
    OWM_KEY = st.secrets["OPENWEATHER_API_KEY"]
    GENAI_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=GENAI_KEY)
except Exception:
    st.error("🔑 API Keys missing or invalid in Secrets.")
    st.stop()

# --- STYLES (No Changes) ---
st.markdown("""
    <style>
    .stMetric { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 12px; border: 1px solid #4A90E2; }
    .advice-box { background-color: #262730; padding: 20px; border-radius: 10px; border-left: 5px solid #4A90E2; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCTIONS ---
def get_ai_response(prompt):
    try:
        # UPDATED: Using gemini-2.5-flash-lite for better free-tier access in 2026
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite', 
            contents=prompt
        )
        return response.text
    except Exception as e:
        # Catch and display the specific reason for failure
        if "429" in str(e):
            return "⏳ AI is in high demand (Rate Limit). Please wait 60 seconds and search again!"
        return None

# --- UI & LOGIC ---
st.title("🌤️ Vertex SkyCast AI")
st.caption("AI-Powered Weather Intelligence • Powered by Gemini 2.5 Flash-Lite")

# Single Search Bar
st.write("#### 🔍 Search Your City")
city_input = st.text_input("City Name", placeholder="e.g. Coimbatore, London, Tokyo", label_visibility="collapsed")
unit = st.radio("Display Unit:", ["Celsius", "Fahrenheit"], horizontal=True)
u_code = "metric" if unit == "Celsius" else "imperial"
u_sym = "C" if unit == "Celsius" else "F"

if city_input:
    w_url = f"https://api.openweathermap.org/data/2.5/weather?q={city_input}&appid={OWM_KEY}&units={u_code}"
    res = requests.get(w_url)
    
    if res.status_code == 200:
        data = res.json()
        st.divider()
        st.header(f"📍 {data['name']}, {data['sys']['country']}")
        
        # 1. AI Short Insight
        with st.spinner("AI Analysis..."):
            desc = data['weather'][0]['description']
            ai_prompt = f"Weather: {data['main']['temp']}{u_sym}, {desc}. 1 short outfit tip."
            insight = get_ai_response(ai_prompt)
            if insight:
                st.info(f"💡 **AI Insight:** {insight}")
            else:
                st.warning("💡 **AI Insight:** AI is currently warming up. Follow the metrics below!")

        # 2. Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Temperature", f"{data['main']['temp']}°{u_sym}")
        m2.metric("Feels Like", f"{data['main']['feels_like']}°{u_sym}")
        m3.metric("Humidity", f"{data['main']['humidity']}%")
        m4.metric("Wind Speed", f"{data['wind']['speed']} m/s")

        # 3. AI Consultant
        st.markdown("### 💬 Ask the Consultant")
        query = st.text_input("Ask about your plans:", placeholder="Example: 'Should I go for a bike ride?'")
        if query:
            with st.spinner("Consulting..."):
                ans_prompt = f"Weather in {data['name']}: {data['main']['temp']}{u_sym}, {desc}. Question: {query}. Answer briefly in bold with 2 bullets."
                ans = get_ai_response(ans_prompt)
                if ans:
                    st.markdown(f'<div class="advice-box">{ans}</div>', unsafe_allow_html=True)
                else:
                    st.error("AI is momentarily offline. Try again in a minute!")
    else:
        st.error("⚠️ City not found.")

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏆 Internship Task 2")
    st.markdown("---")
    st.write("**Developer:** Hemavarni S")
    st.write("**Tech Stack:** Streamlit, OpenWeatherMap, Gemini 2.5")
    st.success("System Status: Online")
    st.markdown("---")