import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import re

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1-u_eNtf-ApcFdzk9CzNZilRHrLRgxveuxr8j4UQqBmI'

# Keep ONLY this minimal caching for the connection
@st.cache_resource(show_spinner=False)
def get_google_sheet():
    """Connect to Google Sheets - Keep this cached for performance"""
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    return gspread.authorize(credentials).open_by_key(SPREADSHEET_ID)

# NO @st.cache_data decorators on these functions
def get_team_data():
    """Get team leaderboard data - NO CACHE"""
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
                points_cell = ws.acell(f'D{row_num}').value
                
                points = 0
                if points_cell:
                    try:
                        # Clean the value
                        cleaned = str(points_cell).replace(',', '').strip()
                        # Remove any non-numeric except decimal point
                        cleaned = ''.join(ch for ch in cleaned if ch.isdigit() or ch == '.')
                        if cleaned:
                            points = float(cleaned)
                    except:
                        points = 0
                
                teams.append({
                    'team': team_name,
                    'points': points
                })
                
            except Exception as e:
                print(f"Error reading team {team_name}: {e}")
                teams.append({
                    'team': team_name,
                    'points': 0
                })
        
        df = pd.DataFrame(teams)
        df = df.sort_values('points', ascending=False)
        df['rank'] = range(1, len(df) + 1)
        return df
        
    except Exception as e:
        print(f"Error getting team data: {e}")
        # Return minimal fallback
        return pd.DataFrame({
            'team': ['الشمس', 'القمر', 'الزهرة', 'المشتري'],
            'points': [0, 0, 0, 0],
            'rank': [1, 2, 3, 4]
        })

def get_student_data():
    """Get individual student performance - NO CACHE"""
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
        print(f"Error getting student data: {e}")
        return pd.DataFrame()

def get_weekly_data():
    """Get weekly breakdown - NO CACHE"""
    try:
        sheet = get_google_sheet()
        
        # Try Points Table Monthly sheet first
        try:
            ws = sheet.worksheet("Points Table Monthly")
            
            weekly_data = []
            teams = ['الشمس', 'القمر', 'الزهرة', 'المشتري']
            week_names = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5']
            
            # Week data is in rows 6-10 (1-indexed in gspread)
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
                        cell_address = f"{col_letter}{row_num}"
                        cell_value = ws.acell(cell_address).value
                        
                        points = 0
                        if cell_value:
                            try:
                                cleaned = str(cell_value).strip()
                                # Extract numbers
                                numbers = re.findall(r'\d+\.?\d*', cleaned)
                                if numbers:
                                    points = float(numbers[0])
                            except:
                                points = 0
                        
                        weekly_data.append({
                            'team': team_name,
                            'week': week_name,
                            'points': points
                        })
                    except Exception as e:
                        print(f"Error reading {week_name} {team_name}: {e}")
                        weekly_data.append({
                            'team': team_name,
                            'week': week_name,
                            'points': 0
                        })
            
            return pd.DataFrame(weekly_data)
            
        except Exception as e:
            print(f"Error reading Points Table Monthly: {e}")
            # Fallback to OFFICE WORKING
            ws = sheet.worksheet("OFFICE WORKING")
            
            weekly_data = []
            teams = ['الشمس', 'القمر', 'الزهرة', 'المشتري']
            
            week_columns = {
                'Week 1': 'I',
                'Week 2': 'M',
                'Week 3': 'Q',
                'Week 4': 'U',
                'Week 5': 'Y'
            }
            
            team_rows = {
                'الشمس': 48,
                'القمر': 49,
                'الزهرة': 50,
                'المشتري': 51
            }
            
            for team_name, row_num in team_rows.items():
                for week_name, col_letter in week_columns.items():
                    try:
                        cell_value = ws.acell(f"{col_letter}{row_num}").value
                        points = 0
                        
                        if cell_value:
                            try:
                                cleaned = str(cell_value).strip()
                                numbers = re.findall(r'\d+\.?\d*', cleaned)
                                if numbers:
                                    points = float(numbers[0])
                            except:
                                points = 0
                        
                        weekly_data.append({
                            'team': team_name,
                            'week': week_name,
                            'points': points
                        })
                    except Exception as e:
                        print(f"Error reading {team_name} {week_name}: {e}")
                        weekly_data.append({
                            'team': team_name,
                            'week': week_name,
                            'points': 0
                        })
            
            return pd.DataFrame(weekly_data)
        
    except Exception as e:
        print(f"Error in get_weekly_data: {e}")
        # Return empty dataframe
        return pd.DataFrame()

def get_special_achievements(month_sheet):
    """Get special achievements - NO CACHE"""
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
            
            # Check if this is a student row (has points in second column)
            if len(row) >= 2 and row[0] and row[1]:
                student_name = str(row[0]).strip()
                points_str = str(row[1]).strip()
                
                # Skip if it's a header or empty
                if student_name in ["Student", "Activity", "-", ""]:
                    continue
                
                # Try to extract points
                points = 0
                try:
                    # Extract first number found
                    numbers = re.findall(r'\d+', points_str)
                    if numbers:
                        points = int(numbers[0])
                except:
                    points = 0
                
                # Only add if we have a student name
                if student_name and student_name != "-":
                    achievements.append({
                        'student': student_name,
                        'points': points,
                        'category': current_category,
                        'team': "Unknown",  # Will be determined later
                        'month': month_sheet
                    })
        
        return pd.DataFrame(achievements)
    except Exception as e:
        print(f"Error getting achievements from {month_sheet}: {e}")
        return pd.DataFrame()
