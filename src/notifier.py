import requests

# === Thay bằng Webhook URL bạn tạo ở Discord ===
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1402034497796440348/n3Ude02whBVRkW49lg59GLz6Sp_zGrHzmMG1UBs83c4mRcp7vzd3-qkfkVPD41zt6MJS"

def format_report_discord(report, ten_may, timestamp):
    """
    Tạo nội dung báo cáo gửi lên Discord.
    """
    description = ""
    stt = 0
    total_profit = 0
    for item in report:
        stt = stt + 1
        name = item['account']
        old = item['old']
        new = item['new']
        status = item['status']
        profit = item['profit']

        if status == "Tăng":
            emoji = "🟢"
            total_profit += new - old
        elif status == "Chưa đạt KPI":
            emoji = "⚠️"
            total_profit += new - old
        elif status == "Giảm":
            emoji = "🔻"
        elif status == "Không đổi":
            emoji = "⏸️"
        elif status == "Mới":
            emoji = "🆕"
        elif status == "Văng game":
            emoji = "❌"
        else:
            emoji = "❓"

        description += f"{emoji} {stt} **{name}**: {old} → {new} = {profit:.2f} ({status})\n"

    if total_profit > 0:
        total_line = f"💰 **Tổng tiền tăng:** {total_profit:.2f}\n\n"
    else:
        total_line = ""

    embed = {
        "title": f"📡 Báo cáo máy {ten_may}",
        "description": total_line + description.strip(),
        "color": 0x3498db,  # Xanh dương
        "footer": {
            "text": f"⏰ {timestamp}"
        }
    }

    return embed


def send_discord_report(report, ten_may, timestamp):
    """
    Gửi báo cáo qua Discord Webhook.
    """
    embed = format_report_discord(report, ten_may, timestamp)
    payload = {
        "username": "AutoFixBot",
        "embeds": [embed]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print("✅ Đã gửi Discord thành công.")
        else:
            print(f"❌ Lỗi gửi Discord: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception khi gửi Discord: {e}")

def send_discord_login_report(tenmay, timestamp, is_all_accounts_logged_in):
    """
    Gửi báo cáo đăng nhập thành công qua Discord Webhook.
    """
    if is_all_accounts_logged_in:
        title = "🔔 Thông báo đăng nhập thành công tất cả account"
    else:
        title = "🔔 Thông báo đăng nhập xong nhưng chưa full acc ❌"

    embed = {
        "title": "🔔 Thông báo đăng nhập thành công",
        "description": f"Máy: **{tenmay}**\n⏰ **Thời gian:** {timestamp}",
        "color": 0x2ecc71,  # Xanh lá
        "footer": {
            "text": "AutoLogin VLTK"
        }
    }

    payload = {
        "username": "AutoLoginBot",
        "embeds": [embed]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print("✅ Đã gửi thông báo đăng nhập thành công qua Discord.")
        else:
            print(f"❌ Lỗi gửi thông báo đăng nhập: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception khi gửi thông báo đăng nhập: {e}")