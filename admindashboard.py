# admindashboard.py - SUPER SIMPLE VERSION
import streamlit as st

st.set_page_config(page_title="Quran Scoreboard", layout="wide")
st.title("🎯 Quran Scoreboard - DEBUG MODE")

st.write("### Step 1: Basic imports")
try:
    import pandas as pd
    st.success("✅ pandas imported")
except Exception as e:
    st.error(f"❌ pandas error: {e}")

st.write("### Step 2: Check Google Sheets connection")
try:
    # Test the data loader
    import sys
    import os
    
    PROJECT_ROOT = "/mount/src/mukhayum-scoreboard"
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    
    st.success("✅ Path configured")
    
    from shared.data_loader import get_google_sheet
    st.success("✅ data_loader imported")
    
    # Test connection
    if st.button("Test Google Sheets Connection"):
        with st.spinner("Connecting..."):
            try:
                sheet = get_google_sheet()
                st.success("✅ Google Sheets Connected!")
                
                # List worksheets
                worksheets = sheet.worksheets()
                st.write(f"Found {len(worksheets)} worksheets:")
                for ws in worksheets:
                    st.write(f"- {ws.title}")
                    
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")
                
except ImportError as e:
    st.error(f"❌ Import error: {e}")
    st.code(str(e))
except Exception as e:
    st.error(f"❌ Other error: {e}")
    st.code(str(e))

st.write("### Step 3: Check secrets")
try:
    secrets = st.secrets["gcp_service_account"]
    st.success("✅ Secrets loaded")
    st.write(f"Project ID: {secrets.get('project_id', 'Not found')}")
except:
    st.error("❌ Secrets not found")

st.write("### App Status: Ready")
st.info("If you see all green checkmarks above, the basic setup is working.")
