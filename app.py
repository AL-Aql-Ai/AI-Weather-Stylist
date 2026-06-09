# app.py
import streamlit as st
import requests
from groq import Groq
import re
from datetime import datetime

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================
st.set_page_config(
    page_title="AI Weather Stylist Pro",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# STYLING
# ==========================================================
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .result-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin-top: 1rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# API CONFIGURATION
# ==========================================================
def initialize_apis():
    """Initialize API clients with error handling"""
    try:
        # For Streamlit Cloud deployment, use secrets
        openweather_key = st.secrets.get("OPENWEATHER_API_KEY", "")
        groq_key = st.secrets.get("GROQ_API_KEY", "")
        
        # Fallback to session state or environment variables
        if not groq_key:
            groq_key = st.session_state.get("groq_key", "")
        
        if groq_key:
            groq_client = Groq(api_key=groq_key)
            return openweather_key, groq_client
        return openweather_key, None
        
    except Exception as e:
        st.error(f"API initialization error: {e}")
        return "", None

# ==========================================================
# WEATHER API FUNCTIONS
# ==========================================================
@st.cache_data(ttl=1800)  # Cache weather data for 30 minutes
def get_weather(city, api_key):
    """Fetch weather data with caching"""
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric"
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "city": data["name"],
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }
        
    except requests.exceptions.RequestException as e:
        st.error(f"Weather API error: {e}")
        return {"error": f"Could not fetch weather for {city}"}
    except Exception as e:
        return {"error": str(e)}

# ==========================================================
# HEALTH METRICS
# ==========================================================
def calculate_bmi(height_cm, weight_kg):
    """Calculate BMI with health insights"""
    height_m = height_cm / 100
    bmi = round(weight_kg / (height_m ** 2), 1)
    
    if bmi < 18.5:
        category = "Underweight"
        insight = "Focus on building healthy muscle mass"
    elif bmi < 25:
        category = "Normal Weight"
        insight = "Maintain your healthy lifestyle"
    elif bmi < 30:
        category = "Overweight"
        insight = "Consider incorporating more physical activity"
    else:
        category = "Obese"
        insight = "Prioritize health with balanced nutrition and exercise"
    
    return bmi, category, insight

# ==========================================================
# STYLE KNOWLEDGE BASE
# ==========================================================
def get_body_guidance(body_type):
    """Detailed body type styling guidance"""
    guidance = {
        "ectomorph": {
            "description": "Slim, lean build with fast metabolism",
            "tips": "Create visual balance with structured pieces",
            "recommendations": [
                "Layered outfits for depth",
                "Horizontal stripes for width",
                "Fitted but not tight clothing",
                "Textured fabrics for volume"
            ],
            "avoid": ["Oversized clothing", "Very tight fits", "Vertical stripes"]
        },
        "mesomorph": {
            "description": "Athletic, well-proportioned build",
            "tips": "Most styles work well with proper fit",
            "recommendations": [
                "Tailored clothing for sharp looks",
                "V-necks to elongate torso",
                "Fitted jackets and blazers",
                "Clean silhouettes"
            ],
            "avoid": ["Extremely baggy clothing", "Restrictive fits"]
        },
        "endomorph": {
            "description": "Broader, curvier build",
            "tips": "Create vertical lines and structure",
            "recommendations": [
                "Vertical stripes and patterns",
                "V-neck and scoop necklines",
                "Structured blazers and jackets",
                "Monochromatic outfits"
            ],
            "avoid": ["Horizontal stripes", "Bulky fabrics", "Overly tight clothing"]
        }
    }
    return guidance.get(body_type, guidance["mesomorph"])

