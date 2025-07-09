import requests

# === Thay bằng Webhook URL bạn tạo ở Discord ===
DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1392438088936063087/hfufprc6vsN9EuseRFgMNYZl_5O3odEk-oQzshCC2pFYUptXDv8srW5_ycx42bmpkef7"

def format_report_discord(report, ten_may, timestamp):
    """
    Tạo nội dung báo cáo gửi lên Discord.
    """
    description = ""
    stt = 0
    for item in report:
        stt = stt + 1
        name = item['account']
        old = item['old']
        new = item['new']
        status = item['status']

        if status == "Tăng":
            emoji = "🟢"
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

        description += f"{emoji} {stt} **{name}**: {old} → {new} ({status})\n"

    embed = {
        "title": f"📡 Báo cáo máy {ten_may}",
        "description": description.strip(),
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
