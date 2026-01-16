import streamlit as st
import requests
import google.generativeai as genai
from streamlit_js_eval import streamlit_js_eval

# --- CONFIG ---
st.set_page_config(page_title="Vertex SkyCast AI", page_icon="🌤️", layout="wide")

# --- API SETUP ---
try:
    OWM_KEY = st.secrets["OPENWEATHER_API_KEY"]
    GENAI_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GENAI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("🔑 API Keys missing or invalid in Secrets.")
    st.stop()

# --- STYLES ---
st.markdown("""
    <style>
    .stMetric { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 12px; border: 1px solid #4A90E2; }
    .advice-box { background-color: #262730; padding: 20px; border-radius: 10px; border-left: 5px solid #4A90E2; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCTIONS ---
def get_weather(lat=None, lon=None, city=None, unit_code="metric"):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"appid": OWM_KEY, "units": unit_code}
    if lat and lon: params.update({"lat": lat, "lon": lon})
    elif city: params["q"] = city
    else: return None
    try:
        res = requests.get(url, params=params)
        return res.json() if res.status_code == 200 else None
    except: return None

def get_ai_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        if "429" in str(e): return "⏳ AI is taking a quick breather (Rate limit). Try again in 30 seconds!"
        return "⛅ Focus on the weather metrics while I reconnect!"

# --- LOCATION LOGIC ---
def get_fallback_loc():
    # Try Service A
    try:
        data = requests.get('http://ip-api.com/json/').json()
        return data['lat'], data['lon']
    except:
        # Try Service B
        try:
            data = requests.get('https://ipinfo.io/json').json()
            loc = data['loc'].split(',')
            return float(loc[0]), float(loc[1])
        except: return None, None

# --- UI ---
st.title("🌤️ Vertex SkyCast AI")
st.caption("Intelligence via Gemini 1.5 Flash • Global Real-Time Data")

c1, c2 = st.columns([1, 1])
with c1:
    st.write("#### 📍 Live GPS")
    if st.button("Detect My Location"):
        # Try Browser GPS
        loc = streamlit_js_eval(data_of='geolocation', stop_after_once=True, key='gps')
        if loc:
            st.session_state.lat, st.session_state.lon = loc['coords']['latitude'], loc['coords']['longitude']
            st.session_state.mode = "gps"
            st.rerun()
        else:
            # Try Multi-Service IP Fallback
            lat, lon = get_fallback_loc()
            if lat:
                st.session_state.lat, st.session_state.lon = lat, lon
                st.session_state.mode = "gps"
                st.rerun()
            else: st.warning("Location services unavailable. Please search manually.")

with c2:
    st.write("#### 🔍 City Search")
    city = st.text_input("City", placeholder="Enter city...", label_visibility="collapsed")
    if city:
        st.session_state.city, st.session_state.mode = city, "manual"

unit = st.radio("Unit:", ["Celsius", "Fahrenheit"], horizontal=True)
u_code = "metric" if unit == "Celsius" else "imperial"
u_sym = "C" if unit == "Celsius" else "F"

# --- RENDER ---
data = None
if st.session_state.get("mode") == "gps":
    data = get_weather(lat=st.session_state.lat, lon=st.session_state.lon, unit_code=u_code)
elif st.session_state.get("mode") == "manual":
    data = get_weather(city=st.session_state.city, unit_code=u_code)

if data:
    st.divider()
    st.header(f"📍 {data['name']}, {data['sys']['country']}")
    
    # Smart Insight
    with st.spinner("AI Analysis..."):
        desc = data['weather'][0]['description']
        insight = get_ai_response(f"Weather: {data['main']['temp']}{u_sym}, {desc}. Give 1 sentence of outfit advice.")
        st.info(f"💡 **AI Insight:** {insight}")

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Temp", f"{data['main']['temp']}°{u_sym}")
    m2.metric("Feels Like", f"{data['main']['feels_like']}°{u_sym}")
    m3.metric("Humidity", f"{data['main']['humidity']}%")
    m4.metric("Wind", f"{data['wind']['speed']}")

    # Chat
    st.markdown("### 💬 Ask the Consultant")
    query = st.text_input("Example: 'Is it good for a picnic?'")
    if query:
        with st.spinner("Thinking..."):
            ans = get_ai_response(f"Weather: {data['name']}, {data['main']['temp']}{u_sym}, {desc}. User: {query}. Rules: Bold answer, bullets for reasons.")
            st.markdown(f'<div class="advice-box">{ans}</div>', unsafe_allow_html=True)
else:
    st.info("👋 Detect location or search for a city to begin.")