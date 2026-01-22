import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '12FWohzX2yJXxvC4xTu3-NSTzLgJogQOmp2LtDLDaw7I'

@st.cache_resource(show_spinner=False)
def get_google_sheet():
    """Connect to Google Sheets"""
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    return gspread.authorize(credentials).open_by_key(SPREADSHEET_ID)

@st.cache_data(ttl=60, show_spinner=False)
def get_team_data():
    """Get team leaderboard data"""
    try:
        sheet = get_google_sheet()
        ws = sheet.worksheet("OFFICE WORKING")
        
        # Teams are in rows 48-51
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
        
    except Exception as e:
        st.error(f"Error getting team data: {e}")
        # Return fallback data
        return pd.DataFrame({
            'team': ['الشمس', 'القمر', 'الزهرة', 'المشتري'],
            'points': [67, 58, 45, 50],
            'rank': [1, 2, 3, 4]
        })

@st.cache_data(ttl=120, show_spinner=False)
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

@st.cache_data(ttl=300, show_spinner=False)
def get_weekly_data():
    """Get weekly breakdown"""
    try:
        sheet = get_google_sheet()
        ws = sheet.worksheet("OFFICE WORKING")
        
        # Weekly points from your sheet structure
        weekly_data = []
        teams = ['الشمس', 'القمر', 'الزهرة', 'المشتري']
        
        # Try to get actual weekly data
        week_columns = ['I', 'M', 'Q', 'U', 'Y']
        week_names = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5']
        
        # Team rows in the totals section
        team_rows = {
            'الشمس': 48,
            'القمر': 49, 
            'الزهرة': 50,
            'المشتري': 51
        }
        
        for team in teams:
            row = team_rows.get(team, 48)
            for i, col in enumerate(week_columns):
                try:
                    cell_value = ws.acell(f'{col}{row}').value
                    if cell_value:
                        try:
                            points = float(cell_value)
                        except:
                            points = 0
                    else:
                        points = 0
                except:
                    points = 0
                
                weekly_data.append({
                    'team': team,
                    'week': week_names[i],
                    'points': points
                })
        
        return pd.DataFrame(weekly_data)
        
    except Exception as e:
        st.error(f"Error getting weekly data: {e}")
        # Return empty dataframe
        return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def get_special_achievements(month_sheet):
    """Get special achievements with proper team detection"""
    try:
        sheet = get_google_sheet()
        ws = sheet.worksheet(month_sheet)
        
        data = ws.get_all_values()
        achievements = []
        
        current_category = ""
        for row in data:
            if not row:
                continue
            
            # Check for category headers
            if "Nihāʾī Ikhtibār" in row[0]:
                current_category = "Final Exam"
            elif "Sanawāt Ikhtibār" in row[0]:
                current_category = "Sanawat Exam"
            elif "Sub Sanawāt Ikhtibār" in row[0]:
                current_category = "Sub-Sanawat Exam"
            elif "Monthly Jadīd Target Achievers" in row[0]:
                current_category = "Monthly Target Achievers"
            elif "Student of the Week Achievers" in row[0]:
                current_category = "Student of the Week"
            
            # Check for student rows (has points in second column)
            if len(row) >= 2 and row[1] and row[1].isdigit():
                student_name = row[0]
                
                # Determine team from student name based on your patterns
                team = "Unknown"
                
                # Check team indicators in the name
                team_keywords = {
                    'الشمس': ['Anwar', 'أنور'],
                    'القمر': ['Aqmar', 'أقمر'],
                    'الزهرة': ['Azhar', 'أزهر'],
                    'المشتري': ['Juyushi', 'جيوشي']
                }
                
                for team_name, keywords in team_keywords.items():
                    for keyword in keywords:
                        if keyword in student_name:
                            team = team_name
                            break
                    if team != "Unknown":
                        break
                
                achievements.append({
                    'student': student_name,
                    'points': int(row[1]),
                    'category': current_category,
                    'team': team,
                    'month': month_sheet
                })
        
        return pd.DataFrame(achievements)
    except Exception as e:
        st.error(f"Error getting achievements from {month_sheet}: {e}")
        return pd.DataFrame()