def get_undertone_guidance(undertone):
    """Color guidance based on skin undertone"""
    guidance = {
        "warm": {
            "colors": ["Olive", "Mustard", "Coral", "Rust", "Camel", "Warm Red"],
            "metals": ["Gold", "Rose Gold", "Bronze"],
            "avoid": ["Icy blues", "Cool pinks", "Silver-toned jewelry"]
        },
        "cool": {
            "colors": ["Navy", "Burgundy", "Emerald", "Lavender", "Cool Blue"],
            "metals": ["Silver", "Platinum", "White Gold"],
            "avoid": ["Orange", "Yellow", "Warm browns"]
        },
        "neutral": {
            "colors": ["Most colors work", "Muted tones", "Soft variations"],
            "metals": ["Both gold and silver"],
            "avoid": ["Nothing specific to avoid"]
        }
    }
    return guidance.get(undertone, guidance["neutral"])

def weather_fabric_guide(temp, humidity):
    """Weather-appropriate fabric recommendations"""
    if temp >= 35:
        return {
            "fabrics": ["Linen", "Lightweight Cotton", "Bamboo", "Seersucker"],
            "style": "Breathable, loose-fitting clothing",
            "colors": "Light colors to reflect heat",
            "tip": "Moisture-wicking fabrics are essential"
        }
    elif temp >= 25:
        return {
            "fabrics": ["Cotton", "Chambray", "Tencel", "Rayon"],
            "style": "Comfortable, semi-fitted clothing",
            "colors": "Light to medium tones",
            "tip": "Natural fibers for breathability"
        }
    elif temp >= 15:
        return {
            "fabrics": ["Cotton blends", "Light Wool", "Jersey", "Denim"],
            "style": "Versatile layering pieces",
            "colors": "Any color works",
            "tip": "Perfect weather for layering"
        }
    else:
        return {
            "fabrics": ["Wool", "Cashmere", "Flannel", "Fleece"],
            "style": "Warm, insulating layers",
            "colors": "Rich, deep colors",
            "tip": "Focus on thermal regulation"
        }

# ==========================================================
# AI STYLIST FUNCTION
# ==========================================================
def generate_outfit_recommendation(
    groq_client, weather_data, user_profile, style_context
):
    """Generate AI-powered outfit recommendation"""
    
    prompt = f"""
    You are an elite fashion stylist providing personalized recommendations.
    
    USER PROFILE:
    Gender: {user_profile['gender']}
    Age: {user_profile['age']}
    Height: {user_profile['height']} cm
    Weight: {user_profile['weight']} kg
    BMI: {user_profile['bmi']} ({user_profile['bmi_category']})
    Body Type: {user_profile['body_type']}
    Skin Undertone: {user_profile['undertone']}
    Water Intake: {user_profile['water_intake']} L/day
    
    STYLE PREFERENCES:
    Style: {style_context['style_preference']}
    Occasion: {style_context['occasion']}
    
    WEATHER CONDITIONS:
    Temperature: {weather_data['temp']}°C (Feels like {weather_data['feels_like']}°C)
    Condition: {weather_data['condition']}
    Humidity: {weather_data['humidity']}%
    
    BODY TYPE GUIDANCE:
    {user_profile['body_guidance']}
    
    COLOR GUIDANCE:
    {user_profile['color_guidance']}
    
    FABRIC GUIDANCE:
    {user_profile['fabric_guidance']}
    
    Provide a concise, practical outfit recommendation covering:
    1. Complete outfit description
    2. Color combinations with rationale
    3. Fabric choices
    4. Footwear
    5. Accessories
    6. Styling tips specific to body type and weather
    
    Keep it practical, realistic, and under 200 words. No markdown or special formatting.
    """
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.7
        )
        
        advice = response.choices[0].message.content
        # Clean any markdown
        advice = re.sub(r'[*#|]', '', advice)
        advice = re.sub(r'\n{3,}', '\n\n', advice)
        
        return advice.strip()
        
    except Exception as e:
        st.error(f"AI generation error: {e}")
        return "Unable to generate recommendation. Please try again."

