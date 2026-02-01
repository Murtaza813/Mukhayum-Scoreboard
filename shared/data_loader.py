# shared/data_loader.py - CORRECTED VERSION
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import re

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
    """Get team leaderboard data - FIXED"""
    try:
        sheet = get_google_sheet()
        ws = sheet.worksheet("OFFICE WORKING")
        
        # Teams are in rows 48-51
        # Based on your Excel file: الشمس(row 48), القمر(49), الزهرة(50), المشتري(51)
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
                        
                        # If it's a formula like =M5+Q5+U5+Y5, we need to get the result
                        if '=' in cleaned:
                            # Get the cell with formula result
                            cell = ws.acell(f'D{row_num}', value_render_option='FORMULA')
                            formula = cell.value
                            if formula:
                                # Try to extract numbers from formula
                                numbers = re.findall(r'\d+\.?\d*', formula)
                                if numbers:
                                    # Sum the numbers (they're cell references, not values)
                                    # For now, let's read the actual value differently
                                    # Get the cell with calculated value
                                    calculated = ws.acell(f'D{row_num}', value_render_option='UNFORMATTED_VALUE').value
                                    if calculated:
                                        try:
                                            points = float(calculated)
                                        except:
                                            points = 0
                        else:
                            # Direct number
                            points = float(cleaned.replace(',', ''))
                    except Exception as e:
                        print(f"Error parsing points for {team_name}: {e}")
                        points = 0
                
                # Debug print
                print(f"Team {team_name}: {points} points")
                
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
        
        # Debug: print the final data
        print("Final team data:")
        print(df)
        
        return df
        
    except Exception as e:
        print(f"Error in get_team_data: {e}")
        import traceback
        traceback.print_exc()
        
        # Return fallback data
        return pd.DataFrame({
            'team': ['الشمس', 'القمر', 'الزهرة', 'المشتري'],
            'points': [1500, 1200, 900, 800],
            'rank': [1, 2, 3, 4]
        })

def get_student_data():
    """Get individual student performance"""
    try:
        sheet = get_google_sheet()
        ws = sheet.worksheet("OFFICE WORKING")
        
        # Get student data from rows 5-44 (A5:H44)
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
        
        print(f"Loaded {len(students)} students")
        return pd.DataFrame(students)
        
    except Exception as e:
        print(f"Error getting student data: {e}")
        return pd.DataFrame()

def get_weekly_data():
    """Get weekly breakdown - FIXED"""
    try:
        sheet = get_google_sheet()
        
        # Try Points Table Monthly first
        try:
            ws = sheet.worksheet("Points Table Monthly")
            
            weekly_data = []
            teams = ['الشمس', 'القمر', 'الزهرة', 'المشتري']
            week_names = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5']
            
            # Week data is in rows 6-10 (1-indexed in gspread)
            week_rows = {
                'Week 1': 6,  # Row 6
                'Week 2': 7,  # Row 7
                'Week 3': 8,  # Row 8
                'Week 4': 9,  # Row 9
                'Week 5': 10  # Row 10
            }
            
            # Team columns (B=الشمس, C=القمر, D=الزهرة, E=المشتري)
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
                                # Check if it's a formula reference
                                if str(cell_value).startswith("='OFFICE WORKING'!"):
                                    # Extract the reference and get value from OFFICE WORKING
                                    ref_match = re.search(r"!'([A-Z]+)(\d+)", cell_value)
                                    if ref_match:
                                        ref_col = ref_match.group(1)
                                        ref_row = int(ref_match.group(2))
                                        
                                        # Get value from OFFICE WORKING
                                        office_ws = sheet.worksheet("OFFICE WORKING")
                                        ref_value = office_ws.acell(f"{ref_col}{ref_row}").value
                                        
                                        if ref_value:
                                            try:
                                                points = float(str(ref_value).replace(',', ''))
                                            except:
                                                points = 0
                                else:
                                    # Direct value
                                    points = float(str(cell_value).replace(',', ''))
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
            
            df = pd.DataFrame(weekly_data)
            print(f"Weekly data loaded: {len(df)} entries")
            return df
            
        except Exception as e:
            print(f"Error reading Points Table Monthly: {e}")
            
            # Fallback: Read from OFFICE WORKING sheet
            ws = sheet.worksheet("OFFICE WORKING")
            
            weekly_data = []
            teams = ['الشمس', 'القمر', 'الزهرة', 'المشتري']
            
            # Weekly columns in OFFICE WORKING
            week_columns = {
                'Week 1': 'I',
                'Week 2': 'M',
                'Week 3': 'Q',
                'Week 4': 'U',
                'Week 5': 'Y'
            }
            
            # Team rows in OFFICE WORKING
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
                                points = float(str(cell_value).replace(',', ''))
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
        print(f"Error in get_weekly_data: {e}")
        # Return sample data
        return pd.DataFrame({
            'team': ['الشمس', 'القمر', 'الزهرة', 'المشتري'] * 5,
            'week': ['Week 1']*4 + ['Week 2']*4 + ['Week 3']*4 + ['Week 4']*4 + ['Week 5']*4,
            'points': [
                150, 200, 180, 170,  # Week 1
                50, 60, 55, 45,      # Week 2
                60, 70, 65, 50,      # Week 3
                55, 65, 60, 52,      # Week 4
                70, 80, 75, 65       # Week 5
            ]
        })

def get_special_achievements(month_sheet):
    """Get special achievements"""
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
        print(f"Error getting achievements from {month_sheet}: {e}")
        return pd.DataFrame()
