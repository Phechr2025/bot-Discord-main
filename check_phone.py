import gspread
from oauth2client.service_account import ServiceAccountCredentials
import config
import os

def find_user_by_phone(phone):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)

    client = gspread.authorize(creds)
    sheet = client.open_by_url(config.GOOGLE_SHEET_URL).worksheet(config.SHEET_NAME)
    data = sheet.get_all_values()

    headers = data[0]  # แถวหัวตาราง เช่น ['เบอร์โทร', 'ชื่อ', 'สถานะ', ...]
    
    for i in range(1, len(data)):  # ข้ามแถวหัวตาราง
        row = data[i]
        if len(row) > 0 and row[0].strip() == phone.strip():  # ตรวจเบอร์ในคอลัมน์ A
            return dict(zip(headers, row))  # คืนค่าแถวทั้งแถวแบบเป็น dictionary

    return None
