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

# === BIẾN TOÀN CỤC ===
stop_flag = False
gom_accounts_info_data = []
gom_account_file = 'gom_accounts.json'

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

def auto_check_loop(minutes):
    print(f"🔁 Bắt đầu kiểm tra tự động mỗi {minutes} phút...")
    global stop_flag, gom_accounts_info_data
    previous_data = {}
    while not stop_flag:
        check_accounts_money()
        new_data = copy.deepcopy(gom_accounts_info_data)  # ✅ Đảm bảo dữ liệu không bị ghi đè
        for acc in new_data:
            name = acc[0]
            money = float(acc[1]) 
            timestamp = acc[2]

            if name in previous_data:
                old_money = previous_data[name]
                if money > old_money:
                    print(f"[{timestamp}] ✅ {name} tăng tiền: {old_money} → {money}")
                elif money < old_money:
                    print(f"[{timestamp}] ⚠️ {name} giảm tiền: {old_money} → {money}")
                else:
                    print(f"[{timestamp}] ⏸️ {name} không đổi: {money}")
            else:
                print(f"[{timestamp}] 🆕 {name} mới, tiền: {money}")

            previous_data[name] = money

        for i in range(minutes * 60):
            if stop_flag:
                print("🛑 Đã dừng kiểm tra.")
                return
            print(f"{minutes * 60 - i} giây còn lại trước khi kiểm tra lại...")
            time.sleep(1)

def start_checking(minutes):
    global stop_flag
    stop_flag = False
    t = threading.Thread(target=auto_check_loop, args=(minutes,), daemon=True)
    t.start()
    print("🔁 Bắt đầu kiểm tra...")

def stop_checking():
    global stop_flag
    stop_flag = True
    print("⛔ Yêu cầu dừng kiểm tra.")

if __name__ == "__main__":
    check_accounts_money()

