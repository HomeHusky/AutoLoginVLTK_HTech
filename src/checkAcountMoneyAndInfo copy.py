from pywinauto import Application
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
import client

# Thông tin email
EMAIL_ADDRESS = "htechvlnotification@gmail.com"  # Địa chỉ email gửi đi
EMAIL_PASSWORD = "btpwkapwzdknnqfl"           # Mật khẩu email gửi đi
RECIPIENT_EMAIL = "vitrannhat8@gmail.com"  # Địa chỉ email nhận thông báo

global_time_sleep = GF.load_global_time_sleep()

json_file = 'accounts_money_status.json'
gom_account_file = 'gom_accounts.json'

def load_monitor_time_and_convert_to_second(filepath='monitor_time.json'):
    try:
        with open(os.path.join(GF.join_directory_data(), filepath), 'r') as f:
            data = json.load(f)
            return int(float(data['monitor_time']) * 60)
    except FileNotFoundError:
        # Nếu file không tồn tại, trả về giá trị mặc định
        print(f"File {filepath} không tồn tại. Sử dụng giá trị mặc định 60 giây.")
        return 60

def load_kpi_and_convert_to_hour(filepath='monitor_time.json'):
    try:
        with open(os.path.join(GF.join_directory_data(), filepath), 'r') as f:
            data = json.load(f)
            return float(data['kpi']) / 24
    except FileNotFoundError:
        # Nếu file không tồn tại, trả về giá trị mặc định
        print(f"File {filepath} không tồn tại. Sử dụng giá trị mặc định 1 giờ.")
        return 1.0

def load_total_servers(filepath='monitor_time.json'):
    try:
        with open(os.path.join(GF.join_directory_data(), filepath), 'r') as f:
            data = json.load(f)
            return float(data['total_servers'])
    except FileNotFoundError:
        # Nếu file không tồn tại, trả về giá trị mặc định
        print(f"File {filepath} không tồn tại. Sử dụng giá trị mặc định 10.")
        return 10.0

def load_title_mail(filepath='monitor_time.json'):
    try:
        with open(os.path.join(GF.join_directory_data(), filepath), 'r') as f:
            data = json.load(f)
            return float(data['title_mail'])
    except FileNotFoundError:
        # Nếu file không tồn tại, trả về giá trị mặc định
        print(f"File {filepath} không tồn tại. Sử dụng giá trị mặc định 1.")
        return 1.0

monitor_time_loop = load_monitor_time_and_convert_to_second()
kpi = load_kpi_and_convert_to_hour()
total_servers = load_total_servers()

def send_email(total_income, low_income_accounts, check_time, kpi_value, car_list, time_loop_send):

    title_mail = int(load_title_mail())

    # Tạo tiêu đề và nội dung email
    subject = f"MÁY {title_mail}: CHI TIẾT THU NHẬP TRONG {time_loop_send}!"
    
    # Tạo nội dung HTML với thời gian và KPI
    html_body = f"""
    <html>
    <body>
        <h2>Thông báo thu nhập máy {title_mail} trong {time_loop_send}:</h2>
        <p>Thời gian kiểm tra: {check_time}</p>
        <p>KPI xe 4: {kpi_value} (vạn)</p>
        <p>KPI xe 2: {kpi_value/2} (vạn)</p>
    """
    
    # Thêm mô tả trước bảng tổng thu nhập
    if car_list:
        html_body += f"""
        <p>Các tài khoản xe 2 hiện tại: {", ".join(car_list)}</p>
        """

    html_body += """
        <!-- Bảng 1: Tổng thu nhập -->
        <h3>Tổng thu nhập của tất cả tài khoản</h3>
        <table border="1" style="border-collapse: collapse;">
            <tr>
                <th>Tài khoản</th>
                <th>Thu nhập</th>
            </tr>
    """
    
    # Thêm dữ liệu bảng tổng thu nhập
    for account in total_income:
        html_body += f"""
            <tr>
                <td>{account[0]}</td>
                <td>{account[1]}</td>
            </tr>
        """
    
    html_body += """
        </table>
    """
    
    html_body += """
        <!-- Bảng 2: Thu nhập phát hiện thấp -->
        <h3>Thu nhập phát hiện thấp</h3>
        <table border="1" style="border-collapse: collapse;">
            <tr>
                <th>Tài khoản</th>
                <th>Thu nhập tăng</th>
            </tr>
    """
    
    # Thêm dữ liệu bảng thu nhập phát hiện thấp
    if low_income_accounts:
        for account in low_income_accounts:
            html_body += f"""
                <tr>
                    <td>{account[0]}</td>
                    <td>{account[1]}</td>
                </tr>
            """
    
    html_body += """
        </table>
    </body>
    </html>
    """

    # Tạo email và gắn nội dung
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = EMAIL_ADDRESS
    message["To"] = RECIPIENT_EMAIL
    part = MIMEText(html_body, "html")
    message.attach(part)

    # Tạo SSL context không xác thực
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    # Gửi email qua SMTP với SSL không xác thực
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, message.as_string())
        
