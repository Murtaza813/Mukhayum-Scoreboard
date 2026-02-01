import streamlit as st
import pandas as pd
from datetime import datetime

# Page config FIRST
st.set_page_config(
    page_title="Quran Live Scoreboard",
    page_icon="📖",
    layout="wide"
)

# Simple CSS
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; color: #1E3A8A; text-align: center; }
    .team-card { background: white; border-radius: 10px; padding: 20px; margin: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("Quran Scoreboard")
    st.markdown("---")
    last_update = datetime.now().strftime("%H:%M:%S")
    st.success(f"✅ Live - {last_update}")
    if st.button("🔄 Refresh"):
        st.rerun()

# Main content
st.markdown('<h1 class="main-header">📖 Quran Live Scoreboard</h1>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["🏆 Teams", "📅 Weekly", "👥 Students", "🎯 Achievements"])

with tab1:
    st.header("Team Leaderboard")
    
    # Sample data
    teams_data = pd.DataFrame({
        'Team': ['الشمس (Sun)', 'القمر (Moon)', 'الزهرة (Venus)', 'المشتري (Jupiter)'],
        'Points': [1500, 1200, 900, 800],
        'Rank': [1, 2, 3, 4]
    })
    
    # Display as cards
    cols = st.columns(4)
    for idx, (_, team) in enumerate(teams_data.iterrows()):
        with cols[idx]:
            colors = ['#FF6B6B', '#4ECDC4', '#FFD166', '#06D6A0']
            icons = ['☀️', '🌙', '⭐', '🪐']
            
            st.markdown(f"""
            <div class="team-card" style="border-top: 5px solid {colors[idx]};">
                <div style="font-size: 2rem;">{icons[idx]}</div>
                <h3 style="margin: 10px 0;">{team['Team'].split(' ')[0]}</h3>
                <h1 style="margin: 10px 0; color: {colors[idx]};">{team['Points']:,}</h1>
                <p style="margin: 0;">Rank #{team['Rank']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.dataframe(teams_data, use_container_width=True)

with tab2:
    st.header("Weekly Breakdown")
    st.info("Weekly data loading soon...")

with tab3:
    st.header("Student Performance")
    st.info("Student data loading soon...")

with tab4:
    st.header("Special Achievements")
    st.info("Achievements data loading soon...")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>📊 Live Scoreboard | ⚡ Streamlit | 🎯 Real-time Tracking</p>
    <p>© 2024 Quran Live Scoreboard</p>
</div>
""", unsafe_allow_html=True)
