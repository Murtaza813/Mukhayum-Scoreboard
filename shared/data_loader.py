import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '12FWohzX2yJXxvC4xTu3-NSTzLgJogQOmp2LtDLDaw7I'

@st.cache_resource
def get_google_sheet():
    """Connect to Google Sheets"""
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    return gspread.authorize(credentials).open_by_key(SPREADSHEET_ID)

@st.cache_data(ttl=5)
def get_team_data():
    """Get team leaderboard data - CORRECTED FOR ROWS 48-51"""
    try:
        sheet = get_google_sheet()
        ws = sheet.worksheet("OFFICE WORKING")
        
        # CORRECTED: Teams are in rows 48-51, not 50-53
        team_positions = [
            ('الشمس', 48),  # Row 48 for الشمس
            ('القمر', 49),  # Row 49 for القمر
            ('الزهرة', 50), # Row 50 for الزهرة
            ('المشتري', 51) # Row 51 for المشتري
        ]
        
        teams = []
        
        for team_name, row_num in team_positions:
            try:
                # Get points from column D - use formatted value to get calculated result
                points_cell = ws.acell(f'D{row_num}', value_render_option='FORMATTED_VALUE').value
                
                if points_cell:
                    try:
                        # Clean and convert to float
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
                
            except Exception as e:
                st.warning(f"Error reading {team_name} at D{row_num}: {e}")
                teams.append({
                    'team': team_name,
                    'points': 0
                })
        
        # Create DataFrame and add rank
        df = pd.DataFrame(teams)
        df = df.sort_values('points', ascending=False)
        df['rank'] = range(1, len(df) + 1)
        
        return df
        
    except Exception as e:
        st.error(f"Error getting team data: {e}")
        # Return fallback data (with correct order based on debug)
        return pd.DataFrame({
            'team': ['الشمس', 'القمر', 'الزهرة', 'المشتري'],
            'points': [67, 58, 45, 50],  # CORRECTED from debug output
            'rank': [1, 2, 3, 4]
        })

@st.cache_data(ttl=10)
def get_student_data():
    """Get individual student performance"""
    try:
        sheet = get_google_sheet()
        ws = sheet.worksheet("OFFICE WORKING")
        
        # Get student data from rows 4-43
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
        
    except Exception as e:
        st.error(f"Error getting student data: {e}")
        return pd.DataFrame()