# ==========================================================
# MAIN APPLICATION
# ==========================================================
def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>👔 AI Weather Stylist Pro</h1>
        <p>Smart fashion recommendations powered by AI, weather data, and body science</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for API key
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Keys
        st.subheader("API Keys")
        openweather_key = st.text_input(
            "OpenWeather API Key",
            type="password",
            help="Get your free API key from openweathermap.org"
        )
        
        groq_key = st.text_input(
            "Groq API Key",
            type="password",
            help="Get your API key from console.groq.com"
        )
        
        if groq_key:
            st.session_state['groq_key'] = groq_key
            
        st.divider()
        
        # Quick tips
        st.subheader("💡 Quick Tips")
        st.info("""
        - Be specific with city names
        - Choose accurate body metrics
        - Consider occasion for best results
        """)
        
        st.divider()
        
        # About
        st.markdown("""
        **How it works:**
        1. Real-time weather data
        2. Body type analysis
        3. Color theory matching
        4. AI-powered recommendations
        """)
    
    # Main content area
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📍 Location & Weather")
        city = st.text_input("City", value="Hyderabad", help="Enter city name for weather data")
        
        if st.button("🔄 Refresh Weather", use_container_width=True):
            st.cache_data.clear()
    
    with col2:
        st.subheader("👤 Personal Details")
        gender = st.selectbox("Gender", ["Male", "Female", "Non-Binary"])
        age = st.number_input("Age", min_value=15, max_value=100, value=22)
    
    with col3:
        st.subheader("📊 Body Metrics")
        height = st.number_input("Height (cm)", min_value=130, max_value=220, value=170)
        weight = st.number_input("Weight (kg)", min_value=30, max_value=200, value=65)
    
    # Style preferences row
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        body_type = st.selectbox(
            "Body Type",
            ["ectomorph", "mesomorph", "endomorph"],
            help="Ectomorph: Slim | Mesomorph: Athletic | Endomorph: Broader"
        )
    
    with col2:
        undertone = st.selectbox(
            "Skin Undertone",
            ["warm", "cool", "neutral"],
            help="Warm: Yellow/Golden | Cool: Pink/Blue | Neutral: Mix"
        )
    
    with col3:
        water_intake = st.slider(
            "Daily Water Intake (L)",
            min_value=0.5, max_value=6.0, value=2.5, step=0.1,
            help="Affects fabric recommendations for comfort"
        )
    
    # Occasion and style
    col1, col2 = st.columns(2)
    
    with col1:
        style_preference = st.selectbox(
            "Style Preference",
            ["Streetwear", "Formal", "Ethnic", "Minimalist", 
             "Business Casual", "Smart Casual", "Luxury", "Sporty"]
        )
    
    with col2:
        occasion = st.selectbox(
            "Occasion",
            ["College", "Office", "Interview", "Wedding", "Party",
             "Casual Outing", "Travel", "Date", "Festival"]
        )
    
    # Generate button
    st.divider()
    generate_col1, generate_col2, generate_col3 = st.columns([1, 2, 1])
    
    with generate_col2:
        generate_btn = st.button(
            "🎨 Generate Outfit Recommendation",
            type="primary",
            use_container_width=True
        )
    
    # Results section
    if generate_btn:
        if not openweather_key or not groq_key:
            st.error("⚠️ Please provide both API keys in the sidebar")
            return
        
        with st.spinner("🔄 Fetching weather data..."):
            weather_data = get_weather(city, openweather_key)
        
        if "error" in weather_data:
            st.error(f"❌ {weather_data['error']}")
            return
        
        # Calculate health metrics
        bmi, bmi_category, bmi_insight = calculate_bmi(height, weight)
        body_guidance = get_body_guidance(body_type)
        color_guidance = get_undertone_guidance(undertone)
        fabric_guidance = weather_fabric_guide(weather_data['temp'], weather_data['humidity'])
        
        # Display weather and health metrics
        st.divider()
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.markdown("""
            <div class="metric-card">
                <h3>🌡️ Temperature</h3>
                <h2>{}°C</h2>
                <p>Feels like {}°C</p>
            </div>
            """.format(weather_data['temp'], weather_data['feels_like']), 
            unsafe_allow_html=True)
        
        with metric_col2:
            st.markdown("""
            <div class="metric-card">
                <h3>💧 Humidity</h3>
                <h2>{}%</h2>
                <p>{}</p>
            </div>
            """.format(weather_data['humidity'], weather_data['condition'].title()),
            unsafe_allow_html=True)
        
        with metric_col3:
            st.markdown("""
            <div class="metric-card">
                <h3>📊 BMI</h3>
                <h2>{}</h2>
                <p>{}</p>
            </div>
            """.format(bmi, bmi_category),
            unsafe_allow_html=True)
        
        with metric_col4:
            st.markdown("""
            <div class="metric-card">
                <h3>👔 Body Type</h3>
                <h2>{}</h2>
                <p>{}</p>
            </div>
            """.format(body_type.title(), body_guidance['description'].split(',')[0]),
            unsafe_allow_html=True)
        
        # Generate AI recommendation
        with st.spinner("🤖 Creating your personalized outfit..."):
            groq_client = Groq(api_key=groq_key)
            
            user_profile = {
                'gender': gender,
                'age': age,
                'height': height,
                'weight': weight,
                'bmi': bmi,
                'bmi_category': bmi_category,
                'body_type': body_type,
                'undertone': undertone,
                'water_intake': water_intake,
                'body_guidance': body_guidance,
                'color_guidance': color_guidance,
                'fabric_guidance': fabric_guidance
            }
            
            style_context = {
                'style_preference': style_preference,
                'occasion': occasion
            }
            
            recommendation = generate_outfit_recommendation(
                groq_client, weather_data, user_profile, style_context
            )
        
        # Display recommendation
        st.markdown("""
        <div class="result-container">
            <h2>✨ Your Personalized Outfit</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.text_area(
            "Recommendation",
            recommendation,
            height=300,
            label_visibility="collapsed"
        )
        
        # Download option
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            "📥 Download Recommendation",
            recommendation,
            file_name=f"outfit_recommendation_{timestamp}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        # Additional insights
        with st.expander("🔍 Style Insights & Tips"):
            st.subheader("Body Type Recommendations")
            for rec in body_guidance['recommendations']:
                st.write(f"✓ {rec}")
            
            st.subheader("Color Palette")
            for color in color_guidance['colors']:
                st.write(f"🎨 {color}")
            
            st.subheader("Fabric Suggestions")
            for fabric in fabric_guidance['fabrics']:
                st.write(f"👕 {fabric}")
            
            if 'avoid' in body_guidance:
                st.subheader("⚠️ What to Avoid")
                for item in body_guidance['avoid']:
                    st.write(f"✗ {item}")
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>🌤️ AI Weather Stylist Pro | Powered by Groq AI & OpenWeather</p>
        <p style="font-size: 0.8rem;">Personalized fashion for every weather and body type</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================================
# REQUIREMENTS FILE
# ==========================================================
"""
Save this as requirements.txt:

streamlit>=1.28.0
requests>=2.31.0
groq>=0.4.0

"""

# ==========================================================
# DEPLOYMENT INSTRUCTIONS
# ==========================================================
"""
To deploy this Streamlit app:

1. Install requirements:
   pip install -r requirements.txt

2. Run locally:
   streamlit run app.py

3. Deploy to Streamlit Cloud:
   - Push to GitHub
   - Connect to streamlit.io/cloud
   - Add secrets in Settings > Secrets:
     OPENWEATHER_API_KEY = "your_key"
     GROQ_API_KEY = "your_key"

4. Create a .streamlit/secrets.toml for local development:
   OPENWEATHER_API_KEY = "your_key"
   GROQ_API_KEY = "your_key"
"""

if __name__ == "__main__":
    main()