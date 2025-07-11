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
from fixErrorAccounts import fixErrorAccounts, relogin_lost_accounts
from tkinter import ttk

# === BIẾN TOÀN CỤC ===
kpi_1m = (35/24)/60
stop_flag = False
gom_accounts_info_data = []
gom_account_file = 'gom_accounts.json'
previous_data = {}  # Dùng để lưu trữ số dư tiền của các tài khoản trước khi kiểm tra

EMAIL_ADDRESS = "htechvlnotification@gmail.com"
EMAIL_PASSWORD = "btpwkapwzdknnqfl"
RECIPIENT_EMAIL = "vitrannhat@gmail.com"

# === CÁC HÀM TOÀN CỤC ===
# Hàm này sẽ tải danh sách tài khoản từ file gom_accounts.json
# và lọc ra các tài khoản đang đăng nhập và có is_gom_tien = 1
# Trả về danh sách các tài khoản ingame
def load_gom_accounts(filepath = 'accounts.json'):
    with open(os.path.join(GF.join_directory_data(), filepath), 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Bước 2: Lấy các tài khoản có is_logged_in = True và is_gom_tien = 1
    filtered_ingames = [account['ingame'] for account in data['accounts'] if account['is_logged_in'] and account['is_gom_tien'] == 1]

    # In kết quả
    return filtered_ingames

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

    columns = ("account", "start", "end", "profit", "start_time", "end_time")
    tree = ttk.Treeview(frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col.upper())
        tree.column(col, width=120)

    for row in table:
        tree.insert("", "end", values=(
            row["account"],
            f"{row['start']:.2f}",
            f"{row['end']:.2f}",
            f"{row['profit']:+.2f}",
            row["start_time"],
            row["end_time"]
        ))

    tree.pack(expand=True, fill="both")

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
                    list_control = Application(backend="uia").connect(title_re=nameAutoVLBS).window(title_re=nameAutoVLBS).child_window(control_type="List")
                    if not list_control.exists():
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
    global stop_flag, gom_accounts_info_data, previous_data
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
                    profit = money - old_money
                    if profit >= kpi_1m*minutes:
                        status = "Tăng"
                        print(f"[{timestamp}] ✅ {name} tăng tiền: {old_money} → {money}")
                    else:
                        status = "Chưa đạt KPI"
                        print(f"[{timestamp}] ⚠️ {name} tăng tiền: {old_money} → {money} (Chưa đạt KPI)")
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
                lost_accounts_array.append({
                    "account": known_name,
                })

        # === Gửi email
        # send_email_report(report, loop_time_str, ten_may)

        # Lưu snapshot vào file
        save_snapshot(ten_may, report)
        # Tóm tắt thu nhập trong 24 giờ qua
        summarize_last_24h_income(ten_may)
        # Xóa các snapshot cũ hơn 2 ngày
        clean_old_snapshots(ten_may, days_to_keep=2)

        # === Gửi báo cáo Discord
        if is_first_run:
            print("🔔 Lần chạy đầu tiên, không gửi báo cáo Discord.")
            is_first_run = False
        else:
            send_discord_report(report, ten_may, loop_time_str)
            fixErrorAccounts(error_accounts_array)
        # relogin_lost_accounts(lost_accounts_array)
        print(f"📊 Báo cáo kiểm tra tài khoản máy {ten_may} lúc {loop_time_str} đã hoàn thành.")
        # === Đếm ngược trước vòng lặp tiếp theo
        for i in range(minutes * 60):
            if stop_flag:
                print("🛑 Đã dừng kiểm tra.")
                return
            print(f"{minutes * 60 - i} giây còn lại trước khi kiểm tra lại...")
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

