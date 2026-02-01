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
    
    # Remove refresh rate slider since we're not caching
    st.info("🔄 **Live Mode Active**")
    st.caption("Changes in Google Sheets appear immediately")
    
    # Simple refresh button
    if st.button("🔄 Refresh Page"):
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Data Status")
    
    try:
        df = get_team_data()
        from datetime import datetime
        last_update = datetime.now().strftime("%H:%M:%S")
        if not df.empty:
            st.success(f"✅ Live Connection")
            st.caption(f"Last checked: {last_update}")
            st.caption(f"Teams loaded: {len(df)}")
        else:
            st.warning("⚠️ No team data found in Google Sheets")
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
        st.error("❌ No team data found in Google Sheets")

# ========== TAB 2: WEEKLY BREAKDOWN ==========
with tab2:
    st.header("📅 Weekly Breakdown")
    
    weekly_df = get_weekly_data()
    
    if not weekly_df.empty:
        # Data explanation
        st.info("""
        **📊 Data Source:** Points Table Monthly sheet
        **ℹ️ Note:** Week 1 shows total points, Weeks 2-5 show weekly increments
        """)
        
        # Quick stats at the top
        st.subheader("🏆 Weekly Performance Summary")
        
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
        
        # Week-by-week breakdown
        st.subheader("📆 Week-by-Week Breakdown")
        
        weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5']
        week_cols = st.columns(5)
        
        for i, week in enumerate(weeks):
            with week_cols[i]:
                week_data = weekly_df[weekly_df['week'] == week]
                total = week_data['points'].sum()
                
                # Card styling
                st.markdown(f"""
                <div style="
                    background: {'#f8f9fa' if week != 'Week 1' else '#fff3cd'};
                    border-radius: 10px;
                    padding: 15px;
                    text-align: center;
                    border-left: 5px solid {'#4ECDC4' if week != 'Week 1' else '#FF6B6B'};
                    margin-bottom: 10px;
                ">
                    <h3 style="margin: 0; color: #333;">{week}</h3>
                    <h2 style="margin: 10px 0; color: {'#1E3A8A' if week != 'Week 1' else '#D97706'};">
                        {total:,.0f} pts
                    </h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Team details
                for _, row in week_data.sort_values('points', ascending=False).iterrows():
                    team_icon = {
                        'الشمس': '☀️',
                        'القمر': '🌙', 
                        'الزهرة': '⭐',
                        'المشتري': '🪐'
                    }.get(row['team'], '🏆')
                    
                    st.caption(f"{team_icon} {row['team']}: **{row['points']:.0f}** pts")
        
        # Main visualization section
        st.subheader("📈 Visualization Options")
        
        # Visualization options
        viz_option = st.radio(
            "Choose visualization:",
            ["All Weeks (Log Scale)", "Weeks 2-5 Only", "Comparison View"],
            horizontal=True
        )
        
        # Team colors
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
        
        if viz_option == "All Weeks (Log Scale)":
            # Chart 1: All weeks with log scale
            fig = px.line(weekly_df, x='week', y='points', color='team',
                         color_discrete_map=team_colors,
                         markers=True,
                         line_shape='linear')
            
            fig.update_layout(
                height=500,
                xaxis_title="Week",
                yaxis_title="Points (Log Scale)",
                yaxis_type="log",
                hovermode='x unified',
                plot_bgcolor='white',
                legend_title="Team"
            )
            
            # Add grid
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
            
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Note: Log scale used to better show both Week 1 (500-600+) and Weeks 2-5 (20-30+)")
            
        elif viz_option == "Weeks 2-5 Only":
            # Chart 2: Weeks 2-5 only
            weeks_2_5_df = weekly_df[weekly_df['week'].isin(['Week 2', 'Week 3', 'Week 4', 'Week 5'])]
            
            if not weeks_2_5_df.empty:
                fig = px.line(weeks_2_5_df, x='week', y='points', color='team',
                             color_discrete_map=team_colors,
                             markers=True,
                             line_shape='linear')
                
                fig.update_layout(
                    height=500,
                    xaxis_title="Week",
                    yaxis_title="Points",
                    hovermode='x unified',
                    plot_bgcolor='white',
                    legend_title="Team"
                )
                
                # Add grid
                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data available for Weeks 2-5")
            
        else:  # Comparison View
            # Bar chart comparison
            fig = px.bar(weekly_df, x='week', y='points', color='team',
                        color_discrete_map=team_colors,
                        barmode='group')
            
            fig.update_layout(
                height=500,
                xaxis_title="Week",
                yaxis_title="Points",
                hovermode='x unified',
                plot_bgcolor='white',
                legend_title="Team"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed data table
        st.subheader("📋 Detailed Data Table")
        
        # Create pivot table
        pivot_df = weekly_df.pivot_table(
            index='team',
            columns='week',
            values='points',
            aggfunc='sum'
        )
        
        # Ensure correct column order
        pivot_df = pivot_df[week_order]
        
        # Add row for weekly totals
        weekly_totals_row = pivot_df.sum()
        pivot_df.loc['📊 Week Total'] = weekly_totals_row
        
        # Add column for team totals
        pivot_df['📈 Team Total'] = pivot_df[week_order].sum(axis=1)
        
        # Display with better formatting
        st.dataframe(
            pivot_df.style.format("{:.0f}"),
            use_container_width=True,
            height=400
        )
        
        # Export option
        csv = weekly_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Weekly Data (CSV)",
            data=csv,
            file_name="quran_weekly_points.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # Data quality notes
        with st.expander("ℹ️ Data Notes & Interpretation"):
            st.markdown("""
            ### 📝 Understanding the Data:
            
            **Week 1 (High Values: 500-600+ points):**
            - Likely represents **total accumulated points** or **starting totals**
            - May include points from previous periods
            - Not directly comparable to weekly increments
            
            **Weeks 2-5 (Lower Values: 20-30+ points):**
            - Represent **weekly increments/achievements**
            - Show actual weekly performance
            - Better for tracking week-to-week progress
            
            ### 🎯 How to Interpret:
            1. **For overall ranking**: Look at Week 1 (total points)
            2. **For weekly progress**: Focus on Weeks 2-5
            3. **For team momentum**: Check if weekly points are increasing/decreasing
            """)
        
    else:
        st.error("❌ No weekly data found in Google Sheets. Check your Points Table Monthly sheet.")

# ========== TAB 3: STUDENT PERFORMANCE ==========
with tab3:
    st.header("👥 Student Performance")
    
    student_df = get_student_data()
    
    if not student_df.empty:
        # Clean the data - remove rows with empty or invalid team names
        valid_teams = ['الشمس', 'القمر', 'الزهرة', 'المشتري']
        
        # Filter to only include valid teams
        filtered_students = student_df[student_df['team'].isin(valid_teams)].copy()
        
        if not filtered_students.empty:
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
            st.error("❌ No valid student data found. Check team names in Google Sheets.")
    else:
        st.error("❌ No student data found in Google Sheets. Check the OFFICE WORKING sheet.")

# ========== TAB 4: SPECIAL ACHIEVEMENTS ==========
with tab4:
    st.header("🎯 Special Achievements")
    
    # Try to load from JAN sheet (only sheet that exists)
    months = ['JAN']
    all_achievements = pd.DataFrame()
    loaded_months = []
    
    for month in months:
        try:
            achievements = get_special_achievements(month)
            if not achievements.empty:
                achievements['month_display'] = month
                all_achievements = pd.concat([all_achievements, achievements], ignore_index=True)
                loaded_months.append(month)
        except Exception as e:
            continue
    
    if not all_achievements.empty:
        st.success(f"✅ Loaded achievements from Google Sheets")
        
        # Display summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Achievements", len(all_achievements))
        with col2:
            st.metric("Total Points", int(all_achievements['points'].sum()))
        with col3:
            st.metric("Unique Students", all_achievements['student'].nunique())
        with col4:
            if not all_achievements.empty:
                categories = all_achievements['category'].nunique()
                st.metric("Categories", categories)
        
        # Display by category
        st.subheader("🏅 Achievements by Category")
        
        for category in all_achievements['category'].unique():
            cat_data = all_achievements[all_achievements['category'] == category]
            
            with st.expander(f"{category} ({len(cat_data)})"):
                if not cat_data.empty:
                    # Group by team if available
                    if 'team' in cat_data.columns:
                        for team in cat_data['team'].unique():
                            if team != "Unknown":
                                team_data = cat_data[cat_data['team'] == team]
                                st.markdown(f"**{team}**")
                                for _, row in team_data.iterrows():
                                    st.write(f"• {row['student']}: {row['points']} points")
                                st.write("---")
                    else:
                        for _, row in cat_data.iterrows():
                            st.write(f"• {row['student']}: {row['points']} points")
        
        # Data table view
        st.subheader("📋 All Achievements")
        st.dataframe(
            all_achievements[['student', 'category', 'points', 'month_display']].rename(
                columns={
                    'student': 'Student',
                    'category': 'Achievement Type',
                    'points': 'Points',
                    'month_display': 'Month'
                }
            ),
            use_container_width=True,
            hide_index=True
        )
    
    else:
        st.error("❌ No achievements found in Google Sheets. Check the JAN sheet.")

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>📊 **Live Data Only** - All data from Google Sheets</p>
    <p>📊 Data source: Google Sheets | ⚡ Powered by Streamlit | 🎯 Competition Tracking</p>
    <p>© 2024 Quran Live Scoreboard</p>
</div>
""", unsafe_allow_html=True)
