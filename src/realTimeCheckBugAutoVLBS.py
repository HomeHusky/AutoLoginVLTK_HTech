from pywinauto import Application
from pywinauto import Desktop
import json
import smtplib
import ssl
import time
from datetime import datetime, timedelta
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
from notifier import send_discord_report
from fixErrorAccounts import getLowBoodAccounts, fixLowBloodAccountsWithRepair, fixErrorAccounts, relogin_lost_accounts, fixLowBloodAccounts, fix_account_stuck_on_map_Sa_Mac, run_kill_hung_vo_lam
from tkinter import ttk
import tkinter as tk
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import mongoConnection as MONGO_CONN
from modules.mongodb_manager import mongodb_manager

# === BIẾN TOÀN CỤC ===
kpi_1m = (48/24)/60  # KPI mặc định cho tài khoản thường (Kv/phút) - 1 giờ tăng 2 Kv
kpi_gom_1m = (96/24)/60  # KPI cho tài khoản gom tiền (Kv/phút) - 1 giờ tăng 4 Kv (Gấp đôi)
stop_flag = False
gom_accounts_info_data = []
gom_account_file = 'gom_accounts.json'
gom_accounts_list = []  # Danh sách tài khoản gom tiền
previous_data = {}  # Dùng để lưu trữ số dư tiền của các tài khoản trước khi kiểm tra

EMAIL_ADDRESS = "htechvlnotification@gmail.com"
EMAIL_PASSWORD = "btpwkapwzdknnqfl"
RECIPIENT_EMAIL = "vitrannhat@gmail.com"

def format_time_to_minute_second(seconds: int) -> str:
    """
    Chuyển số giây thành chuỗi dạng 'MM phút SS giây'.
    """
    m, s = divmod(seconds, 60)
    return f"{m:02d} phút {s:02d} giây"

def update_accounts_online_status(current_accounts):
    """
    Cập nhật trạng thái is_logged_in trong accounts.json
    dựa vào danh sách accounts đang online
    """
    try:
        filepath = os.path.join(GF.join_directory_data(), 'accounts.json')
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Cập nhật trạng thái
        for account in data['accounts']:
            ingame = account['ingame']
            if ingame in current_accounts:
                account['is_logged_in'] = True
            else:
                account['is_logged_in'] = False
        
        # Lưu lại file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"✅ Đã cập nhật trạng thái online cho {len(current_accounts)} accounts")
    except Exception as e:
        print(f"❌ Lỗi cập nhật trạng thái online: {e}")

def update_mongodb_server_status():
    """
    Cập nhật thông tin máy chủ lên MongoDB
    Tự động tạo collection 'server_status' nếu chưa tồn tại
    """
    try:
        print("📤 Đang cập nhật thông tin máy chủ lên MongoDB...")
        
        # Kết nối và cập nhật
        if mongodb_manager.connect():
            success = mongodb_manager.update_server_status(collection_name="server_status")
            mongodb_manager.close()
            
            if success:
                print("✅ Đã cập nhật MongoDB thành công!")
            else:
                print("❌ Cập nhật MongoDB thất bại!")
        else:
            print("❌ Không thể kết nối MongoDB!")
            
    except Exception as e:
        print(f"❌ Lỗi cập nhật MongoDB: {e}")

