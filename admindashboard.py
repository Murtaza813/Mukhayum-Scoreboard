# shared/data_loader.py - MINIMAL VERSION
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1-u_eNtf-ApcFdzk9CzNZilRHrLRgxveuxr8j4UQqBmI'

@st.cache_resource(show_spinner=False)
def get_google_sheet():
    """Connect to Google Sheets"""
    try:
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=SCOPES
        )
        client = gspread.authorize(credentials)
        return client.open_by_key(SPREADSHEET_ID)
    except Exception as e:
        st.error(f"Google Sheets connection error: {e}")
        raise e

def get_team_data():
    """Get team leaderboard data - SIMPLE VERSION"""
    try:
        sheet = get_google_sheet()
        ws = sheet.worksheet("OFFICE WORKING")
        
        # Simple: Read from known positions
        teams_data = []
        
        # Team names and their row numbers
        team_rows = [
            ('الشمس', 48),
            ('القمر', 49),
            ('الزهرة', 50),
            ('المشتري', 51)
        ]
        
        for team_name, row_num in team_rows:
            try:
                # Read points from column D
                points_cell = ws.acell(f'D{row_num}').value
                points = 0
                
                if points_cell:
                    try:
                        # Clean the value
                        cleaned = str(points_cell).replace(',', '').strip()
                        # Remove any non-numeric except decimal
                        cleaned = ''.join(ch for ch in cleaned if ch.isdigit() or ch == '.')
                        if cleaned:
                            points = float(cleaned)
                    except:
                        points = 0
                
                teams_data.append({
                    'team': team_name,
                    'points': points
                })
                
            except Exception as e:
                print(f"Error reading {team_name}: {e}")
                teams_data.append({
                    'team': team_name,
                    'points': 0
                })
        
        # Create dataframe and add ranks
        df = pd.DataFrame(teams_data)
        df = df.sort_values('points', ascending=False)
        df['rank'] = range(1, len(df) + 1)
        
        return df
        
    except Exception as e:
        print(f"Error in get_team_data: {e}")
        # Return fallback data
        return pd.DataFrame({
            'team': ['الشمس', 'القمر', 'الزهرة', 'المشتري'],
            'points': [0, 0, 0, 0],
            'rank': [1, 2, 3, 4]
        })

def get_student_data():
    """Placeholder - will implement later"""
    return pd.DataFrame()

def get_weekly_data():
    """Placeholder - will implement later"""
    return pd.DataFrame()

def get_special_achievements(month_sheet):
    """Placeholder - will implement later"""
    return pd.DataFrame()
