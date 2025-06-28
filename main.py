import discord
from discord.ext import commands
from check_phone import find_user_by_phone
import config
import aiohttp
import asyncio
import time
import io
import os
from keep_alive import server_on  # เพิ่มส่วนนี้

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ บอททำงานแล้ว: {bot.user.name}")

if not os.path.exists("credentials.json"):
    print("❌ ไม่พบไฟล์ credentials.json ที่ตำแหน่งนี้:", os.getcwd())
else:
    print("✅ พบไฟล์ credentials.json ที่:", os.getcwd())

# เรียกใช้ keep_alive server
server_on()

# ✅ แปลงลิงก์ Google Drive เป็น direct download
def convert_drive_view_link(url):
    if "drive.google.com/file/d/" in url:
        try:
            file_id = url.split("/d/")[1].split("/")[0]
            return f"https://drive.google.com/uc?export=download&id={file_id}"
        except:
            return url
    return url

# ✅ ส่งไฟล์พร้อมนับถอยหลังทีละวินาที
async def send_file_with_countdown(ctx, url, label="ไฟล์หลักฐาน"):
    view_url = convert_drive_view_link(url)
    try:
        start_time = time.time()
        async with aiohttp.ClientSession() as session:
            async with session.get(view_url) as resp:
                if resp.status != 200:
                    await ctx.send(f"⚠️ ไม่สามารถดูไฟล์ {label} ได้ (status: {resp.status})")
                    return

                content_type = resp.headers.get("Content-Type", "")
                data = await resp.read()
                load_time = int(time.time() - start_time)

                countdown = max(1, load_time)
                msg = await ctx.send(f"⏳ จะส่ง {label} ใน {countdown} วินาที...")

                for remaining in range(countdown - 1, 0, -1):
                    await asyncio.sleep(1)
                    await msg.edit(content=f"⏳ จะส่ง {label} ใน {remaining} วินาที...")

                await asyncio.sleep(1)
                await msg.delete()

                if "image" in content_type:
                    embed = discord.Embed(title=f"📷 {label}", color=0x2ecc71)
                    embed.set_image(url=view_url)
                    await ctx.send(embed=embed)
                elif "video" in content_type:
                    file = discord.File(fp=io.BytesIO(data), filename="video.mp4")
                    await ctx.send(file=file)
                else:
                    await ctx.send(f"📎 {label}: ไม่รองรับไฟล์ประเภทนี้")
    except Exception as e:
        await ctx.send(f"❌ เกิดข้อผิดพลาดกับ {label}: {str(e)}")

@bot.command(name="ตรวจสอบ")
async def ตรวจสอบ(ctx, phone: str = None):
    if ctx.channel.id != config.TARGET_CHANNEL_ID:
        await ctx.send("❌ ใช้คำสั่งนี้ได้เฉพาะในห้องที่กำหนดเท่านั้น")
        return

    if not phone:
        await ctx.send("⚠️ กรุณาพิมพ์เบอร์ด้วย เช่น `!ตรวจสอบ 0812345678`")
        return

    result = find_user_by_phone(phone)
    if result:
        embed = discord.Embed(title="📋 รายละเอียด", color=0x3498db)

        keys = list(result.keys())
        col_d_key = keys[3] if len(keys) > 3 else None
        col_e_key = keys[4] if len(keys) > 4 else None

        col_d_value = result.get(col_d_key, "") if col_d_key else ""
        col_e_value = result.get(col_e_key, "") if col_e_key else ""

        # ❌ ไม่แสดง D/E ใน embed หลัก
        for key, value in result.items():
            if key not in [col_d_key, col_e_key]:
                embed.add_field(name=key, value=value or "—", inline=False)

        await ctx.send(embed=embed)

        # ✅ จัดการลิงก์จาก D
        if "drive.google.com/file/d/" in col_d_value:
            await send_file_with_countdown(ctx, col_d_value, label="ไฟล์หลักฐาน 1")
        elif col_d_value.strip():
            await ctx.send(f"📎 {col_d_key}: {col_d_value}")

        # ✅ จัดการลิงก์จาก E
        if "drive.google.com/file/d/" in col_e_value:
            await send_file_with_countdown(ctx, col_e_value, label="ไฟล์หลักฐาน 2")
        elif col_e_value.strip():
            await ctx.send(f"📎 {col_e_key}: {col_e_value}")

    else:
        await ctx.send("❌ ไม่พบเบอร์นี้ในระบบ")

bot.run(config.DISCORD_TOKEN)