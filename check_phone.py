import gspread
from oauth2client.service_account import ServiceAccountCredentials
import config
import os
from pathlib import Path

def find_user_by_phone(phone):
    try:
        # ตรวจสอบไฟล์ credentials
        creds_path = Path(__file__).parent / "credentials.json"
        if not creds_path.exists():
            raise FileNotFoundError("credentials.json not found")
            
        print(f"🔑 Using credentials from: {creds_path}")

        # ตั้งค่า scope
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # สร้าง credentials
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            str(creds_path), scope
        )
        
        # สร้าง client
        client = gspread.authorize(creds)
        print("🔗 Connected to Google Sheets API")

        # เปิด Sheet
        sheet = client.open_by_url(config.GOOGLE_SHEET_URL).worksheet(config.SHEET_NAME)
        print(f"📊 Accessing sheet: {config.SHEET_NAME}")
        
        # อ่านข้อมูล
        data = sheet.get_all_values()
        headers = data[0]

        for i, row in enumerate(data[1:], start=1):
            if row and row[0].strip() == phone.strip():
                return dict(zip(headers, row))
                
        return None

    except Exception as e:
        print(f"❌ Error accessing Google Sheet: {str(e)}")
        raise
