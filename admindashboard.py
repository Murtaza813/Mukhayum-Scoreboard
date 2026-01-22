# ========== IMPORTS FIRST ==========
import sys
import os
import time
from datetime import datetime

# For Streamlit Cloud environment
PROJECT_ROOT = "/mount/src/mukhayum-scoreboard"

# Add to Python path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import Streamlit FIRST
import streamlit as st

# Then other imports
import pandas as pd
import numpy as np
import plotly.express as px

# Import from shared module - ONLY THESE FUNCTIONS
from shared.data_loader import get_team_data, get_student_data, get_weekly_data, get_special_achievements
# ========== END IMPORTS ==========

# Page configuration
st.set_page_config(
    page_title="Quran Live Scoreboard",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ========== CUSTOM CSS ==========
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
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F3F4F6;
        border-radius: 5px 5px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103655.png", width=100)
    st.title("Quran Scoreboard")
    st.markdown("---")
    
    refresh_rate = st.slider("Refresh rate (seconds)", 10, 300, 30)
    
    if st.button("🔄 Refresh Now"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Data Status")
    
    # Test connection by calling get_team_data, not get_google_sheet
    try:
        df = get_team_data()
        last_update = datetime.now().strftime("%H:%M:%S")
        if not df.empty:
            st.success(f"✅ Connected to Google Sheets")
            st.caption(f"Last update: {last_update}")
            st.caption(f"Teams loaded: {len(df)}")
        else:
            st.warning("⚠️ No team data found")
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")

# ========== MAIN CONTENT ==========
st.markdown('<h1 class="main-header">📖 Quran Live Scoreboard</h1>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["🏆 Team Leaderboard", "📅 Weekly Breakdown", "👥 Student Performance", "🎯 Special Achievements"])

# ========== TAB 1: TEAM LEADERBOARD ==========
with tab1:
    st.header("🏆 Live Team Leaderboard")
    
    team_df = get_team_data()
    
    if not team_df.empty:
        # Team information
        team_info = {
            'الشمس': {
                'en': 'Al-Anwar (Sun)',
                'color': '#FF6B6B',
                'border_color': '#FF0000',
                'icon': '☀️'
            },
            'القمر': {
                'en': 'Al-Aqmar (Moon)', 
                'color': '#4ECDC4',
                'border_color': '#00B894',
                'icon': '🌙'
            },
            'الزهرة': {
                'en': 'Al-Azhar (Venus)',
                'color': '#FFD166',
                'border_color': '#FDCB6E',
                'icon': '⭐'
            },
            'المشتري': {
                'en': 'Al-Juyushi (Jupiter)',
                'color': '#06D6A0',
                'border_color': '#00CEC9',
                'icon': '🪐'
            }
        }
        
        # Create columns for team cards
        cols = st.columns(4)
        
        for idx, (_, team) in enumerate(team_df.iterrows()):
            with cols[idx]:
                info = team_info.get(team['team'], {
                    'en': team['team'],
                    'color': '#667eea',
                    'border_color': '#764ba2',
                    'icon': '🏆'
                })
                
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
        
        # Add English names for chart
        team_df['team_display'] = team_df['team'].map(lambda x: team_info.get(x, {}).get('en', x))
        
        fig = px.bar(team_df, x='team_display', y='points', 
                    color='team',
                    color_discrete_map={
                        'الشمس': '#FF6B6B',
                        'القمر': '#4ECDC4',
                        'الزهرة': '#FFD166',
                        'المشتري': '#06D6A0'
                    })
        fig.update_layout(
            height=400, 
            showlegend=False,
            xaxis_title="Team",
            yaxis_title="Total Points",
            plot_bgcolor='white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Show raw data
        with st.expander("View Team Data Details"):
            st.dataframe(team_df, use_container_width=True)
            
    else:
        st.warning("No team data found.")

# ========== TAB 2: WEEKLY BREAKDOWN ==========
with tab2:
    st.header("📅 Weekly Breakdown")
    
    weekly_df = get_weekly_data()
    
    if not weekly_df.empty:
        # Heatmap
        st.subheader("Weekly Performance Heatmap")
        
        try:
            pivot_df = weekly_df.pivot(index='team', columns='week', values='points')
            
            fig = px.imshow(pivot_df, 
                          labels=dict(x="Week", y="Team", color="Points"),
                          aspect="auto",
                          color_continuous_scale='Viridis')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Heatmap data not available yet")
        
        # Line chart
        st.subheader("Weekly Progress")
        
        # Add team colors
        team_colors = {
            'الشمس': '#FF6B6B',
            'القمر': '#4ECDC4',
            'الزهرة': '#FFD166',
            'المشتري': '#06D6A0'
        }
        
        weekly_df['color'] = weekly_df['team'].map(team_colors)
        
        fig2 = px.line(weekly_df, x='week', y='points', color='team',
                      color_discrete_map=team_colors,
                      markers=True)
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
        
        # Data table
        st.subheader("Weekly Data Table")
        st.dataframe(weekly_df, use_container_width=True)
        
    else:
        st.info("Weekly data will be available once configured in Google Sheets.")

# ========== TAB 3: STUDENT PERFORMANCE ==========
with tab3:
    st.header("👥 Student Performance")
    
    student_df = get_student_data()
    
    if not student_df.empty:
        # Clean the data - remove rows with empty or invalid team names
        valid_teams = ['الشمس', 'القمر', 'الزهرة', 'المشتري']
        
        # Filter to only include valid teams
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
        
        # Team distribution
        st.subheader("Student Distribution by Team")
        
        # Count students per team (only valid teams)
        team_counts = filtered_students['team'].value_counts()
        
        # Create two columns for chart and metrics
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if len(team_counts) > 0:
                # Create pie chart with only valid teams
                fig = px.pie(
                    values=team_counts.values, 
                    names=team_counts.index,
                    color=team_counts.index,
                    color_discrete_map={
                        'الشمس': '#FF6B6B',
                        'القمر': '#4ECDC4',
                        'الزهرة': '#FFD166',
                        'المشتري': '#06D6A0'
                    },
                    hole=0.3  # Creates a donut chart
                )
                fig.update_layout(
                    height=400,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No valid team data available for chart")
        
        with col2:
            st.markdown("### Students per Team")
            # Display metrics for each team
            for team in valid_teams:
                count = team_counts.get(team, 0)
                st.metric(f"**{team}**", count)
        
        # Show data quality info
        if len(filtered_students) != len(student_df):
            st.info(f"Showing {len(filtered_students)} of {len(student_df)} students (filtered invalid team entries)")
            
            # Show what was filtered out
            invalid_teams = student_df[~student_df['team'].isin(valid_teams)]
            if len(invalid_teams) > 0:
                with st.expander("Show students with invalid/missing team data"):
                    st.write("These students have missing or invalid team names:")
                    st.dataframe(invalid_teams[['name', 'team']], use_container_width=True)
        
        # Student list by team
        st.subheader("Student List")
        
        team_filter = st.selectbox("Filter by Team", 
                                 ['All Teams'] + valid_teams)
        
        if team_filter != 'All Teams':
            display_students = filtered_students[filtered_students['team'] == team_filter]
        else:
            display_students = filtered_students
        
        # Display student table
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
            st.info("No students found for the selected filter")
        
    else:
        st.warning("No student data found.")

# ========== TAB 4: SPECIAL ACHIEVEMENTS ==========
with tab4:
    st.header("🎯 Special Achievements")
    
    # Get achievements from all monthly sheets
    months = ['Jumādā al-Ūlā', 'Jumādā al-Ukhrā', 'May', 'June']
    all_achievements = pd.DataFrame()
    
    for month in months:
        achievements = get_special_achievements(month)
        if not achievements.empty:
            all_achievements = pd.concat([all_achievements, achievements])
    
    if not all_achievements.empty:
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_category = st.selectbox("Achievement Type", 
                                           ['All'] + list(all_achievements['category'].unique()))
        with col2:
            selected_team = st.selectbox("Team", 
                                       ['All'] + list(all_achievements['team'].unique()))
        with col3:
            selected_month = st.selectbox("Month", 
                                        ['All'] + list(all_achievements['month'].unique()))
        
        # Apply filters
        filtered_ach = all_achievements.copy()
        if selected_category != 'All':
            filtered_ach = filtered_ach[filtered_ach['category'] == selected_category]
        if selected_team != 'All':
            filtered_ach = filtered_ach[filtered_ach['team'] == selected_team]
        if selected_month != 'All':
            filtered_ach = filtered_ach[filtered_ach['month'] == selected_month]
        
        # Display achievements by category
        if not filtered_ach.empty:
            for category in filtered_ach['category'].unique():
                category_data = filtered_ach[filtered_ach['category'] == category]
                
                st.subheader(f"{category} ({len(category_data)} achievements)")
                
                # Create a grid of cards
                items_per_row = 3
                items = list(category_data.iterrows())
                
                for i in range(0, len(items), items_per_row):
                    cols = st.columns(items_per_row)
                    row_items = items[i:i + items_per_row]
                    
                    for col_idx, (_, row) in enumerate(row_items):
                        with cols[col_idx]:
                            team_color = {
                                'الشمس': '#FF6B6B',
                                'القمر': '#4ECDC4',
                                'الزهرة': '#FFD166',
                                'المشتري': '#06D6A0',
                                'Unknown': '#667eea'
                            }.get(row['team'], '#667eea')
                            
                            st.markdown(f"""
                            <div class="metric-card" style="border-left-color: {team_color};">
                                <h4 style="margin: 0 0 10px 0; font-size: 1rem;">
                                    {row['student'][:40]}{'...' if len(row['student']) > 40 else ''}
                                </h4>
                                <p style="margin: 5px 0; font-size: 0.9rem;">
                                    <strong style="color: {team_color};">{row['points']} points</strong>
                                </p>
                                <p style="margin: 5px 0; font-size: 0.8rem; color: #666;">
                                    <strong>Team:</strong> {row['team']}<br>
                                    <strong>Month:</strong> {row['month']}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
            
            # Summary statistics
            st.subheader("📊 Achievements Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Achievements", len(filtered_ach))
            with col2:
                st.metric("Unique Students", filtered_ach['student'].nunique())
            with col3:
                st.metric("Total Points", filtered_ach['points'].sum())
            with col4:
                top_team = filtered_ach['team'].value_counts().index[0] if not filtered_ach.empty else "None"
                st.metric("Top Team", top_team)
            
            # Achievements by team chart
            if filtered_ach['team'].nunique() > 0:
                st.subheader("Achievements by Team")
                
                team_achievements = filtered_ach.groupby('team').agg({
                    'points': 'sum',
                    'student': 'count'
                }).rename(columns={'student': 'count'}).reset_index()
                
                fig = px.bar(team_achievements, x='team', y='count',
                            color='team',
                            color_discrete_map={
                                'الشمس': '#FF6B6B',
                                'القمر': '#4ECDC4',
                                'الزهرة': '#FFD166',
                                'المشتري': '#06D6A0',
                                'Unknown': '#667eea'
                            })
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                
        else:
            st.info("No achievements match the selected filters.")
            
    else:
        st.info("No special achievements found in monthly sheets.")

# ========== FOOTER ==========
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🔄 Updates automatically every {refresh_rate} seconds</p>
    <p>📊 Data source: Google Sheets | ⚡ Powered by Streamlit | 🎯 Real-time Competition Tracking</p>
    <p>© 2024 Quran Live Scoreboard</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh
time.sleep(refresh_rate)

st.rerun()




