# admindashboard.py - COMPLETE WORKING VERSION
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import sys
import os

# Set page config
st.set_page_config(
    page_title="Quran Live Scoreboard",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .team-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        border-top: 5px solid;
        margin-bottom: 20px;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #4F46E5;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Add project root to path
PROJECT_ROOT = "/mount/src/mukhayum-scoreboard"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import data functions
from shared.data_loader import get_team_data, get_student_data, get_weekly_data, get_special_achievements

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103655.png", width=100)
    st.title("Quran Scoreboard")
    st.markdown("---")
    
    # Auto-refresh option
    auto_refresh = st.checkbox("🔄 Enable Auto-Refresh", value=True)
    
    if auto_refresh:
        refresh_rate = st.slider("Refresh every (seconds)", 2, 10, 3)
        st.info(f"Auto-refreshing every {refresh_rate} seconds")
        import time
        time.sleep(refresh_rate)
        st.rerun()
    
    if st.button("🔄 Manual Refresh"):
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Connection Status")
    
    try:
        team_df = get_team_data()
        last_update = datetime.now().strftime("%H:%M:%S")
        if not team_df.empty:
            st.success("✅ Live Data Connected")
            st.caption(f"Last update: {last_update}")
            st.caption(f"Teams: {len(team_df)}")
        else:
            st.warning("⚠️ No team data found")
    except Exception as e:
        st.error(f"❌ Connection error: {str(e)[:50]}")

# ========== MAIN CONTENT ==========
st.markdown('<h1 class="main-header">📖 Quran Live Scoreboard</h1>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["🏆 Team Leaderboard", "📅 Weekly Breakdown", "👥 Student Performance", "🎯 Special Achievements"])

# ========== TAB 1: TEAM LEADERBOARD ==========
with tab1:
    st.header("🏆 Live Team Leaderboard")
    
    try:
        team_df = get_team_data()
        
        if not team_df.empty:
            # Team information
            team_info = {
                'الشمس': {'en': 'Al-Anwar (Sun)', 'color': '#FF6B6B', 'border_color': '#FF0000', 'icon': '☀️'},
                'القمر': {'en': 'Al-Aqmar (Moon)', 'color': '#4ECDC4', 'border_color': '#00B894', 'icon': '🌙'},
                'الزهرة': {'en': 'Al-Azhar (Venus)', 'color': '#FFD166', 'border_color': '#FDCB6E', 'icon': '⭐'},
                'المشتري': {'en': 'Al-Juyushi (Jupiter)', 'color': '#06D6A0', 'border_color': '#00CEC9', 'icon': '🪐'}
            }
            
            # Create team cards
            cols = st.columns(4)
            for idx, (_, team) in enumerate(team_df.iterrows()):
                with cols[idx]:
                    info = team_info.get(team['team'], {'en': team['team'], 'color': '#667eea', 'border_color': '#764ba2', 'icon': '🏆'})
                    
                    st.markdown(f"""
                    <div class="team-card" style="border-color: {info['border_color']};">
                        <div style="font-size: 2rem; margin-bottom: 10px;">{info['icon']}</div>
                        <h3 style="margin: 0; color: #666; font-size: 1rem;">Rank #{team['rank']}</h3>
                        <h2 style="margin: 10px 0; color: #333; font-size: 1.8rem; direction: rtl;">{team['team']}</h2>
                        <p style="margin: 0; color: #666; font-size: 0.9rem;">{info['en']}</p>
                        <h1 style="margin: 15px 0; color: {info['border_color']}; font-size: 3rem;">{team['points']:,.0f}</h1>
                        <p style="margin: 0; color: #666;">Total Points</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Bar chart
            st.subheader("Points Comparison")
            team_df['team_display'] = team_df['team'].map(lambda x: team_info.get(x, {}).get('en', x))
            
            fig = px.bar(team_df, x='team_display', y='points', 
                        color='team',
                        color_discrete_map={
                            'الشمس': '#FF6B6B',
                            'القمر': '#4ECDC4',
                            'الزهرة': '#FFD166',
                            'المشتري': '#06D6A0'
                        })
            fig.update_layout(height=400, showlegend=False, xaxis_title="Team", yaxis_title="Total Points", plot_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("View Team Data Details"):
                st.dataframe(team_df, use_container_width=True)
                
        else:
            st.warning("No team data found.")
            
    except Exception as e:
        st.error(f"Error loading team data: {str(e)}")
        st.info("Check your data_loader.py file")

# ========== TAB 2: WEEKLY BREAKDOWN ==========
with tab2:
    st.header("📅 Weekly Breakdown")
    
    try:
        weekly_df = get_weekly_data()
        
        if not weekly_df.empty:
            st.info("**Data Source:** Points Table Monthly sheet")
            
            # Quick stats
            st.subheader("🏆 Weekly Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_points = weekly_df['points'].sum()
                st.metric("Total Points", f"{total_points:,.0f}")
            
            with col2:
                avg_per_week = weekly_df.groupby('week')['points'].sum().mean()
                st.metric("Average per Week", f"{avg_per_week:,.0f}")
            
            with col3:
                weekly_totals = weekly_df.groupby('week')['points'].sum()
                best_week = weekly_totals.idxmax() if not weekly_totals.empty else "N/A"
                st.metric("Best Week", best_week)
            
            with col4:
                team_totals = weekly_df.groupby('team')['points'].sum()
                leading_team = team_totals.idxmax() if not team_totals.empty else "N/A"
                st.metric("Leading Team", leading_team)
            
            # Visualization
            st.subheader("📈 Weekly Progress")
            
            team_colors = {
                'الشمس': '#FF6B6B',
                'القمر': '#4ECDC4',
                'الزهرة': '#FFD166',
                'المشتري': '#06D6A0'
            }
            
            # Order weeks correctly
            week_order = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5']
            weekly_df['week'] = pd.Categorical(weekly_df['week'], categories=week_order, ordered=True)
            weekly_df = weekly_df.sort_values(['team', 'week'])
            
            # Line chart
            fig = px.line(weekly_df, x='week', y='points', color='team',
                         color_discrete_map=team_colors,
                         markers=True)
            
            fig.update_layout(height=500, xaxis_title="Week", yaxis_title="Points", hovermode='x unified', plot_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)
            
            # Data table
            st.subheader("📋 Weekly Data Table")
            pivot_df = weekly_df.pivot_table(index='team', columns='week', values='points', aggfunc='sum')
            pivot_df = pivot_df[week_order]
            pivot_df['Total'] = pivot_df.sum(axis=1)
            pivot_df.loc['Week Total'] = pivot_df.sum()
            
            st.dataframe(pivot_df.style.format("{:.0f}"), use_container_width=True)
            
        else:
            st.info("Weekly data will be available once configured.")
            
    except Exception as e:
        st.error(f"Error loading weekly data: {str(e)}")

# ========== TAB 3: STUDENT PERFORMANCE ==========
with tab3:
    st.header("👥 Student Performance")
    
    try:
        student_df = get_student_data()
        
        if not student_df.empty:
            # Filter valid teams
            valid_teams = ['الشمس', 'القمر', 'الزهرة', 'المشتري']
            filtered_students = student_df[student_df['team'].isin(valid_teams)].copy()
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Students", len(filtered_students))
            with col2:
                st.metric("Valid Teams", filtered_students['team'].nunique())
            with col3:
                male_count = len(filtered_students[filtered_students['gender'] == 'M'])
                st.metric("Male Students", male_count)
            with col4:
                female_count = len(filtered_students[filtered_students['gender'] == 'F'])
                st.metric("Female Students", female_count)
            
            # Team distribution chart
            st.subheader("Student Distribution by Team")
            team_counts = filtered_students['team'].value_counts()
            
            col1, col2 = st.columns([2, 1])
            with col1:
                if len(team_counts) > 0:
                    fig = px.pie(values=team_counts.values, names=team_counts.index,
                                color=team_counts.index,
                                color_discrete_map={
                                    'الشمس': '#FF6B6B',
                                    'القمر': '#4ECDC4',
                                    'الزهرة': '#FFD166',
                                    'المشتري': '#06D6A0'
                                },
                                hole=0.3)
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### Students per Team")
                for team in valid_teams:
                    count = team_counts.get(team, 0)
                    st.metric(f"**{team}**", count)
            
            # Student list
            st.subheader("Student List")
            team_filter = st.selectbox("Filter by Team", ['All Teams'] + valid_teams)
            
            if team_filter != 'All Teams':
                display_students = filtered_students[filtered_students['team'] == team_filter]
            else:
                display_students = filtered_students
            
            if len(display_students) > 0:
                st.dataframe(
                    display_students[['name', 'team', 'gender', 'grade', 'its']].rename(columns={
                        'name': 'Name',
                        'team': 'Team',
                        'gender': 'Gender',
                        'grade': 'Grade',
                        'its': 'ITS ID'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No students found.")
                
        else:
            st.info("Student data will be available once configured.")
            
    except Exception as e:
        st.error(f"Error loading student data: {str(e)}")

# ========== TAB 4: SPECIAL ACHIEVEMENTS ==========
with tab4:
    st.header("🎯 Special Achievements")
    
    try:
        months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN']
        all_achievements = pd.DataFrame()
        
        for month in months:
            try:
                achievements = get_special_achievements(month)
                if not achievements.empty:
                    achievements['month_display'] = month
                    all_achievements = pd.concat([all_achievements, achievements], ignore_index=True)
            except:
                continue
        
        if not all_achievements.empty:
            st.success(f"✅ Loaded achievements data")
            
            # Simple display
            for month in all_achievements['month_display'].unique():
                month_data = all_achievements[all_achievements['month_display'] == month]
                with st.expander(f"{month} - {len(month_data)} achievements"):
                    for _, row in month_data.iterrows():
                        st.write(f"• {row['student']}: {row['points']} points ({row['category']})")
        
        else:
            st.info("No achievements found. Check your JAN sheet in Google Sheets.")
            
    except Exception as e:
        st.error(f"Error loading achievements: {str(e)}")

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>📊 Live Scoreboard | ⚡ Powered by Streamlit | 🎯 Real-time Tracking</p>
    <p>© 2024 Quran Live Scoreboard</p>
</div>
""", unsafe_allow_html=True)
