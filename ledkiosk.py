# ========== IMPORTS FIRST ==========
import sys
import os
import time

# ABSOLUTE PATH SOLUTION
PROJECT_ROOT = r"C:\Users\Murtaza\Pictures\quran-kiosk-led"

# Add to Python path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import Streamlit FIRST
import streamlit as st

# Then other imports
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
# ========== END IMPORTS ==========

# ========== GOOGLE SHEETS CONNECTION ==========
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '12FWohzX2yJXxvC4xTu3-NSTzLgJogQOmp2LtDLDaw7I'

@st.cache_resource(show_spinner=False)
def get_google_sheet():
    """Connect to Google Sheets - Silent"""
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    return gspread.authorize(credentials).open_by_key(SPREADSHEET_ID)

@st.cache_data(ttl=60, show_spinner=False)
def get_team_data():
    """Get team leaderboard data - Silent"""
    try:
        sheet = get_google_sheet()
        ws = sheet.worksheet("OFFICE WORKING")
        
        team_positions = [
            ('الشمس', 48),
            ('القمر', 49),
            ('الزهرة', 50),
            ('المشتري', 51)
        ]
        
        teams = []
        
        for team_name, row_num in team_positions:
            try:
                points_cell = ws.acell(f'D{row_num}', value_render_option='FORMATTED_VALUE').value
                
                if points_cell:
                    try:
                        cleaned = str(points_cell).replace(',', '').strip()
                        points = float(cleaned) if cleaned else 0
                    except:
                        points = 0
                else:
                    points = 0
                
                teams.append({
                    'team': team_name,
                    'points': points
                })
                
            except Exception:
                teams.append({
                    'team': team_name,
                    'points': 0
                })
        
        df = pd.DataFrame(teams)
        df = df.sort_values('points', ascending=False)
        df['rank'] = range(1, len(df) + 1)
        return df
        
    except Exception:
        return pd.DataFrame({
            'team': ['الشمس', 'القمر', 'الزهرة', 'المشتري'],
            'points': [67, 58, 45, 50],
            'rank': [1, 2, 3, 4]
        })

@st.cache_data(ttl=180, show_spinner=False)
def get_student_data():
    """Get individual student performance - Silent"""
    try:
        sheet = get_google_sheet()
        ws = sheet.worksheet("OFFICE WORKING")
        
        data = ws.get_values('A4:H43')
        students = []
        for row in data:
            if len(row) >= 8:
                students.append({
                    'id': row[0] if row[0] else '',
                    'group': row[1] if len(row) > 1 else '',
                    'team': row[2] if len(row) > 2 else '',
                    'name': row[3] if len(row) > 3 else '',
                    'its': row[4] if len(row) > 4 else '',
                    'grade': row[5] if len(row) > 5 else '',
                    'gender': row[6] if len(row) > 6 else '',
                    'eq_id': row[7] if len(row) > 7 else ''
                })
        return pd.DataFrame(students)
        
    except Exception:
        return pd.DataFrame()
# ========== END GOOGLE SHEETS CODE ==========

# ========== LED/KIOSK MODE ==========
st.set_page_config(
    page_title="Quran LED Scoreboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# COMPLETE UI HIDING
hide_streamlit_style = """
<style>
    /* Hide all Streamlit UI elements */
    #MainMenu, footer, header {visibility: hidden !important; display: none !important;}
    .stDeployButton {display: none !important;}
    div[data-testid="stToolbar"] {display: none !important;}
    section[data-testid="stSidebar"] {display: none !important;}
    
    /* Hide status messages */
    [data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0 !important;
        width: 0 !important;
        overflow: hidden !important;
    }
    
    .stConnectionStatus {display: none !important;}
    .stAlert, .stException, .stWarning, .stInfo, .stSuccess, .stError {
        display: none !important;
        visibility: hidden !important;
    }
    
    .stProgress > div > div, [data-testid="stProgress"] {display: none !important;}
    div.element-container:has([data-testid="stStatusWidget"]) {
        display: none !important;
        height: 0 !important;
        visibility: hidden !important;
    }
    
    .stTooltip, div[data-testid="stDecoration"] {display: none !important;}
    
    /* Black background */
    .stApp {
        background-color: #000000 !important;
        color: white !important;
        padding: 0 !important;
        margin: 0 !important;
    }
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# LED CSS
led_css = """
<style>
    .led-title {
        font-size: 4.5rem !important;
        font-weight: 900 !important;
        text-align: center;
        color: #FFD700;
        text-shadow: 0 0 15px #FFD700;
        margin-bottom: 0.5rem !important;
        padding: 5px !important;
    }
    
    .led-subtitle {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        text-align: center;
        color: #00FFFF;
        text-shadow: 0 0 10px #00FFFF;
        margin-bottom: 1.5rem !important;
        padding: 5px !important;
    }
    
    .led-team-card {
        background: rgba(10, 10, 10, 0.95) !important;
        border-radius: 20px !important;
        padding: 15px !important;
        margin: 5px !important;
        border: 4px solid !important;
        text-align: center;
        min-height: 250px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }
    
    .led-team-rank {
        font-size: 2.8rem !important;
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%) !important;
        color: black !important;
        border-radius: 50% !important;
        width: 80px !important;
        height: 80px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 auto 10px !important;
        font-weight: 900 !important;
    }
    
    .led-team-name {
        font-size: 3.2rem !important;
        font-weight: 900 !important;
        margin: 8px 0 !important;
        direction: rtl;
    }
    
    .led-team-points {
        font-size: 4.5rem !important;
        font-weight: 900 !important;
        margin: 12px 0 !important;
        text-shadow: 0 0 10px;
    }
    
    .led-student-card {
        background: rgba(20, 20, 20, 0.9) !important;
        padding: 20px !important;
        margin: 8px 0 !important;
        border-radius: 15px !important;
        border-left: 8px solid;
        font-size: 2.2rem !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
    }
    
    .slide-indicator {
        text-align: center !important;
        margin-top: 15px !important;
        padding: 8px !important;
    }
    
    .slide-dot {
        display: inline-block !important;
        width: 20px !important;
        height: 20px !important;
        border-radius: 50% !important;
        margin: 0 10px !important;
        background: #444 !important;
    }
    
    .slide-dot.active {
        background: #FFD700 !important;
        box-shadow: 0 0 15px #FFD700 !important;
    }
    
    .timestamp {
        text-align: center !important;
        margin-top: 20px !important;
        color: #666 !important;
        font-size: 1.5rem !important;
        font-family: monospace !important;
    }
