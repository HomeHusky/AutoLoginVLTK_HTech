from pywinauto import Application
from pywinauto import Desktop
import json
import smtplib
import ssl
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os  # Thêm thư viện os để kiểm tra file tồn tại
import GlobalFunction as GF
import threading
from tkinter import messagebox
import copy
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# === BIẾN TOÀN CỤC ===
stop_flag = False
gom_accounts_info_data = []
gom_account_file = 'gom_accounts.json'
previous_data = {}  # Dùng để lưu trữ số dư tiền của các tài khoản trước khi kiểm tra

EMAIL_ADDRESS = "htechvlnotification@gmail.com"
EMAIL_PASSWORD = "btpwkapwzdknnqfl"
RECIPIENT_EMAIL = "vitrannhat@gmail.com"

def send_email_report(report_data, loop_time_str, ten_may):
    """
    Gửi email báo cáo kết quả kiểm tra tài khoản.

    :param report_data: List chứa các dict như:
        [
            {"account": "PT2ÙTLÙHT11", "old": 900, "new": 979.97, "status": "Tăng"},
            ...
        ]
    :param loop_time_str: Thời gian kiểm tra (ví dụ: "2025-07-09 03:00:00")
    """

    # ===== Soạn HTML nội dung email =====
    html_rows = ""
    for item in report_data:
        color = {"Tăng": "green", "Giảm": "red", "Không đổi": "gray"}.get(item["status"], "black")
        html_rows += f"""
            <tr>
                <td>{item['account']}</td>
                <td>{item['old']}</td>
                <td>{item['new']}</td>
                <td style="color:{color}; font-weight: bold;">{item['status']}</td>
            </tr>
        """

    html_content = f"""
    <html>
        <body>
            <h2 style="color: #2e6c80;">📊 Báo cáo kiểm tra tài khoản VLTK máy {ten_may}</h2>
            <p><b>Thời gian kiểm tra:</b> {loop_time_str}</p>
            <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse;">
                <thead style="background-color: #f2f2f2;">
                    <tr>
                        <th>Tài khoản</th>
                        <th>Tiền cũ</th>
                        <th>Tiền mới</th>
                        <th>Trạng thái</th>
                    </tr>
                </thead>
                <tbody>
                    {html_rows}
                </tbody>
            </table>
            <p style="margin-top: 20px;">📧 Đây là email tự động từ hệ thống kiểm tra nhân vật.</p>
        </body>
    </html>
    """

    # ===== Gửi email =====
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Báo cáo kiểm tra VLTK lúc {loop_time_str}"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL

    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            print("✅ Email đã được gửi thành công.")
    except Exception as e:
        print(f"❌ Lỗi khi gửi email: {e}")

