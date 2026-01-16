import streamlit as st
import requests
import google.generativeai as genai
from streamlit_js_eval import streamlit_js_eval

# --- PROFESSIONAL UI CONFIG ---
st.set_page_config(page_title="Vertex SkyCast AI", page_icon="🌤️", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 12px; border: 1px solid #4A90E2; }
    .advice-box { background-color: #262730; padding: 20px; border-radius: 10px; border-left: 5px solid #4A90E2; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- API SETUP ---
try:
    OWM_KEY = st.secrets["OPENWEATHER_API_KEY"]
    GENAI_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GENAI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"⚠️ API Key Error: Ensure OPENWEATHER_API_KEY and GEMINI_API_KEY are in secrets.toml")
    st.stop()

# --- DATA FETCHING ---
def get_weather(lat=None, lon=None, city=None, unit_code="metric"):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"appid": OWM_KEY, "units": unit_code}
    
    if lat and lon:
        params["lat"] = lat
        params["lon"] = lon
    elif city:
        params["q"] = city
    else:
        return None

    try:
        res = requests.get(base_url, params=params)
        return res.json() if res.status_code == 200 else None
    except:
        return None

# --- AI LOGIC ---
def clean_data_for_ai(data, unit):
    return (f"Location: {data.get('name')}, Temp: {data['main']['temp']} {unit}, "
            f"Humidity: {data['main']['humidity']}%, Condition: {data['weather'][0]['description']}, "
            f"Wind: {data['wind']['speed']}")

def get_short_insight(data, unit):
    clean_info = clean_data_for_ai(data, unit)
    prompt = f"Given weather: {clean_info}. Provide 1 short, punchy sentence of outfit advice. No jargon."
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Enjoy the weather! Stay safe and hydrated."

def get_chat_response(query, data, unit):
    clean_info = clean_data_for_ai(data, unit)
    prompt = f"""
    Context: {clean_info}. User asks: {query}
    Rules: 1. Start with a Direct Bold Answer. 2. Bullet points for reasons. 3. Short Pro-Tip. 4. Friendly tone.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "⚠️ AI is currently at capacity. Please try again in a moment!"

# --- APP LAYOUT ---
st.title("🌤️ Vertex SkyCast AI")
st.caption("Real-Time Weather Intelligence • Powered by Gemini 1.5 Flash")

# --- CONTROLS ---
col1, col2 = st.columns([1, 1])
with col1:
    st.write("#### 📍 Live GPS")
    if st.button("Detect My Location"):
        # 1. Attempt High-Accuracy Browser GPS
        loc = streamlit_js_eval(data_of='geolocation', stop_after_once=True, key='gps_final')
        
        if loc:
            st.session_state.lat = loc['coords']['latitude']
            st.session_state.lon = loc['coords']['longitude']
            st.session_state.mode = "gps"
            st.rerun()
        else:
            # 2. Fallback to IP-based Geolocation if Browser GPS fails/blocked
            with st.spinner("GPS blocked or unavailable. Using IP fallback..."):
                try:
                    ip_data = requests.get('https://ipapi.co/json/').json()
                    if 'latitude' in ip_data:
                        st.session_state.lat = ip_data['latitude']
                        st.session_state.lon = ip_data['longitude']
                        st.session_state.mode = "gps"
                        st.rerun()
                except:
                    st.warning("Could not detect location. Please use manual search.")

with col2:
    st.write("#### 🔍 City Search")
    city_input = st.text_input("City", placeholder="Enter city (e.g. Coimbatore)...", label_visibility="collapsed")
    if city_input:
        st.session_state.city = city_input
        st.session_state.mode = "manual"

unit = st.radio("Unit:", ["Celsius", "Fahrenheit"], horizontal=True)
unit_code = "metric" if unit == "Celsius" else "imperial"
unit_symbol = "C" if unit == "Celsius" else "F"

# --- ENGINE ---
data = None
if st.session_state.get("mode") == "gps" and "lat" in st.session_state:
    data = get_weather(lat=st.session_state.lat, lon=st.session_state.lon, unit_code=unit_code)
elif st.session_state.get("mode") == "manual" and "city" in st.session_state:
    data = get_weather(city=st.session_state.city, unit_code=unit_code)

# --- DISPLAY ---
if data:
    st.divider()
    
    # 1. AI Insight
    with st.spinner("Analyzing atmosphere..."):
        insight = get_short_insight(data, unit_symbol)
    
    st.header(f"📍 {data['name']}, {data['sys']['country']}")
    st.info(f"💡 **AI Insight:** {insight}")
    
    # 2. Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Temperature", f"{data['main']['temp']}°{unit_symbol}")
    c2.metric("Feels Like", f"{data['main']['feels_like']}°{unit_symbol}")
    c3.metric("Humidity", f"{data['main']['humidity']}%")
    c4.metric("Wind Speed", f"{data['wind']['speed']} {'m/s' if unit=='Celsius' else 'mph'}")

    # 3. Chat
    st.markdown("### 💬 Ask the AI Weather Consultant")
    query = st.text_input("Ask about your plans:", placeholder="Should I wear a hoodie? Can I go for a run?")
    if query:
        with st.spinner("Consulting Gemini..."):
            response = get_chat_response(query, data, unit_symbol)
            st.markdown(f'<div class="advice-box">{response}</div>', unsafe_allow_html=True)

else:
    if st.session_state.get("mode"):
        st.error("Location data unavailable. Please try searching for your city manually.")
    else:
        st.info("👋 Use 'Detect My Location' or enter a city to start.")

# --- FOOTER ---
st.markdown("---")
with st.sidebar:
    st.title("🏆 Internship Portfolio")
    st.success("Task 2: Weather AI Dashboard")
    st.write("Developer: **Hemavarni S**")
    st.divider()
    st.caption("Data: OpenWeatherMap | AI: Gemini 1.5 Flash")