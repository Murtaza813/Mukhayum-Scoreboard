# shared/data_loader.py - MINIMAL WORKING VERSION
import streamlit as st

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1-u_eNtf-ApcFdzk9CzNZilRHrLRgxveuxr8j4UQqBmI'

def get_google_sheet():
    """Connect to Google Sheets - SIMPLE VERSION"""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        st.write("🔧 Creating credentials...")
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=SCOPES
        )
        
        st.write("🔧 Authorizing...")
        client = gspread.authorize(credentials)
        
        st.write("🔧 Opening sheet...")
        sheet = client.open_by_key(SPREADSHEET_ID)
        
        st.write(f"✅ Connected to: {sheet.title}")
        return sheet
        
    except Exception as e:
        st.error(f"❌ Google Sheets error: {str(e)}")
        raise e

# Add simple versions of other functions
def get_team_data():
    """Simple team data function"""
    import pandas as pd
    return pd.DataFrame({
        'team': ['الشمس', 'القمر', 'الزهرة', 'المشتري'],
        'points': [100, 200, 300, 400],
        'rank': [4, 3, 2, 1]
    })
