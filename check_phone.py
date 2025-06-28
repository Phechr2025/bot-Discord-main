import gspread
from oauth2client.service_account import ServiceAccountCredentials
import config
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_user_by_phone(phone):
    try:
        # ตรวจสอบเวลาเซิร์ฟเวอร์
        logger.info(f"🕒 Server time: {datetime.utcnow()} UTC")
        
        # ตรวจสอบว่าไฟล์ credentials.json มีอยู่จริง
        if not os.path.exists("credentials.json"):
            raise FileNotFoundError("credentials.json not found")
        
        logger.info("🔑 Using credentials.json for authentication")
        
        # ตั้งค่า scope
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # สร้าง credentials
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials.json", scope
        )
        
        # สร้าง client
        client = gspread.authorize(creds)
        logger.info("✅ Successfully authenticated with Google API")
        
        # เปิด Sheet
        try:
            spreadsheet = client.open_by_url(config.GOOGLE_SHEET_URL)
            sheet = spreadsheet.worksheet(config.SHEET_NAME)
            logger.info(f"📊 Accessing sheet: {config.SHEET_NAME}")
        except Exception as e:
            logger.error(f"❌ Failed to access sheet: {str(e)}")
            raise
        
        # อ่านข้อมูล
        data = sheet.get_all_values()
        headers = data[0]

        for i, row in enumerate(data[1:], start=1):
            if row and row[0].strip() == phone.strip():
                return dict(zip(headers, row))
                
        return None

    except Exception as e:
        logger.error(f"🔥 Critical error: {str(e)}")
        raise
