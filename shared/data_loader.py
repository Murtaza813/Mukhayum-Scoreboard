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
    """Get weekly breakdown from Points Table Monthly sheet"""
    try:
        import re
        
        sheet = get_google_sheet()
        
        # Try to get data from Points Table Monthly sheet first
        try:
            ws = sheet.worksheet("Points Table Monthly")
            
            # Get data from rows 6-10 (Weeks 1-5)
            # Row indices: Week 1=5, Week 2=6, Week 3=7, Week 4=8, Week 5=9 (0-indexed)
            weekly_data = []
            teams = ['الشمس', 'القمر', 'الزهرة', 'المشتري']
            week_names = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5']
            
            # Column mapping for teams
            team_cols = {
                'الشمس': 0,  # Column A (0-indexed) - adjust based on actual sheet
                'القمر': 1,  # Column B
                'الزهرة': 2,  # Column C
                'المشتري': 3   # Column D
            }
            
            # Try to read the data
            for week_idx, week_name in enumerate(week_names):
                row_num = 5 + week_idx  # Start from row 6 (0-indexed: 5)
                
                try:
                    # Read the entire row
                    row_data = ws.row_values(row_num + 1)  # gspread is 1-indexed
                    
                    for team_name, col_idx in team_cols.items():
                        if col_idx < len(row_data):
                            cell_value = row_data[col_idx]
                            points = 0
                            
                            if cell_value:
                                try:
                                    # Clean and convert
                                    cleaned = str(cell_value).strip()
                                    # Remove any formula references or special characters
                                    if '=' in cleaned:
                                        # Try to extract number from formula
                                        nums = re.findall(r'\d+\.?\d*', cleaned)
                                        if nums:
                                            points = float(nums[0])
                                    else:
                                        points = float(cleaned.replace(',', ''))
                                except:
                                    points = 0
                            
                            weekly_data.append({
                                'team': team_name,
                                'week': week_name,
                                'points': points
                            })
                except:
                    # If row doesn't exist, add zeros
                    for team_name in teams:
                        weekly_data.append({
                            'team': team_name,
                            'week': week_name,
                            'points': 0
                        })
            
            # Check if we got valid data
            total_points = sum(item['points'] for item in weekly_data)
            
            if total_points > 0:
                return pd.DataFrame(weekly_data)
                
        except Exception as e:
            print(f"Error reading Points Table Monthly: {e}")
        
        # Fallback: Read from OFFICE WORKING sheet
        ws = sheet.worksheet("OFFICE WORKING")
        
        # Read team totals from rows 48-51
        weekly_data = []
        teams = ['الشمس', 'القمر', 'الزهرة', 'المشتري']
        week_names = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5']
        
        # Week columns in OFFICE WORKING (January section)
        week_columns = {
            'Week 1': 'I',
            'Week 2': 'M',
            'Week 3': 'Q',
            'Week 4': 'U',
            'Week 5': 'Y'
        }
        
        # Team rows
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
                            # Remove any formula or special characters
                            if '=' in cleaned:
                                # Try to get the calculated value
                                try:
                                    # Extract numbers from formula
                                    nums = re.findall(r'\d+\.?\d*', cleaned)
                                    if nums:
                                        points = sum(float(num) for num in nums[:3])
                                except:
                                    pass
                            else:
                                points = float(cleaned.replace(',', ''))
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
        
        # Return sample data as fallback
        return pd.DataFrame({
            'team': ['الشمس', 'القمر', 'الزهرة', 'المشتري'] * 5,
            'week': ['Week 1']*4 + ['Week 2']*4 + ['Week 3']*4 + ['Week 4']*4 + ['Week 5']*4,
            'points': [
                555.5, 693.0, 604.0, 495.0,  # Week 1
                24.0, 25.0, 26.0, 25.0,      # Week 2
                13.0, 33.0, 19.0, 25.0,      # Week 3
                20.0, 27.0, 27.0, 28.0,      # Week 4
                18.0, 15.0, 26.0, 26.0       # Week 5
            ]
        })
@st.cache_data(ttl=300, show_spinner=False)
def get_special_achievements(month_sheet):
    """Get special achievements from monthly sheets like JAN, FEB, etc."""
    try:
        sheet = get_google_sheet()
        ws = sheet.worksheet(month_sheet)
        
        # Get all data from the sheet
        all_data = ws.get_all_values()
        achievements = []
        
        current_category = ""
        current_team = ""
        
        # Team columns mapping (based on your JAN sheet structure)
        # Column positions: 0=SUN(الشمس), 2=MOON(القمر), 4=VENUS(الزهرة), 6=JUPITER(المشتري)
        team_columns = {
            0: "الشمس",  # SUN column
            2: "القمر",  # MOON column
            4: "الزهرة",  # VENUS column
            6: "المشتري"   # JUPITER column
        }
        
        i = 0
        while i < len(all_data):
            row = all_data[i]
            
            if not any(row):  # Skip empty rows
                i += 1
                continue
            
            # Check for category headers
            row_text = " ".join(str(cell) for cell in row)
            
            if "Nihāʾī Ikhtibār" in row_text:
                current_category = "Final Exam (Nihāʾī Ikhtibār)"
                i += 2  # Skip header and column headers
                continue
            elif "Sub Sanawāt Ikhtibār" in row_text:
                current_category = "Sub-Sanawat Exam (Sub Sanawāt Ikhtibār)"
                i += 2  # Skip header and column headers
                continue
            elif "Marhala Ikhtibār" in row_text:
                current_category = "Stage Exam (Marhala Ikhtibār)"
                i += 2  # Skip header and column headers
                continue
            elif "Monthly Jadīd Target Achievers" in row_text:
                current_category = "Monthly Target Achievers (Monthly Jadīd)"
                i += 2  # Skip header and column headers
                continue
            elif "Student of the Week Achievers" in row_text:
                current_category = "Student of the Week (SOTW)"
                i += 2  # Skip header and column headers
                continue
            elif "Other Activities" in row_text or "Other Activities / Points" in row_text:
                current_category = "Other Activities"
                i += 2  # Skip header and column headers
                continue
            elif "Total points" in row_text:
                # End of achievements section
                break
            
            # Check for student/activity rows
            # In your structure, each team has 2 columns: Student and Points
            for col_idx, team_name in team_columns.items():
                if col_idx < len(row):
                    student = str(row[col_idx]).strip()
                    points_cell = str(row[col_idx + 1]).strip() if col_idx + 1 < len(row) else ""
                    
                    # Check if this is a valid entry (not empty and not a dash)
                    if student and student != "-" and student != "":
                        # Try to parse points
                        points = 0
                        try:
                            # Remove any non-numeric characters except decimal point
                            points_str = "".join(ch for ch in points_cell if ch.isdigit() or ch == '.')
                            if points_str:
                                points = float(points_str)
                        except:
                            points = 0
                        
                        # Only add if we have points or it's a valid student entry
                        if points > 0 or (student and student != "-"):
                            achievements.append({
                                'student': student,
                                'points': points,
                                'category': current_category,
                                'team': team_name,
                                'month': month_sheet
                            })
            
            i += 1
        
        # Debug: Print what was found
        if achievements:
            print(f"Found {len(achievements)} achievements in {month_sheet}")
        
        return pd.DataFrame(achievements)
        
    except Exception as e:
        print(f"Error getting achievements from {month_sheet}: {str(e)}")
        # Return empty dataframe instead of error
        return pd.DataFrame()