# === CÁC HÀM TOÀN CỤC ===
# Hàm này sẽ tải danh sách tài khoản từ file accounts.json
# và lọc ra các tài khoản đang đăng nhập và có is_gom_tien = 1
# Trả về dictionary: {ingame: kpi_gom}
def load_gom_accounts(filepath = 'accounts.json'):
    with open(os.path.join(GF.join_directory_data(), filepath), 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Lấy các tài khoản có is_logged_in = True và is_gom_tien = 1
    # Trả về dict với ingame và KPI riêng (nếu có)
    gom_accounts_dict = {}
    for account in data['accounts']:
        if account['is_logged_in'] and account['is_gom_tien'] == 1:
            ingame = account['ingame']
            kpi_gom = account.get('kpi_gom', '')  # Lấy KPI riêng, nếu không có thì ''
            gom_accounts_dict[ingame] = kpi_gom
    
    return gom_accounts_dict

# === LƯU DỮ LIỆU VÀO FILE ===
def save_snapshot(ten_may, report):
    folder = "data_logs"
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, f"{ten_may}_log.json")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Format dữ liệu
    snapshot = {
        "time": now_str,
        "accounts": [{"account": acc["account"], "money": acc["new"]} for acc in report]
    }

    data = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = []

    data.append(snapshot)

    # Ghi lại
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# === LƯU DỮ LIỆU VÀO MONGODB ===
def save_money_data_to_mongo(ten_may, total_profit):
    """
    Lưu dữ liệu tiền từng account lên MongoDB
    :param json_data: dict kiểu {"acc1": [{"money": .., "time": ..}, ...], ...}
    :param ten_may: tên máy (str)
    """
    client, collection = MONGO_CONN.connect_mongo()
    
    document = {
        "ten_may": ten_may,
        "loi_nhuan": total_profit,
        "time": datetime.now()
    }
    collection.insert_one(document)
    
    client.close()

# === TÍNH TOÁN THU NHẬP TRONG 24 GIỜ QUA TRÊN MONGODB===
def get_24h_income_from_mongo(ten_may):
    """
    Tính tổng tiền tăng của tất cả account trong 24h gần nhất cho một máy.
    :param ten_may: tên máy (str)
    :return: tổng tiền tăng (float)
    """
    client, collection = MONGO_CONN.connect_mongo()

    now = datetime.now()
    time_24h_ago = now - timedelta(hours=24)

    total_income = 0

    # Lấy danh sách các account duy nhất của máy
    accounts = collection.distinct("account", {"ten_may": ten_may})

    for acc in accounts:
        # Lấy dòng mới nhất
        latest = collection.find_one(
            {"ten_may": ten_may, "account": acc},
            sort=[("time", -1)]
        )

        # Lấy dòng gần nhất trước mốc 24h
        old = collection.find_one(
            {
                "ten_may": ten_may,
                "account": acc,
                "time": {"$lte": time_24h_ago}
            },
            sort=[("time", -1)]
        )

        if latest and old:
            income = latest["money"] - old["money"]
            total_income += income
    client.close()
    return total_income

# === TÍNH TOÁN THU NHẬP TRONG THÁNG HIỆN TẠI TRÊN MONGODB===
def get_month_income(ten_may):
    """
    Tính tổng tiền tăng trong tháng hiện tại cho một máy.
    So sánh dòng mới nhất với dòng đầu tiên trong tháng.
    :param ten_may: tên máy (str)
    :return: tổng tiền tăng trong tháng (float)
    """
    client, collection = MONGO_CONN.connect_mongo()

    now = datetime.now()
    start_of_month = datetime(now.year, now.month, 1)

    total_income = 0
    accounts = collection.distinct("account", {"ten_may": ten_may})

    for acc in accounts:
        # Dòng mới nhất trong tháng
        latest = collection.find_one(
            {
                "ten_may": ten_may,
                "account": acc,
                "time": {"$gte": start_of_month}
            },
            sort=[("time", -1)]
        )

        # Dòng đầu tiên trong tháng
        first = collection.find_one(
            {
                "ten_may": ten_may,
                "account": acc,
                "time": {"$gte": start_of_month}
            },
            sort=[("time", 1)]
        )

        if latest and first:
            income = latest["money"] - first["money"]
            total_income += income

    client.close()
    return total_income

