import config
import os
from datetime import datetime
import logging
import gspread
from google.oauth2.service_account import Credentials

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_user_by_phone(phone):
    try:
        logger.info(f"🕒 Server time: {datetime.utcnow()} UTC")
        
        # ตรวจสอบว่าไฟล์ credentials.json มีอยู่
        if not os.path.exists("credentials.json"):
            raise FileNotFoundError("credentials.json not found")
        
        logger.info("🔑 Using credentials.json for authentication")
        
        # ตั้งค่า scope
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        
        # สร้าง client ด้วย gspread
        client = gspread.service_account("credentials.json", scopes=SCOPES)
        
        logger.info("✅ Successfully authenticated with Google API")
        
        # ดึง Sheet ID จาก URL
        if '/d/' in config.GOOGLE_SHEET_URL:
            sheet_id = config.GOOGLE_SHEET_URL.split('/d/')[1].split('/')[0]
        else:
            sheet_id = config.GOOGLE_SHEET_URL.split('/')[-1]
        
        logger.info(f"📊 Accessing sheet ID: {sheet_id}")
        
        # เปิด spreadsheet
        spreadsheet = client.open_by_key(sheet_id)
        sheet = spreadsheet.worksheet(config.SHEET_NAME)
        
        # อ่านข้อมูล
        data = sheet.get_all_values()
        
        if not data:
            logger.warning("⚠️ No data found in sheet")
            return None
        
        headers = data[0]
        
        for row in data[1:]:
            if row and row[0].strip() == phone.strip():
                # เติมข้อมูลให้ครบตามจำนวนคอลัมน์
                full_row = row + [''] * (len(headers) - len(row))
                return dict(zip(headers, full_row))
                
        return None

    except Exception as e:
        logger.error(f"🔥 Critical error: {str(e)}")
        raise