</style>
"""

st.markdown(led_css, unsafe_allow_html=True)

# Team colors
TEAM_CONFIG = {
    'الشمس': {'color': '#FF6B00', 'border': '#FF0000', 'icon': '☀️'},
    'القمر': {'color': '#00B4D8', 'border': '#00FFFF', 'icon': '🌙'},
    'الزهرة': {'color': '#FF4081', 'border': '#FF00FF', 'icon': '⭐'},
    'المشتري': {'color': '#7B2CBF', 'border': '#9D4EDD', 'icon': '🪐'}
}

# ========== SLIDE MANAGEMENT ==========
# Get current slide from URL or default to 0
query_params = st.query_params
current_slide = 0

# Check if we have a slide parameter in URL
if 'slide' in query_params:
    try:
        current_slide = int(query_params['slide'])
    except:
        current_slide = 0

# Calculate next slide
next_slide = 1 if current_slide == 0 else 0

# ========== SLIDE 0: TEAM COMPARISON ==========
def show_slide_comparison():
    """Team comparison slide"""
    # Title
    st.markdown('<h1 class="led-title">📊 مقارنة الفرق</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="led-subtitle">TEAM COMPARISON</h2>', unsafe_allow_html=True)
    
    # Get team data
    team_df = get_team_data()
    
    if not team_df.empty:
        cols = st.columns(4)
        
        for idx, (_, team) in enumerate(team_df.iterrows()):
            with cols[idx]:
                config = TEAM_CONFIG.get(team['team'], TEAM_CONFIG['الشمس'])
                
                st.markdown(f"""
                <div class="led-team-card" style="border-color: {config['border']} !important;">
                    <div class="led-team-rank">#{team['rank']}</div>
                    <div class="led-team-name" style="color: {config['color']} !important;">
                        {config['icon']} {team['team']}
                    </div>
                    <div class="led-team-points" style="color: {config['color']} !important;">
                        {team['points']:,.0f}
                    </div>
                    <div style="font-size: 1.8rem !important; color: #AAA !important;">
                        POINTS
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Timestamp
    current_time = datetime.now().strftime("%I:%M %p")
    st.markdown(f'<div class="timestamp">آخر تحديث: {current_time}</div>', unsafe_allow_html=True)

# ========== SLIDE 1: TOP STUDENTS ==========
def show_slide_students():
    """Top students slide"""
    # Title
    st.markdown('<h1 class="led-title">👑 أعلى ٥ طلاب</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="led-subtitle">TOP 5 STUDENTS</h2>', unsafe_allow_html=True)
    
    # Get student data
    student_df = get_student_data()
    
    if not student_df.empty:
        valid_teams = ['الشمس', 'القمر', 'الزهرة', 'المشتري']
        filtered_students = student_df[student_df['team'].isin(valid_teams)].copy()
        
        if len(filtered_students) > 0:
            for i in range(min(5, len(filtered_students))):
                student = filtered_students.iloc[i]
                config = TEAM_CONFIG.get(student['team'], TEAM_CONFIG['الشمس'])
                
                student_name = student['name']
                if len(student_name) > 25:
                    student_name = student_name[:22] + "..."
                
                st.markdown(f"""
                <div class="led-student-card" style="border-left-color: {config['color']} !important;">
                    <div style="display: flex; align-items: center;">
                        <span style="font-size: 2.5rem !important; color: {config['color']} !important; margin-right: 15px !important;">
                            #{i+1}
                        </span>
                        <strong style="font-size: 2.5rem !important;">{student_name}</strong>
                    </div>
                    <div style="color: {config['color']} !important; font-size: 2rem !important;">
                        {config['icon']} {student['team']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Timestamp
    current_time = datetime.now().strftime("%I:%M %p")
    st.markdown(f'<div class="timestamp">آخر تحديث: {current_time}</div>', unsafe_allow_html=True)

# ========== MAIN DISPLAY ==========
# Show current slide
slides = [show_slide_comparison, show_slide_students]
slides[current_slide]()

# Slide indicator
dots_html = '<div class="slide-indicator">'
for i in range(2):
    active_class = "active" if i == current_slide else ""
    dots_html += f'<span class="slide-dot {active_class}"></span>'
dots_html += '</div>'
st.markdown(dots_html, unsafe_allow_html=True)

# ========== AUTO-REFRESH WITH SLIDE ROTATION ==========
# JavaScript to auto-refresh and switch slides
auto_refresh_js = f"""
<script>
    // Wait 10 seconds, then redirect to next slide
    setTimeout(function() {{
        // Redirect to next slide
        window.location.href = window.location.pathname + "?slide={next_slide}";
    }}, 10000); // 10 seconds
</script>
"""


st.markdown(auto_refresh_js, unsafe_allow_html=True)
