import streamlit as st
import requests
import google.generativeai as genai

# --- CONFIG ---
st.set_page_config(page_title="Vertex SkyCast AI", page_icon="🌤️", layout="wide")

# --- API SETUP ---
try:
    OWM_KEY = st.secrets["OPENWEATHER_API_KEY"]
    GENAI_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GENAI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("🔑 API Keys missing or invalid in Secrets. Please check your secrets.toml.")
    st.stop()

# --- STYLES ---
st.markdown("""
    <style>
    .stMetric { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 12px; border: 1px solid #4A90E2; }
    .advice-box { background-color: #262730; padding: 20px; border-radius: 10px; border-left: 5px solid #4A90E2; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCTIONS ---
def get_weather(city, unit_code="metric"):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": OWM_KEY, "units": unit_code}
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

# --- UI ---
st.title("🌤️ Vertex SkyCast AI")
st.caption("AI-Powered Weather Intelligence • Powered by Gemini 1.5 Flash")

# Single Search Bar
st.write("#### 🔍 Search Your City")
city_input = st.text_input("City Name", placeholder="e.g. Coimbatore, London, Tokyo", label_visibility="collapsed")

# Unit Selection below search
unit = st.radio("Display Unit:", ["Celsius", "Fahrenheit"], horizontal=True)
u_code = "metric" if unit == "Celsius" else "imperial"
u_sym = "C" if unit == "Celsius" else "F"

# --- RENDER ---
if city_input:
    data = get_weather(city_input, u_code)
    
    if data:
        st.divider()
        st.header(f"📍 {data['name']}, {data['sys']['country']}")
        
        # 1. AI Short Insight
        with st.spinner("AI Analysis..."):
            desc = data['weather'][0]['description']
            insight = get_ai_response(f"Weather: {data['main']['temp']}{u_sym}, {desc}. Provide 1 punchy sentence of outfit advice.")
            st.info(f"💡 **AI Insight:** {insight}")

        # 2. Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Temperature", f"{data['main']['temp']}°{u_sym}")
        m2.metric("Feels Like", f"{data['main']['feels_like']}°{u_sym}")
        m3.metric("Humidity", f"{data['main']['humidity']}%")
        m4.metric("Wind Speed", f"{data['wind']['speed']}")

        # 3. AI Chat Consultant
        st.markdown("### 💬 Ask the Consultant")
        query = st.text_input("Ask about your plans:", placeholder="Example: 'Should I go for a bike ride?'")
        
        if query:
            with st.spinner("Consulting..."):
                ans_prompt = f"""
                Weather in {data['name']}: {data['main']['temp']}{u_sym}, {desc}. 
                User Question: {query}
                Instructions: Answer directly in bold first. Use 2-3 bullet points for reasons. Keep it short.
                """
                ans = get_ai_response(ans_prompt)
                st.markdown(f'<div class="advice-box">{ans}</div>', unsafe_allow_html=True)
    else:
        st.error("⚠️ City not found. Please check the spelling and try again.")
else:
    st.info("👋 Enter a city name above to see the weather intelligence.")

# --- SIDEBAR PORTFOLIO INFO ---
with st.sidebar:
    st.title("🏆 Internship Task 2")
    st.markdown("---")
    st.write("**Developer:** Hemavarni S")
    st.write("**Tech Stack:** Streamlit, OpenWeatherMap, Google Gemini 1.5 Flash")
    st.success("System Status: Online")
    st.markdown("---")