# === TÓM TẮT THU NHẬP TRONG 24 GIỜ QUA ===
def summarize_last_24h_income(ten_may):
    file_path = f"data_logs/{ten_may}_log.json"
    if not os.path.exists(file_path):
        print("❌ Không tìm thấy dữ liệu.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if len(data) < 2:
        print("⚠️ Chưa đủ dữ liệu để tính.")
        return

    now = datetime.now()
    threshold_time = now - timedelta(hours=24)

    # Tìm snapshot cũ nhất trước ngưỡng
    oldest = None
    latest = data[-1]

    for entry in reversed(data):
        entry_time = datetime.strptime(entry["time"], "%Y-%m-%d %H:%M:%S")
        if entry_time <= threshold_time:
            oldest = entry
            break

    if not oldest:
        print("⚠️ Không có snapshot đủ cũ (24h trước).")
        return

    # Tính thu nhập
    old_money_map = {acc["account"]: acc["money"] for acc in oldest["accounts"]}
    new_money_map = {acc["account"]: acc["money"] for acc in latest["accounts"]}

    total_income = 0
    for acc, new_money in new_money_map.items():
        old_money = old_money_map.get(acc, 0)
        income = new_money - old_money
        print(f"💰 {acc}: {old_money:.2f} → {new_money:.2f} = +{income:.2f}")
        total_income += income

    print(f"\n📊 Tổng tiền máy {ten_may} kiếm được trong 24 giờ qua: {total_income:.2f} [vạn]")

# === XÓA CÁC SNAPSHOT CŨ HƠN MỘT SỐ NGÀY ===
def clean_old_snapshots(ten_may, days_to_keep=2, folder="data_logs"):
    file_path = os.path.join(folder, f"{ten_may}_log.json")
    if not os.path.exists(file_path):
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        print(f"❌ Không thể đọc {file_path}")
        return

    cutoff_time = datetime.now() - timedelta(days=days_to_keep)
    new_data = []

    for entry in data:
        try:
            entry_time = datetime.strptime(entry["time"], "%Y-%m-%d %H:%M:%S")
            if entry_time >= cutoff_time:
                new_data.append(entry)
        except Exception as e:
            print(f"⚠️ Bỏ qua dòng lỗi: {e}")

    # Ghi lại file nếu có thay đổi
    if len(new_data) != len(data):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        print(f"🧹 Đã xóa {len(data) - len(new_data)} snapshot cũ trong {file_path}")

# === LẤY BẢNG LỢI NHUẬN TRONG 24 GIỜ QUA ===
# Hàm này sẽ lấy dữ liệu từ file log và tạo bảng lợi nhuận cho các tài khoản trong 24 giờ qua
# Trả về danh sách các dict với cấu trúc:
def get_profit_table_last_24h(ten_may):
    file_path = f"data_logs/{ten_may}_log.json"
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if len(data) < 2:
        return []

    now = datetime.now()
    time_24h_ago = now - timedelta(hours=24)

    # Tìm snapshot sớm nhất >= 24h trước
    start_snapshot = None
    for entry in data:
        entry_time = datetime.strptime(entry["time"], "%Y-%m-%d %H:%M:%S")
        if entry_time <= time_24h_ago:
            start_snapshot = entry
        else:
            break

    if not start_snapshot:
        return []

    end_snapshot = data[-1]  # snapshot hiện tại

    # Map acc → money
    start_map = {acc["account"]: acc["money"] for acc in start_snapshot["accounts"]}
    end_map = {acc["account"]: acc["money"] for acc in end_snapshot["accounts"]}

    # Tạo bảng dạng array cho hiển thị UI
    profit_table = []
    for acc, end_money in end_map.items():
        start_money = start_map.get(acc, 0)
        profit = end_money - start_money
        profit_table.append({
            "account": acc,
            "start": start_money,
            "end": end_money,
            "profit": profit,
            "start_time": start_snapshot["time"],
            "end_time": end_snapshot["time"]
        })

    return profit_table

# === RENDER BẢNG LỢI NHUẬN TRONG 24 GIỜ QUA TRÊN GIAO DIỆN ===
def render_profit_table_ui(frame, ten_may):
    for widget in frame.winfo_children():
        widget.destroy()  # Xóa bảng cũ

    table = get_profit_table_last_24h(ten_may)

    # Tính tổng profit
    total_profit = sum(row["profit"] for row in table)

    # Tạo label hiển thị tổng lợi nhuận
    label = tk.Label(
        frame,
        text=f"{total_profit:+.2f}",
        font=("Arial", 14, "bold"),
        fg="green" if total_profit >= 0 else "red"
    )
    label.pack(expand=True, fill="both", padx=10, pady=10)

def render_current_online_accounts(frame, nameAutoVLBS):
    account_online = load_len_accounts_online(nameAutoVLBS)
    # Tạo label hiển thị tổng lợi nhuận
    label = tk.Label(
        frame,
        text=f"{account_online} online",
        font=("Arial", 14, "bold"),
        fg="green" if account_online > 0 else "red"
    )
    label.pack(expand=True, fill="both", padx=10, pady=10)

def load_len_accounts_online(nameAutoVLBS):
    try:
        list_control = None
        GF.checkBothAutoVlbsAndQuanLyRunning(nameAutoVLBS)
        app = Application(backend="uia").connect(title_re=nameAutoVLBS)
        dlg = app.window(title_re=nameAutoVLBS)

        # Lấy tất cả control loại List trong cửa sổ
        list_controls = dlg.descendants(control_type="List")

        # Kiểm tra số lượng và lấy theo điều kiện
        if len(list_controls) == 3:
            print("Có 3 List control, lấy cái đầu tiên.")
            list_control = list_controls[2]  # lấy cái đầu tiên
        else:
            list_control = dlg.child_window(control_type="List")  # mặc định nếu chỉ có 1   

        items = list_control.children(control_type="ListItem")
        return len(items)
    except Exception as e:
        print(f"Lỗi khi lấy số lượng tài khoản online: {e}")
        return 0

# === HÀM GỬI MAIL ===
# Hàm này sẽ gửi email báo cáo kết quả kiểm tra tài khoản
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

def sleep_until_next_hour():
    now = datetime.now()
    # Calculate next hour (add 1 hour, set minutes and seconds to 0)
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    seconds_to_sleep = (next_hour - now).total_seconds()
    print(f"⏳ Sleeping for {int(seconds_to_sleep)} seconds until next hour: {next_hour.strftime('%H:%M:%S')}")
    time.sleep(seconds_to_sleep)

# === KIỂM TRA TÀI KHOẢN VÀ LẤY DỮ LIỆU ===
# Hàm này sẽ kết nối với ứng dụng, lấy danh sách tài khoản và số dư tiền của chúng
# Lưu ý: Hàm này cần được gọi trong một luồng riêng biệt để tránh làm treo giao diện chính
def check_accounts_money():
    global gom_accounts_info_data
    gom_accounts = load_gom_accounts()
    try:
        list_control = None
        for attempt in range(3):
            try:
                print(f"Thử kết nối lần {attempt + 1}...")
                # backend = GF.get_backend()
                list_control = Application(backend="uia").connect(title_re='^Quan ly nhan vat.*').window(title_re='^Quan ly nhan vat.*').child_window(control_type="List")
                print("Kết nối thành công!")
                break  # Nếu kết nối thành công, thoát vòng lặp
            except Exception as e:
                print(f"Lỗi khi kết nối (lần {attempt + 1}): {e}")
                # backend = GF.get_backend()
                nameAutoVLBS = GF.getNameAutoVLBS()
                if not GF.checkBothAutoVlbsAndQuanLyRunning(nameAutoVLBS):
                    app = Application(backend="uia").connect(title_re=nameAutoVLBS)
                    dlg = app.window(title_re=nameAutoVLBS)

                    # Lấy tất cả control loại List trong cửa sổ
                    list_controls = dlg.descendants(control_type="List")

                    # Kiểm tra số lượng và lấy theo điều kiện
                    if len(list_controls) == 3:
                        print("Có 3 List control, lấy cái đầu tiên.")
                        list_control = list_controls[2]  # lấy cái đầu tiên
                    else:
                        list_control = dlg.child_window(control_type="List")  # mặc định nếu chỉ có 1   
                    if not list_control:
                        print("Không tìm thấy bảng!")
                    else:
                        try:
                            # Cách 1: Dùng phím Home
                            list_control.set_focus()
                            list_control.type_keys("{HOME}")
                            
                            # Hoặc cách 2: Dùng scroll pattern (nếu ứng dụng hỗ trợ)
                            # list_control.iface_scroll.SetScrollPercent(horizontalPercent=None, verticalPercent=0)
                            
                            time.sleep(0.5)  # Đợi scroll hoàn thành
                        except Exception as e:
                            print(f"Lỗi khi scroll: {str(e)}")
                        # Tìm các mục trong danh sách và nhấp chuột phải vào mục đầu tiên
                        # Tìm các mục trong danh sách và nhấp chuột phải vào mục đầu tiên
                        items = list_control.children(control_type="ListItem")
                        if items:
                            items[0].right_click_input()
                        else:
                            print("Không có mục nào trong danh sách!")
                    time.sleep(1)

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

# === VÒNG LẶP KIỂM TRA TỰ ĐỘNG ===
# Hàm này sẽ tự động kiểm tra tài khoản mỗi `minutes` phút
# và gửi báo cáo qua email hoặc Discord nếu có thay đổi
# ten_may: Tên máy để hiển thị trong báo cáo
def auto_check_loop(minutes, ten_may):
    global stop_flag, gom_accounts_info_data, previous_data, gom_accounts_list
    
    # Load danh sách tài khoản gom tiền với KPI riêng
    gom_accounts_list = load_gom_accounts()  # Dict: {ingame: kpi_gom}
    print(f"📋 Danh sách tài khoản GOM với KPI:")
    for ingame, kpi in gom_accounts_list.items():
        kpi_display = kpi if kpi else "default"
        print(f"   - {ingame}: {kpi_display} Kv/day")
    print(f"🔁 Sẽ bắt đầu kiểm tra vào giờ chẵn tiếp theo...")

    sleep_until_next_hour()  # Wait until the next even hour

    print(f"🔁 Bắt đầu kiểm tra tự động mỗi {minutes} phút...")

    known_accounts = set()  # lưu tài khoản đã từng xuất hiện
    missing_accounts = set()  # lưu tài khoản đã bị văng
    error_accounts = set()  # lưu tài khoản có lỗi
    is_first_run = True  # Biến để xác định lần chạy đầu tiên

    while not stop_flag:
        check_accounts_money()
        new_data = copy.deepcopy(gom_accounts_info_data)
        loop_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = []
        error_accounts_array = []
        lost_accounts_array = []
        low_blood_accounts_array = []
        # === Tạo set tài khoản hiện tại
        current_accounts = set(acc[0] for acc in new_data)
        total_profit = 0
        # === Kiểm tra từng tài khoản trong dữ liệu mới
        for acc in new_data:
            name = acc[0]
            money = float(acc[1])
            timestamp = acc[2]
            profit = 0  # Khởi tạo lợi nhuận mặc định
            
            if name in previous_data:
                old_money = previous_data[name]
                profit = money - old_money  # Tính lợi nhuận
                total_profit += profit  # Cộng dồn lợi nhuận tổng
                if money > old_money:
                    # Kiểm tra KPI theo loại tài khoản
                    if name in gom_accounts_list:
                        # Tài khoản gom tiền
                        kpi_custom = gom_accounts_list[name]
                        if kpi_custom:
                            # Có KPI riêng
                            kpi_check = (float(kpi_custom)/24)/60  # Chuyển từ Kv/day sang Kv/phút
                            account_type = f"GOM-{kpi_custom}"
                        else:
                            # Dùng KPI default
                            kpi_check = kpi_gom_1m
                            account_type = "GOM-default"
                    else:
                        # Tài khoản thường
                        kpi_check = kpi_1m
                        account_type = "THƯỜNG"
                    
                    kpi_required = kpi_check * minutes
                    
                    if profit >= kpi_required:
                        status = "Tăng"
                        print(f"[{timestamp}] ✅ {name} ({account_type}) tăng tiền: {old_money} → {money} (+{profit:.2f})")
                    else:
                        status = "Chưa đạt KPI"
                        print(f"[{timestamp}] ⚠️ {name} ({account_type}) tăng tiền: {old_money} → {money} (+{profit:.2f}) (Chưa đạt KPI: {kpi_required:.2f})")
                elif money < old_money:
                    status = "Giảm"
                    print(f"[{timestamp}] 🔻 {name} giảm tiền: {old_money} → {money}")
                else:
                    status = "Không đổi"
                    print(f"[{timestamp}] ⏸️ {name} không đổi: {money}")
                    error_accounts.add(name)
                    error_accounts_array.append({
                        "account": name,
                    })
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
                "status": status,
                "profit": profit
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
                    "status": "Văng game",
                    "profit": 0
                })
                missing_accounts.add(known_name)
                lost_accounts_array.append({
                    "account": known_name,
                })

        # === Gửi email
        # send_email_report(report, loop_time_str, ten_may)

        # Lưu snapshot vào file
        save_snapshot(ten_may, report)
        # Lưu dữ liệu vào MongoDB
        save_money_data_to_mongo(ten_may, total_profit)
        # Tóm tắt thu nhập trong 24 giờ qua
        summarize_last_24h_income(ten_may)
        # Xóa các snapshot cũ hơn 2 ngày
        clean_old_snapshots(ten_may, days_to_keep=2)

        # === Cập nhật trạng thái is_logged_in trong accounts.json
        update_accounts_online_status(current_accounts)
        
        # === Cập nhật thông tin máy chủ lên MongoDB
        update_mongodb_server_status()
        
        # === Gửi báo cáo Discord
        if is_first_run:
            print("🔔 Lần chạy đầu tiên, không gửi báo cáo Discord.")
            is_first_run = False
        else:
            send_discord_report(report, ten_may, loop_time_str)
            run_kill_hung_vo_lam()
            fixErrorAccounts(error_accounts_array)
            # Xử lý các tài khoản bị mất kết nối vì thấp máu
            low_blood_accounts_array = getLowBoodAccounts()
            # fixLowBloodAccounts()
            fix_account_stuck_on_map_Sa_Mac()
            relogin_lost_accounts()
        print(f"📊 Báo cáo kiểm tra tài khoản máy {ten_may} lúc {loop_time_str} đã hoàn thành.")
        # === Đếm ngược trước vòng lặp tiếp theo
        for i in range(minutes * 15):
            if stop_flag:
                print("🛑 Đã dừng kiểm tra.")
                return
            seconds_left = minutes * 60 - i
            print(f"Còn lại {format_time_to_minute_second(seconds_left)} trước khi kiểm tra lại...")
            # print(f"{minutes * 60 - i} giây còn lại trước khi kiểm tra lại...")
            time.sleep(1)
        # Xử lý các tài khoản lỗi sau 15 phut
        run_kill_hung_vo_lam()
        fixLowBloodAccountsWithRepair(prev_errors=low_blood_accounts_array)
        low_blood_accounts_array = []
        # fixLowBloodAccounts()
        fix_account_stuck_on_map_Sa_Mac()

        # === Đếm ngược trước vòng lặp tiếp theo
        for i in range(minutes * 15):
            if stop_flag:
                print("🛑 Đã dừng kiểm tra.")
                return
            seconds_left = minutes * 45 - i
            print(f"Còn lại {format_time_to_minute_second(seconds_left)} trước khi kiểm tra lại...")
            # print(f"{minutes * 45 - i} giây còn lại trước khi kiểm tra lại...")
            time.sleep(1)
        # Xử lý các tài khoản lỗi sau 15 phut
        run_kill_hung_vo_lam()
        low_blood_accounts_array = getLowBoodAccounts()
        # fixLowBloodAccounts()
        fix_account_stuck_on_map_Sa_Mac()
        relogin_lost_accounts()

        # === Đếm ngược trước vòng lặp tiếp theo
        for i in range(minutes * 15):
            if stop_flag:
                print("🛑 Đã dừng kiểm tra.")
                return
            seconds_left = minutes * 30 - i
            print(f"Còn lại {format_time_to_minute_second(seconds_left)} trước khi kiểm tra lại...")
            # print(f"{minutes * 30 - i} giây còn lại trước khi kiểm tra lại...")
            time.sleep(1)
        # Xử lý các tài khoản lỗi sau 15 phut
        run_kill_hung_vo_lam()
        fixLowBloodAccountsWithRepair(prev_errors=low_blood_accounts_array)
        low_blood_accounts_array = []
        # fixLowBloodAccounts()
        fix_account_stuck_on_map_Sa_Mac()

        # === Đếm ngược trước vòng lặp tiếp theo
        for i in range(minutes * 15):
            if stop_flag:
                print("🛑 Đã dừng kiểm tra.")
                return
            seconds_left = minutes * 15 - i
            print(f"Còn lại {format_time_to_minute_second(seconds_left)} trước khi kiểm tra lại...")
            # print(f"{minutes * 15 - i} giây còn lại trước khi kiểm tra lại...")
            time.sleep(1)

# === HÀM ĐIỀU KHIỂN LUỒNG ===
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