def load_gom_accounts(filepath = 'accounts.json'):
    with open(os.path.join(GF.join_directory_data(), filepath), 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Bước 2: Lấy các tài khoản có is_logged_in = True và is_gom_tien = 1
    filtered_ingames = [account['ingame'] for account in data['accounts'] if account['is_logged_in'] and account['is_gom_tien'] == 1]

    # In kết quả
    return filtered_ingames

def check_accounts_money():
    global gom_accounts_info_data
    gom_accounts = load_gom_accounts()
    try:
        list_control = None
        for attempt in range(3):
            try:
                print(f"Thử kết nối lần {attempt + 1}...")
                backend = GF.get_backend()
                list_control = Application(backend="uia").connect(title_re='^Quan ly nhan vat.*').window(title_re='^Quan ly nhan vat.*').child_window(control_type="List")
                print("Kết nối thành công!")
                break  # Nếu kết nối thành công, thoát vòng lặp
            except Exception as e:
                print(f"Lỗi khi kết nối (lần {attempt + 1}): {e}")
                time.sleep(1)  # Đợi 1 giây trước khi thử lại

        items = list_control.children(control_type="ListItem")
        gom_accounts_info_data = []
        for item in items:
            nextItem = False
            array_name = None
            newdata = []
            countChild = 0
            for child in item.children():
                
                if countChild == 1:
                    array_name = child.window_text()  # Tên tài khoản
                    if array_name not in gom_accounts:
                        countChild += 1
                        nextItem = True
                        continue
                    newdata.append(child.window_text())
                elif countChild == 2:
                    newdata.append(child.window_text())  # tong_tien
                # elif countChild == 3:
                #     newdata.append(child.window_text())  # thu_nhap
                # elif countChild == 4:
                #     newdata.append(child.window_text())  # thoi_gian
                # elif countChild == 6:
                #     newdata.append(child.window_text())  # TDP/C
                # elif countChild == 8:
                #     newdata.append(child.window_text())  # ban_do
                # elif countChild == 9:
                #     newdata.append(child.window_text())  # server
                countChild += 1

            if nextItem: continue
            # Lấy thời gian hiện tại
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Thêm thông tin thời gian vào newdata
            newdata.append(current_time)
            # Chuyển đổi newdata thành chuỗi JSON
            # json_data = json.dumps(newdata, ensure_ascii=False)
            # Ghi dữ liệu vào file JSON 
            gom_accounts_info_data.append(newdata)
        print(f"Dữ liệu: {gom_accounts_info_data}")
        # messagebox.showinfo("Dữ liệu:", gom_accounts_info_data)
    except Exception as e:
        print(f"Lỗi khi kiểm tra tài khoản: {e}")

def auto_check_loop(minutes, ten_may):
    global stop_flag, gom_accounts_info_data, previous_data
    print(f"🔁 Bắt đầu kiểm tra tự động mỗi {minutes} phút...")

    known_accounts = set()  # lưu tài khoản đã từng xuất hiện
    missing_accounts = set()  # lưu tài khoản đã bị văng

    while not stop_flag:
        check_accounts_money()
        new_data = copy.deepcopy(gom_accounts_info_data)
        loop_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = []

        # === Tạo set tài khoản hiện tại
        current_accounts = set(acc[0] for acc in new_data)

        # === Kiểm tra từng tài khoản trong dữ liệu mới
        for acc in new_data:
            name = acc[0]
            money = float(acc[1])
            timestamp = acc[2]

            if name in previous_data:
                old_money = previous_data[name]
                if money > old_money:
                    status = "Tăng"
                    print(f"[{timestamp}] ✅ {name} tăng tiền: {old_money} → {money}")
                elif money < old_money:
                    status = "Giảm"
                    print(f"[{timestamp}] ⚠️ {name} giảm tiền: {old_money} → {money}")
                else:
                    status = "Không đổi"
                    print(f"[{timestamp}] ⏸️ {name} không đổi: {money}")
            elif name in missing_accounts:
                status = "Mới"
                print(f"[{timestamp}] 🔄 {name} quay lại sau khi bị văng. Tiền: {money}")
                missing_accounts.remove(name)
            else:
                status = "Mới"
                print(f"[{timestamp}] 🆕 {name} mới, tiền: {money}")

            report.append({
                "account": name,
                "old": previous_data.get(name, 0),
                "new": money,
                "status": status
            })

            # Lưu vào bộ nhớ
            previous_data[name] = money
            known_accounts.add(name)

        # === Kiểm tra các tài khoản bị mất
        for known_name in known_accounts:
            if known_name not in current_accounts:
                print(f"[{loop_time_str}] ❌ {known_name} bị văng game (không còn trong danh sách).")
                report.append({
                    "account": known_name,
                    "old": previous_data[known_name],
                    "new": 0,
                    "status": "Văng game"
                })
                missing_accounts.add(known_name)

        # === Gửi email
        send_email_report(report, loop_time_str, ten_may)

        # === Đếm ngược trước vòng lặp tiếp theo
        for i in range(minutes * 60):
            if stop_flag:
                print("🛑 Đã dừng kiểm tra.")
                return
            print(f"{minutes * 60 - i} giây còn lại trước khi kiểm tra lại...")
            time.sleep(1)

def start_checking(minutes, ten_may):
    global stop_flag
    stop_flag = False
    t = threading.Thread(target=auto_check_loop, args=(minutes,ten_may), daemon=True)
    t.start()
    print("🔁 Bắt đầu kiểm tra...")

def stop_checking():
    global stop_flag
    stop_flag = True
    print("⛔ Yêu cầu dừng kiểm tra.")

if __name__ == "__main__":
    check_accounts_money()

