# shared/data_loader.py - NO SAMPLE DATA, ONLY GOOGLE SHEETS
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1-u_eNtf-ApcFdzk9CzNZilRHrLRgxveuxr8j4UQqBmI'

@st.cache_resource(show_spinner=False)
def get_google_sheet():
    """Connect to Google Sheets"""
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    return gspread.authorize(credentials).open_by_key(SPREADSHEET_ID)

def get_team_data():
    """Get team leaderboard data - ONLY REAL DATA"""
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
                # Column D has total points for each team
                cell_value = ws.acell(f'D{row_num}').value
                
                points = 0
                if cell_value:
                    try:
                        # Clean the value
                        cleaned = str(cell_value).strip()
                        
                        # Remove commas and spaces
                        cleaned = cleaned.replace(',', '').replace(' ', '')
                        
                        # Try to convert to float
                        if cleaned:
                            points = float(cleaned)
                    except:
                        points = 0
                
                teams.append({
                    'team': team_name,
                    'points': points
                })
                
            except Exception as e:
                # If can't read data, still add team with 0 points
                teams.append({
                    'team': team_name,
                    'points': 0
                })
        
        # Create dataframe
        df = pd.DataFrame(teams)
        df = df.sort_values('points', ascending=False)
        df['rank'] = range(1, len(df) + 1)
        
        return df
        
    except Exception as e:
        # NO SAMPLE DATA - return empty dataframe
        print(f"ERROR in get_team_data: {e}")
        return pd.DataFrame()

def get_student_data():
    """Get individual student performance - ONLY REAL DATA"""
    try:
        sheet = get_google_sheet()
        ws = sheet.worksheet("OFFICE WORKING")
        
        # Get student data from rows 5-44
        data = ws.get_values('A5:H44')
        
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
        # NO SAMPLE DATA - return empty dataframe
        print(f"ERROR in get_student_data: {e}")
        return pd.DataFrame()

def get_weekly_data():
    """Get weekly breakdown - ONLY REAL DATA"""
    try:
        sheet = get_google_sheet()
        
        # Read from Points Table Monthly sheet
        ws = sheet.worksheet("Points Table Monthly")
        
        weekly_data = []
        teams = ['الشمس', 'القمر', 'الزهرة', 'المشتري']
        week_names = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5']
        
        # Week rows (6-10)
        week_rows = {
            'Week 1': 6,
            'Week 2': 7,
            'Week 3': 8,
            'Week 4': 9,
            'Week 5': 10
        }
        
        # Team columns (B, C, D, E)
        team_cols = {
            'الشمس': 'B',
            'القمر': 'C',
            'الزهرة': 'D',
            'المشتري': 'E'
        }
        
        for week_name, row_num in week_rows.items():
            for team_name, col_letter in team_cols.items():
                try:
                    cell_value = ws.acell(f"{col_letter}{row_num}").value
                    points = 0
                    
                    if cell_value:
                        try:
                            # Try to convert to number
                            cleaned = str(cell_value).strip()
                            cleaned = cleaned.replace(',', '').replace(' ', '')
                            if cleaned:
                                points = float(cleaned)
                        except:
                            points = 0
                    
                    weekly_data.append({
                        'team': team_name,
                        'week': week_name,
                        'points': points
                    })
                except:
                    weekly_data.append({
                        'team': team_name,
                        'week': week_name,
                        'points': 0
                    })
        
        return pd.DataFrame(weekly_data)
        
    except Exception as e:
        # NO SAMPLE DATA - return empty dataframe
        print(f"ERROR in get_weekly_data: {e}")
        return pd.DataFrame()

def get_special_achievements(month_sheet):
    """Get special achievements - ONLY REAL DATA"""
    try:
        sheet = get_google_sheet()
        ws = sheet.worksheet(month_sheet)
        
        data = ws.get_all_values()
        achievements = []
        
        current_category = ""
        for row in data:
            if not row:
                continue
            
            first_cell = str(row[0]) if row else ""
            
            if "Nihāʾī Ikhtibār" in first_cell:
                current_category = "Final Exam"
            elif "Sub Sanawāt Ikhtibār" in first_cell:
                current_category = "Sub-Sanawat Exam"
            elif "Marhala Ikhtibār" in first_cell:
                current_category = "Stage Exam"
            elif "Monthly Jadīd Target Achievers" in first_cell:
                current_category = "Monthly Target Achievers"
            elif "Student of the Week Achievers" in first_cell:
                current_category = "Student of the Week"
            elif "Other Activities" in first_cell:
                current_category = "Other Activities"
            
            if len(row) >= 2 and row[0] and row[1]:
                student_name = str(row[0]).strip()
                points_str = str(row[1]).strip()
                
                if student_name in ["Student", "Activity", "-", ""]:
                    continue
                
                points = 0
                try:
                    # Extract numbers
                    import re
                    numbers = re.findall(r'\d+', points_str)
                    if numbers:
                        points = int(numbers[0])
                except:
                    points = 0
                
                if student_name and student_name != "-" and points > 0:
                    achievements.append({
                        'student': student_name,
                        'points': points,
                        'category': current_category,
                        'team': "Unknown",
                        'month': month_sheet
                    })
        
        return pd.DataFrame(achievements)
    except Exception as e:
        # NO SAMPLE DATA - return empty dataframe
        print(f"ERROR in get_special_achievements: {e}")
        return pd.DataFrame()