def load_gom_accounts(filepath = 'accounts.json'):
    with open(os.path.join(GF.join_directory_data(), filepath), 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Bước 2: Lấy các tài khoản có is_logged_in = True và is_gom_tien = 1
    filtered_ingames = [account['ingame'] for account in data['accounts'] if account['is_logged_in'] and account['is_gom_tien'] == 1]

    # In kết quả
    return filtered_ingames

def load_xe_2_accounts(filepath = 'accounts.json'):
    with open(os.path.join(GF.join_directory_data(), filepath), 'r', encoding='utf-8') as file:
        data = json.load(file)

    filtered_ingames = [account['ingame'] for account in data['accounts'] if account['is_xe_2'] == 1 and account['is_logged_in'] == True and account['is_gom_tien'] == 1]

    return filtered_ingames

def run_right_click(name):
    backend = GF.get_backend()
    list_control = None
    app = Application(backend="uia").connect(title_re=name)
    dlg = app.window(title_re=name)

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
        # Tìm các mục trong danh sách và nhấp chuột phải vào mục đầu tiên
        items = list_control.children(control_type="ListItem")
        if items:
            items[0].right_click_input()
        else:
            print("Không có mục nào trong danh sách!")
    time.sleep(1)

def run_update_accounts_money(name, gom_accounts):
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
            elif countChild == 2:
                newdata.append(child.window_text())  # tong_tien
            elif countChild == 3:
                newdata.append(child.window_text())  # thu_nhap
            elif countChild == 4:
                newdata.append(child.window_text())  # thoi_gian
            elif countChild == 6:
                newdata.append(child.window_text())  # TDP/C
            elif countChild == 8:
                newdata.append(child.window_text())  # ban_do
            elif countChild == 9:
                newdata.append(child.window_text())  # server
            countChild += 1

        if nextItem: continue
        # Lấy thời gian hiện tại
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Thêm thông tin thời gian vào newdata
        newdata.append(current_time)
        
        add_status_accounts_data(newdata, array_name)
    
def updateAcountMoneyAndInfo(name, callback):

    data = None
    try:
        gom_accounts = load_gom_accounts()
        print("Gom accounts: ", gom_accounts)
        GF.checkBothAutoVlbsAndQuanLyRunning(name)

        if GF.checkQuanlynhanvat():
            pass
        elif GF.checkWindowRunning(name) == 1:
            run_right_click(name)
            time.sleep(global_time_sleep)
        elif GF.checkWindowRunning(name) == 2:
            GF.show_application(name)
            time.sleep(global_time_sleep)
        run_update_accounts_money(name, gom_accounts)
        
        # Đọc và cập nhật dữ liệu JSON
        with open(os.path.join(GF.join_directory_data(), json_file), 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("Update thành công!")
        callback()
        return data
    except Exception as e:
        run_right_click(name)
        updateAcountMoneyAndInfo(name, callback)
        callback()
        print("Lỗi dòng 228 file checkAccountMoneyAndInffo.py: " + str(e))
        return None

def update_account_thread(name):
    thread = threading.Thread(target=updateAcountMoneyAndInfo, args=(name, on_update_success,))
    thread.start()
    thread.join()  # Đảm bảo luồng cập nhật hoàn tất trước khi tiếp tục

def on_update_success():
    print("Update Success!")

def add_status_accounts_data(newdata, array_name):
    # Hàm thêm dữ liệu mới vào file JSON
    with open(os.path.join(GF.join_directory_data(), json_file), 'r+', encoding='utf-8') as f:
        data = json.load(f)

        # Thêm dữ liệu mới vào tài khoản tương ứng
        if array_name not in data:
            data[array_name] = []

        # Tạo một mục mới với dữ liệu cập nhật và thời gian
        account_data = {
            "tong_tien": newdata[0],
            "thu_nhap": newdata[1],
            "thoi_gian": newdata[2],
            "TDP/C": newdata[3],
            "ban_do": newdata[4],
            "server": newdata[5],
            "thoi_diem_cap_nhat": newdata[6]  # Thời gian cập nhật
        }

        # Thêm vào danh sách các bản ghi theo thời gian
        data[array_name].append(account_data)

        # Ghi lại vào file
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.truncate()

def readAcountMoneyAndInfo():
    gom_accounts = load_gom_accounts()

    GF.check_and_create_json_file(json_file)

    with open(os.path.join(GF.join_directory_data(), json_file), 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    latest_data = {}

    for account, records in data.items():
        if account not in gom_accounts:
            continue
        # Lọc những bản ghi có 'thoi_diem_cap_nhat'
        valid_records = [record for record in records if 'thoi_diem_cap_nhat' in record]

        if valid_records:
            # Sắp xếp các bản ghi theo 'thoi_diem_cap_nhat' giảm dần
            sorted_records = sorted(valid_records, key=lambda x: datetime.strptime(x['thoi_diem_cap_nhat'], "%Y-%m-%d %H:%M:%S"), reverse=True)
            # Lấy bản ghi mới nhất
            latest_data[account] = sorted_records[0]
        else:
            # Nếu không có bản ghi nào hợp lệ, bỏ qua tài khoản này hoặc xử lý khác
            latest_data[account] = None

    return latest_data

def check_income_increase(name, callback, stop_monitor_event, stop_monitor_success):
    accounts_xe_2 = load_xe_2_accounts()
    print("Xe 2: ", accounts_xe_2)
    monitor_time_loop = load_monitor_time_and_convert_to_second()
    kpi = None
    kpi = load_kpi_and_convert_to_hour()
    total_servers = load_total_servers()
    print("monitor_time_loop: ", monitor_time_loop)
    second = monitor_time_loop
    testkpi = load_kpi_and_convert_to_hour()
    testkpiForOneServer = testkpi / total_servers
    kpiXe4 = (testkpiForOneServer / 3600) * monitor_time_loop
    print("testkpi: ", testkpi)
    
    if second < 60:
        print(f"Kpi xe 4 trong {second} giây: ", kpiXe4)
    elif second < 3600:
        print(f"Kpi xe 4 trong {second / 60} phút: ", kpiXe4)
    else:
        print(f"Kpi xe 4 trong {second / 3600} giờ: ", kpiXe4)

    data = readAcountMoneyAndInfo()  # Tải dữ liệu ban đầu từ file JSON
    initial_income = {}
    stop_private = False

    # Lưu giá trị thu_nhap ban đầu cho từng tài khoản
    for key, item in data.items():
        if item:  # Kiểm tra nếu item hợp lệ
            initial_income[key] = float(item['thu_nhap'])

    while not stop_monitor_event.is_set():  # Vòng lặp vô hạn
        if stop_private:
            break
        for _ in range(monitor_time_loop):  # monitor_time_loop giây
            if stop_monitor_event.is_set():  # Nếu có yêu cầu dừng, thoát khỏi vòng lặp
                print("Đã dừng!")
                stop_private = True
                stop_monitor_success()
                return
            time.sleep(1)  # Ngủ trong 1 giây

        total_income = []  # Danh sách lưu tổng thu nhập
        low_income_accounts = []  # Danh sách tài khoản có thu nhập dưới 70% KPI
        time_loop_send = None

        # Tải lại dữ liệu và kiểm tra sự tăng trưởng của thu_nhap
        update_account_thread(name)
        data_updated = readAcountMoneyAndInfo()  # Tải dữ liệu mới
        for key, item in data_updated.items():
            kpiCheck = kpiXe4
            if key in accounts_xe_2:
                kpiCheck = kpiCheck / 2

            if item:  # Kiểm tra nếu item hợp lệ
                current_income = float(item['thu_nhap'])
                try:
                    income_difference = current_income - initial_income[key]
                    total_income.append((key, income_difference))
                    print(key, f": {income_difference}")
                except Exception as e:
                    print("Dữ liệu đầu: ", initial_income)
                    continue

                # Kiểm tra nếu thu nhập dưới 70% KPI
                print(f"kpiCheck cho xe {key}: {kpiCheck}")
                if income_difference < (kpiCheck * 0.7):
                    if monitor_time_loop < 60:
                        time_loop_send = f"{monitor_time_loop} giây"
                    elif monitor_time_loop < 3600:
                        time_loop_send = f"{monitor_time_loop / 60} phút"
                    else:
                        time_loop_send = f"{monitor_time_loop / 3600} giờ"

                    low_income_accounts.append((key, f"{income_difference:.5f}"))

        # Gửi email nếu có tài khoản có thu nhập thấp
        if low_income_accounts:
            # send_email(total_income, low_income_accounts, check_time=time.strftime("%Y-%m-%d %H:%M:%S"), kpi_value=kpiXe4, car_list=accounts_xe_2, time_loop_send=time_loop_send)
            client.send_data(total_income, low_income_accounts, check_time=time.strftime("%Y-%m-%d %H:%M:%S"), kpi_value=kpiXe4, car_list=accounts_xe_2, time_loop_send=time_loop_send)
            callback()
            print("Đã gửi mail thông báo!")
            time.sleep(2)
        else:
            # send_email(total_income, None, check_time=time.strftime("%Y-%m-%d %H:%M:%S"), kpi_value=kpiXe4, car_list=accounts_xe_2, time_loop_send=time_loop_send)
            client.send_data(total_income, None, check_time=time.strftime("%Y-%m-%d %H:%M:%S"), kpi_value=kpiXe4, car_list=accounts_xe_2, time_loop_send=time_loop_send)
            callback()
            print("Đã gửi mail thông báo!")
            time.sleep(2)

        # Cập nhật lại giá trị thu_nhap ban đầu cho lần kiểm tra tiếp theo
        initial_income = {key: float(item['thu_nhap']) for key, item in data_updated.items() if item}

    stop_monitor_success()

# Ví dụ sử dụng
# check_income_increase()
