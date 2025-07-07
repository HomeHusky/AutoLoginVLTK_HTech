import json
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import startLogin as START_LOGIN
import GlobalFunction as GF
import checkAcountMoneyAndInfo
import checkStatusAcounts
import autoClickVLBS
import threading
import pyautogui
import time
import os
import datetime
import requests
import zipfile
import sys
import shutil
import client

pyautogui.FAILSAFE = False

def get_current_version():
    version_file = "version.txt"
    try:
        with open(version_file, "r") as file:
            current_version = file.read().strip()
            return current_version
    except FileNotFoundError:
        print(f"File {version_file} không tồn tại.")
        return None

def check_for_update():
    # URL của file version trên GitHub
    url = "https://raw.githubusercontent.com/HomeHusky/AutoLoginVLTK_HTech/master/version.txt"
    
    # Đọc phiên bản hiện tại từ file version.txt
    current_version = get_current_version()
    
    if current_version is None:
        print("Không thể kiểm tra phiên bản hiện tại.")
        return False
    
    try:
        # Lấy phiên bản mới nhất từ GitHub
        response = requests.get(url)
        if response.status_code == 200:
            latest_version = response.text.strip()
            if latest_version != current_version:
                confirm = messagebox.askyesno("Thông báo", "Có bản cập nhật mới, bạn có muốn cập nhật?")
                if confirm:
                    print(f"Chuẩn bị cập nhật mới: {latest_version}")
                    return True
                else:
                    return 2
            else:
                print("Bạn đang sử dụng phiên bản mới nhất.")
        else:
            print("Không thể kết nối đến GitHub.")
    except Exception as e:
        print(f"Lỗi khi kiểm tra cập nhật: {e}")
    
    return False

def download_and_update():
    url = "https://github.com/HomeHusky/AutoLoginVLTK_HTech/archive/refs/heads/master.zip"
    zip_path = "update.zip"
    
    try:
        # Tải file zip từ GitHub
        response = requests.get(url)
        with open(zip_path, "wb") as file:
            file.write(response.content)
        
        # Giải nén file zip vào thư mục tạm thời
        temp_dir = "temp_update"
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        # Di chuyển các file từ thư mục tạm về thư mục hiện tại
        extracted_dir = os.path.join(temp_dir, os.listdir(temp_dir)[0])  # Lấy thư mục con đầu tiên
        for item in os.listdir(extracted_dir):
            s = os.path.join(extracted_dir, item)
            d = os.path.join(".", item)
            if os.path.isdir(s):
                if os.path.exists(d):
                    shutil.rmtree(d)  # Xóa thư mục cũ nếu cần
                shutil.move(s, d)
            else:
                shutil.move(s, d)
        
        # Xóa file zip và thư mục tạm
        os.remove(zip_path)
        shutil.rmtree(temp_dir)

        print("Cập nhật thành công!")
    except Exception as e:
        print(f"Lỗi khi cập nhật: {e}")

def restart_app():
    # Khởi động lại ứng dụng
    python = sys.executable
    os.execl(python, python, *sys.argv)

def update_app():
    try:
        # Chạy lệnh git pull để cập nhật phiên bản mới nhất từ GitHub
        result = check_for_update()
        
        # Hiển thị thông báo kết quả của git pull
        if not result:
            messagebox.showinfo("Update", "Bạn đang sử dụng phiên bản mới nhất.")
        elif result == 2:
            pass
        else:
            download_and_update()
            messagebox.showinfo("Update", "Ứng dụng đã được cập nhật thành công. Bắt đầu khởi động lại.")
            restart_app()
    except Exception as e:
        messagebox.showerror("Update Failed", f"Quá trình cập nhật thất bại: {e}")

def alway_update_app():
    try:
        download_and_update()
        messagebox.showinfo("Update", "Ứng dụng đã được cập nhật thành công. Bắt đầu khởi động lại.")
        restart_app()
    except Exception as e:
        messagebox.showerror("Update Failed", f"Quá trình cập nhật thất bại: {e}")

global_time_sleep = GF.load_global_time_sleep()

# Biến toàn cục để quản lý luồng login
login_thread = None

monitor_thread = None
is_running_monitor = False
stop_monitor_event = threading.Event()  # Biến event để dừng luồng

auto_update_thread = None
is_running_AutoUpdate = False
stop_AutoUpdate_event = False

editting_account = None
currentAutoName = None
auto_tool_path = None
sleepTime = None
try:
    currentAutoName = GF.getNameAutoVLBS()
except Exception as e:
    print("Error", str(e))

# Đường dẫn file JSON
accounts_file_path = 'accounts.json'
accounts_money_status = 'accounts_money_status.json'
servers_path = 'servers.json'
servers_data = GF.read_config_file(servers_path)
servers = servers_data['servers']
folder_game = servers_data['folder_game']
pass_accounts = []

def run_check_status(tryTest):
    auto_tool_path = START_LOGIN.load_auto_tool_path()
    sleepTime = START_LOGIN.load_sleepTime()
    global currentAutoName
    currentAutoName = GF.getNameAutoVLBS()
    if not checkStatusAcounts.checkStatusAcounts(auto_tool_path, currentAutoName, sleepTime):
        currentAutoName = GF.getNameAutoVLBS()
        if not GF.checkAutoVlbsBackGroundRunning():
            if tryTest > 0:
                run_check_status(tryTest-1)
                return
            else:
                messagebox.showerror("Error", f"Có lỗi xảy ra dòng 32 autoLogin!")
                return

# Tải và lưu dữ liệu JSON
def load_data():
    try:
        return GF.read_json_file(accounts_file_path)
    except FileNotFoundError:
        # Nếu file không tồn tại, tạo cấu trúc dữ liệu mặc định
        return {"accounts": [], 
        "autoNames": [ "vocongtruyenky", "congthanhchienxua", "AutoVLBS"],
        "auto_tool_path": "D:/VoLamTruyenKy/AutoVLBS19/TrainJX.exe"}

def load_global_time():
    try:
        return GF.read_config_file('global_time.json')
    except FileNotFoundError:
        # Nếu file không tồn tại, tạo cấu trúc dữ liệu mặc định
        return {
        "sleepTime": [
            {
                "wait_time_open": 15,
                "wait_time_open2": 45,
                "wait_time_load": 2,
                "wait_time_server": 8,
                "wait_time_open_trainjx": 3,
                "wait_time_load_autovlbs": 5,
                "try_number": 3,
                "global_time_sleep": 1
            }
        ]}

def save_data(data):
    with open(os.path.join(GF.join_directory_data(), accounts_file_path), 'w') as file:
        json.dump(data, file, ensure_ascii=True, indent=4)

def save_global_time_data(data):
    with open(os.path.join(GF.join_directory_config(), 'global_time.json'), 'w') as file:
        json.dump(data, file, ensure_ascii=True, indent=4)

def LoginSuccess():
    messagebox.showinfo("Thông báo", "Hoàn thành tự động đăng nhập.")

# Hiển thị dữ liệu từ file JSON lên giao diện
def load_to_gui():
    global data
    data = load_data()  # Tải dữ liệu từ file JSON

    # Xóa dữ liệu hiện tại trong Treeview
    for i in tree_accounts.get_children():
        tree_accounts.delete(i)

    # Hiển thị danh sách tài khoản
    stt = 1
    for account in data['accounts']:
        is_logged_in_display = "Online" if account.get('is_logged_in', False) else ""
        is_gom_tien_display = "✓" if account['is_gom_tien'] else ""
        is_xe_2_display = "✓" if account['is_xe_2'] else ""
        try:
            so_lan_xuong_display = account['so_lan_xuong']
        except Exception as e:
            so_lan_xuong_display = ""
        try:
            so_lan_xuong2_display = account['so_lan_xuong2']
        except Exception as e:
            so_lan_xuong2_display = ""
        
        is_select_display = "✓" if account.get('is_select', False) else ""
        tree_accounts.insert("", "end", values=(
            stt,
            is_select_display, 
            account['username'], 
            account['ingame'], 
            account['game_path'], 
            is_logged_in_display,  # Hiển thị Online nếu is_logged_in là True
            is_gom_tien_display, 
            is_xe_2_display,
            so_lan_xuong_display,
            so_lan_xuong2_display
        ))
        stt += 1

    def on_item_select(event):
        selected_item = tree_accounts.selection()[0]
        values = tree_accounts.item(selected_item, 'values')
        stt = int(values[0]) - 1  # Lấy chỉ số hàng (STT)
        
        # Lấy thông tin account liên quan
        account = data['accounts'][stt]
        
        # Thay đổi trạng thái của 'is_select'
        account['is_select'] = not account['is_select']
        
        # Cập nhật hiển thị trong Treeview
        is_select_display = "✓" if account['is_select'] else ""
        if account['is_select']:
            pass_accounts.append(account['username'])
        else:
            pass_accounts.remove(account['username'])
        print(pass_accounts)
        tree_accounts.item(selected_item, values=(
            values[0],  # STT
            is_select_display,  # Cập nhật trạng thái
            values[2],  # Username
            values[3],  # Ingame
            values[4],  # Game Path
            values[5],  # Online
            values[6],  # Gom Tiền
            values[7]   # Xe 2
        ))

    # Ràng buộc sự kiện nhấp chuột
    tree_accounts.bind("<Double-1>", on_item_select)
    
    def on_heading_click(event):
        try:
            # Lấy cột được nhấn (ở đây kiểm tra với cột đầu tiên)
            region = tree_accounts.identify_region(event.x, event.y)
            column = tree_accounts.identify_column(event.x)
            heading_name = tree_accounts.heading(column)["text"]
            
            if region == "heading" and column == "#2":  # "#2" là cột thứ hai trong treeview (tính từ 1)
                for item_id in tree_accounts.get_children():
                    values = tree_accounts.item(item_id, 'values')
                    stt = int(values[0]) - 1  # Lấy chỉ số hàng (STT)
                    
                    # Lấy thông tin account liên quan
                    account = data['accounts'][stt]
                    
                    # Thay đổi trạng thái của 'is_select' cho tất cả các hàng
                    account['is_select'] = not account['is_select']
                    
                    # Cập nhật hiển thị trong Treeview
                    is_select_display = "✓" if account['is_select'] else ""
                    if account['is_select']:
                        pass_accounts.append(account['username'])
                    else:
                        pass_accounts.remove(account['username'])

                    tree_accounts.item(item_id, values=(
                        values[0],  # STT
                        is_select_display,  # Cập nhật trạng thái
                        values[2],  # Username
                        values[3],  # Ingame
                        values[4],  # Game Path
                        values[5],  # Online
                        values[6],  # Gom Tiền
                        values[7]   # Xe 2
                    ))
                print(pass_accounts)

            elif region == "heading" and column == "#5":
                if heading_name == 'Servers':
                    tree_accounts.heading(column, text='PathGame')
                    update_server_to_pathgame()
                else:
                    tree_accounts.heading(column, text='Servers')
                    update_pathgame_to_server()
        except Exception as e:
            print("Lỗi double click: ", str(e))

    # Ràng buộc sự kiện nhấp chuột vào heading
    tree_accounts.bind("<Button-1>", on_heading_click)

# Kiểm tra tài khoản tồn tại
def check_exist_account(username, gamepath, data):
    is_exist = False
    for account in data['accounts']:
        if account.get('username') == username and account.get('game_path') == gamepath:
            is_exist = True
    return is_exist

# Thêm tài khoản mới
def add_account():
    username = entry_username.get().strip()
    password = entry_password.get().strip()
    ingame = entry_ingame.get().strip()
    game_path = entry_game_path.get().strip()
    auto_update_path = game_path.replace("game.exe", "AutoUpdate.exe")
    solanxuong = entry_solanxuong.get().strip()
    solanxuong2 = entry_solanxuong2.get().strip()

    if not username or not password or not game_path:
        messagebox.showwarning("Warning", "Vui lòng nhập đủ thông tin!")
        return

    data = load_data()

    if check_exist_account(username, game_path, data):
        messagebox.showwarning("Warning", "Tài khoản đã có trong dữ liệu!")
        return

    new_account = {
        'is_select': False,
        'username': username,
        'password': password,
        'ingame': ingame,
        'game_path': game_path,
        'auto_update_path': auto_update_path,
        'is_logged_in': False,
        'is_gom_tien': check_checkbox(varGomCheckBox),
        'is_xe_2': check_checkbox(varXe2CheckBox),
        'so_lan_xuong': solanxuong if solanxuong else 1,
        'so_lan_xuong2': solanxuong2 if solanxuong2 else 0,
        'mo_game_lau': check_checkbox(varMoGameLau)
    }

    data['accounts'].append(new_account)
    save_data(data)
    load_to_gui()

    entry_username.delete(0, tk.END)
    # entry_password.delete(0, tk.END)
    # entry_game_path.delete(0, tk.END)
    # entry_auto_update_path.delete(0, tk.END)
    entry_ingame.delete(0, tk.END)

    update_button.grid_forget()
    cancel_button.grid_forget()
    edit_button.grid(row=0, column=1, padx=5, pady=10)

# Hiển thị thông tin tài khoản đã chọn lên vùng trên cùng để chỉnh sửa
def edit_account():
    global editting_account
    selected_item = tree_accounts.selection()

    if selected_item:
        values = tree_accounts.item(selected_item)['values']
        entry_username.delete(0, tk.END)
        entry_username.insert(0, values[2])
        # Không hiển thị mật khẩu gốc, cần nhập lại mật khẩu mới
        entry_password.delete(0, tk.END)
        entry_game_path.delete(0, tk.END)
        entry_auto_update_path.delete(0, tk.END)
        entry_solanxuong.delete(0, tk.END)
        entry_solanxuong2.delete(0, tk.END)
        entry_ingame.delete(0, tk.END)
        # Tìm dữ liệu gốc để lấy mật khẩu
        data = load_data()
        index = tree_accounts.index(selected_item[0])
        original_password = data['accounts'][index]['password']
        entry_password.insert(0, original_password)
        original_ingame = data['accounts'][index]['ingame']
        entry_ingame.insert(0, original_ingame)
        entry_game_path.insert(0, values[4])
        entry_auto_update_path.insert(0, values[4].replace("game.exe", "AutoUpdate.exe"))
        if data['accounts'][index]['is_gom_tien'] == 1:
            gom_checkbox.select()  # Tự động tick
        else:
            gom_checkbox.deselect()
        if data['accounts'][index]['is_xe_2'] == 1:
            xe_2_checkbox.select()  # Tự động tick
        else:
            xe_2_checkbox.deselect()
        
        try:
            if data['accounts'][index]['mo_game_lau'] == 1:
                mo_game_lau_checkbox.select()  # Tự động tick
            else:
                mo_game_lau_checkbox.deselect()
        except Exception as e:
                mo_game_lau_checkbox.deselect()

        entry_solanxuong.insert(0, values[8])
        entry_solanxuong2.insert(0, values[8])
        
        
        # Lưu tài khoản đang chỉnh sửa
        editting_account = values[2]

        # Ẩn nút Edit và hiện nút Update cùng nút Cancel
        edit_button.grid_forget()
        update_button.grid(row=0, column=1, padx=5, pady=10)
        cancel_button.grid(row=0, column=2, padx=5, pady=10)

# Cập nhật tài khoản đã chỉnh sửa
def update_account():
    global editting_account
    selected_item = tree_accounts.selection()
    
    if selected_item:

        if tree_accounts.item(selected_item)['values'][2] != editting_account:
            messagebox.showwarning("Warning", "Vui lòng chọn tài khoản đang chỉnh sửa!")
            return
        index = tree_accounts.index(selected_item[0])

        data = load_data()
        data['accounts'][index] = {
            'is_select': data['accounts'][index].get('is_select', False),
            'username': entry_username.get(),
            'password': entry_password.get(),
            'ingame': data['accounts'][index]['ingame'],
            'game_path': entry_game_path.get(),
            'auto_update_path': entry_game_path.get().replace("game.exe", "AutoUpdate.exe"),
            'is_logged_in': data['accounts'][index].get('is_logged_in', False),
            'is_gom_tien': check_checkbox(varGomCheckBox),
            'is_xe_2': check_checkbox(varXe2CheckBox),
            'so_lan_xuong': entry_solanxuong.get(),
            'so_lan_xuong2': entry_solanxuong2.get(),
            'mo_game_lau': check_checkbox(varMoGameLau)
        }

        save_data(data)
        load_to_gui()

        entry_username.delete(0, tk.END)
        entry_password.delete(0, tk.END)
        entry_ingame.delete(0, tk.END)
        entry_game_path.delete(0, tk.END)
        entry_auto_update_path.delete(0, tk.END)
        entry_solanxuong.delete(0, tk.END)
        entry_solanxuong2.delete(0, tk.END)

        update_button.grid_forget()
        cancel_button.grid_forget()
        edit_button.grid(row=0, column=1, padx=5, pady=10)

# Xoá tài khoản đã chọn
def delete_account():
    selected_item = tree_accounts.selection()
    if selected_item:
        # Lấy chỉ số của tài khoản đã chọn
        index = tree_accounts.index(selected_item)
        # Xác nhận xóa tài khoản
        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xoá tài khoản này?")
        if confirm:
            del data['accounts'][index]  # Xóa tài khoản khỏi danh sách
            save_data(data)               # Lưu lại dữ liệu vào file JSON
            load_to_gui()                 # Tải lại dữ liệu để hiển thị
            # messagebox.showinfo("Success", "Đã xoá tài khoản!")
    else:
        messagebox.showwarning("Warning", "Vui lòng chọn tài khoản để xóa!")

# Chọn file đường dẫn game
def browse_game_path():
    file_path = filedialog.askopenfilename(
        title="Chọn đường dẫn Game",
        initialfile="game.exe",  # Đặt tên mặc định là "game.exe"
        filetypes=(("Executable Files", "*.exe"), ("All Files", "*.*"))
    )
    if file_path:
        entry_game_path.delete(0, tk.END)
        entry_game_path.insert(0, file_path)
        entry_auto_update_path.delete(0, tk.END)
        entry_auto_update_path.insert(0, file_path.replace("game.exe", "AutoUpdate.exe"))

# Chọn file đường dẫn auto
def browse_auto_path():
    file_path = filedialog.askopenfilename(
        title="Chọn đường dẫn AutoVLBS 1.9",
        filetypes=(("Executable Files", "*.exe"), ("All Files", "*.*"))
    )
    if file_path:
        entry_auto_path.delete(0, tk.END)
        entry_auto_path.insert(0, file_path)
        new_auto_tool_path = entry_auto_path.get().strip()
    
        # Kiểm tra nếu đường dẫn không rỗng
        if not new_auto_tool_path:
            messagebox.showwarning("Warning", "Vui lòng nhập đường dẫn tool auto!")
            return

        # Cập nhật đường dẫn vào dữ liệu
        # data['auto_tool_path'] = new_auto_tool_path  # Cập nhật đường dẫn tool auto vào dữ liệu

        # # Lưu lại vào file JSON ngay khi chọn xong browse
        # save_data(data)
        # messagebox.showinfo("Success", "Cập nhật đường dẫn tool auto thành công!")

def load_auto_data():
    data = load_data()
    global_time_data = load_global_time()
    entry_auto_path.delete(0, tk.END)
    entry_auto_path.insert(0, data.get('auto_tool_path', ''))
    ttk.Label(auto_frame, text="Tên auto:").grid(row=1, column=0, padx=5, pady=5)

    for i, auto in enumerate(data.get('autoNames', [])):
        entry_game_name = ttk.Entry(auto_frame, width=40)
        entry_game_name.grid(row=i+1, column=1, padx=5, pady=5)
        entry_game_name.insert(0, auto)
    
    # Hiển thị thời gian sleepTime
    sleep_times = global_time_data.get('sleepTime', [])
    if sleep_times:
        entry_wait_game_open.delete(0, tk.END)
        entry_wait_game_open2.delete(0, tk.END)
        entry_wait_character_open.delete(0, tk.END)
        entry_wait_server_open.delete(0, tk.END)
        entry_wait_time_trainjx_open.delete(0, tk.END)
        entry_wait_time_autovlbs_open.delete(0, tk.END)
        entry_try_number.delete(0, tk.END)
        entry_global_time_sleep.delete(0, tk.END)

        entry_wait_game_open.insert(0, sleep_times[0]['wait_time_open'])
        entry_wait_game_open2.insert(0, sleep_times[0]['wait_time_open2'])
        entry_wait_character_open.insert(0, sleep_times[0]['wait_time_load'])
        entry_wait_server_open.insert(0, sleep_times[0]['wait_time_server'])
        entry_wait_time_trainjx_open.insert(0, sleep_times[0]['wait_time_open_trainjx'])
        entry_wait_time_autovlbs_open.insert(0, sleep_times[0]['wait_time_load_autovlbs'])
        entry_try_number.insert(0, sleep_times[0]['try_number'])
        entry_global_time_sleep.insert(0, sleep_times[0]['global_time_sleep'])

def reload_auto_data_to_global_variable():
    auto_tool_path = START_LOGIN.load_auto_tool_path()
    sleepTime = START_LOGIN.load_sleepTime()

def save_auto_data():
    data = load_data()
    global_time_data = load_global_time()
    # Lưu đường dẫn tool auto
    data['auto_tool_path'] = entry_auto_path.get().strip()

    # Lưu tên game auto
    autoNames = []
    for i in range(len(data['autoNames'])):
        entry_game_name = auto_frame.grid_slaves(row=i+1, column=1)[0]  # Lấy giá trị từ các entry
        autoNames.append(entry_game_name.get())
    data['autoNames'] = autoNames

    # Lưu thời gian auto
    wait_time_open = entry_wait_game_open.get().strip()
    wait_time_open2 = entry_wait_game_open2.get().strip()    
    wait_time_load = entry_wait_character_open.get().strip()
    wait_time_server = entry_wait_server_open.get().strip()
    wait_time_open_trainjx = entry_wait_time_trainjx_open.get().strip()
    wait_time_load_autovlbs = entry_wait_time_autovlbs_open.get().strip()
    try_number = entry_try_number.get().strip()
    edit_global_time_sleep = entry_global_time_sleep.get().strip()

    global_time_data['sleepTime'] = [{
        'wait_time_open': int(wait_time_open) if wait_time_open.isdigit() else 12,
        'wait_time_open2': int(wait_time_open2) if wait_time_open2.isdigit() else 45,
        'wait_time_load': int(wait_time_load) if wait_time_load.isdigit() else 2,
        'wait_time_server': int(wait_time_server) if wait_time_server.isdigit() else 8,
        'wait_time_open_trainjx': int(wait_time_open_trainjx) if wait_time_open_trainjx.isdigit() else 2,
        'wait_time_load_autovlbs': int(wait_time_load_autovlbs) if wait_time_load_autovlbs.isdigit() else 3,
        'try_number': int(try_number) if try_number.isdigit() else 3,
        'global_time_sleep': int(edit_global_time_sleep) if edit_global_time_sleep.isdigit() else 2,
    }]

    # Lưu dữ liệu vào file JSON
    save_data(data)
    save_global_time_data(global_time_data)
    reload_auto_data_to_global_variable()
    messagebox.showinfo("Success", "Đã lưu thành công dữ liệu Auto Tool!")

# Hủy bỏ chỉnh sửa
def cancel_edit():
    entry_username.delete(0, tk.END)
    entry_password.delete(0, tk.END)
    entry_game_path.delete(0, tk.END)
    entry_auto_update_path.delete(0, tk.END)
    entry_solanxuong.delete(0, tk.END)
    entry_solanxuong2.delete(0, tk.END)
    entry_ingame.delete(0, tk.END)

    update_button.grid_forget()
    cancel_button.grid_forget()
    edit_button.grid(row=0, column=1, padx=5, pady=10)

def update_selected_accounts():
    for item_id in tree_accounts.get_children():
        values = tree_accounts.item(item_id, 'values')
        
        # Lấy username và trạng thái is_select từ cột 1 và cột 2
        username = values[2]  # Cột username (giả định là cột 2)
        is_select_display = values[1]  # Cột is_select (giả định là cột 1)
        
        # Tìm account trong file JSON dựa trên username
        for account in data['accounts']:
            if account['username'] == username:
                # Cập nhật giá trị is_select
                account['is_select'] = True if is_select_display == "✓" else False
                break

    with open(os.path.join(GF.join_directory_data(), 'accounts.json'), 'w') as f:
        json.dump(data, f, indent=4)

def update_pathgame_to_server():
    for child in tree_accounts.get_children():
        item = tree_accounts.item(child)
        game_path = item["values"][4]  # Cột game_path
        server_name = "Lỗi"
        for server, path in servers.items():
            if game_path == path:
                server_name = server
                break
        # Cập nhật cột trạng thái (Tên server hoặc lỗi)
        tree_accounts.set(child, "game_path", server_name)

def update_server_to_pathgame():
    for child in tree_accounts.get_children():
        item = tree_accounts.item(child)
        name = item["values"][4]  # Cột name
        path_name = "Lỗi"
        for server, path in servers.items():
            if name == server:
                path_name = path
                break
        # Cập nhật cột trạng thái (Tên server hoặc lỗi)
        tree_accounts.set(child, "game_path", path_name)

def update_status_to_logged_in(username):
    # Duyệt qua tất cả các mục trong Treeview
    for item in tree_accounts.get_children():
        # Lấy giá trị của tài khoản
        account_username = tree_accounts.item(item, "values")[2]
        
        # Nếu tên tài khoản trùng với username, cập nhật trạng thái
        if account_username == username:
            tree_accounts.set(item, "is_logged_in", "Login(1)")
            break

def start_login(isAutoClickVLBS):
    global login_thread



    # Tạo popup yêu cầu xác nhận
    confirm = messagebox.askyesno(
        "Thông báo",
        "Vui lòng chuyển sang tiếng Anh và tắt CAPS LOCK trước khi bắt đầu. Bạn đã thực hiện chưa?"
    )
    
    if confirm:  # Nếu người dùng xác nhận
        try:
            run_check_status(1)
            # Tạo luồng cho quá trình login
            login_thread = threading.Thread(target=START_LOGIN.runStartLogin, args=(isAutoClickVLBS, on_login_complete, currentAutoName, pass_accounts, on_login_username))
            login_thread.start()  # Bắt đầu luồng login
        except Exception as e:
            messagebox.showerror("Error", f"Không thể bắt đầu quá trình đăng nhập: {e}")
    else:
        # Nếu người dùng không xác nhận, chỉ cần quay lại
        messagebox.showinfo("Thông báo", "Vui lòng thực hiện yêu cầu trước khi tiếp tục.")

# Hàm callback

def on_login_complete():
    # GF.activate_window("Auto Login Htech")
    pass_accounts.clear()
    print(pass_accounts)
    run_check_status(1)
    load_to_gui()
    # check_delete_fail_servers()
    messagebox.showinfo("Error", f"Đăng nhập thành công")

def on_login_username(username):
    update_status_to_logged_in(username)
    
def thread_auto_update(auto_update_data, fix_web_ctcx_data, callback):
    global stop_AutoUpdate_event
    for path in fix_web_ctcx_data['fix_web_ctcx_paths']:
        if stop_AutoUpdate_event:
            messagebox.showinfo("Thông báo", "Dừng AutoUpdate thành công!")
            return
        try:
            print(path)
            # Mở từng file .exe
            # pyautogui.hotkey('win', 'r')
            # time.sleep(global_time_sleep)
            # pyautogui.write(path)
            # time.sleep(global_time_sleep)
            # pyautogui.press('enter')
            # time.sleep(2)  # Chờ 2 giây để đảm bảo file được mở
            
            working_dir = os.path.dirname(path)
            try:
                subprocess.Popen(path, cwd=working_dir)
            except Exception as e:
                print("Lỗi khi mở fix_web:", e)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở file {path}: {str(e)}")
    
    for path in auto_update_data['auto_update_paths']:
        if stop_AutoUpdate_event:
            messagebox.showinfo("Thông báo", "Dừng AutoUpdate thành công!")
            return
        try:
            print(path)
            # Mở từng file .exe
            # pyautogui.hotkey('win', 'r')
            # time.sleep(global_time_sleep)
            # pyautogui.write(path)
            # time.sleep(global_time_sleep)
            # pyautogui.press('enter')
            # time.sleep(2)  # Chờ 2 giây để đảm bảo file được mở
            
            working_dir = os.path.dirname(path)
            try:
                subprocess.Popen(path, cwd=working_dir)
            except Exception as e:
                print("Lỗi khi mở AutoUpdate:", e)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở file {path}: {str(e)}")
    callback()

def on_auto_update_success():
    is_running_AutoUpdate = False
    stop_AutoUpdate_event = True  # Kích hoạt trạng thái dừng
    run_auto_update_button.config(text="AutoUpdate")  # Đổi nhãn nút thành "Bắt đầu"
    messagebox.showinfo("Thông báo", "Chạy AutoUpdate thành công!")

def run_all_auto_update():
    global stop_AutoUpdate_event, is_running_AutoUpdate, auto_update_thread
    if not is_running_AutoUpdate:
        confirm = messagebox.askyesno(
            "Thông báo",
            "Thao tác này sẽ chạy tất cả AutoUpdate của các server mà dữ liệu đang có!"
        )
        if confirm:  # Nếu người dùng xác nhận
            stop_AutoUpdate_event = False
            is_running_AutoUpdate = True
            run_auto_update_button.config(text="Dừng")
            GF.copy_auto_update_path_to_auto_update_path()
            GF.copy_auto_update_path_to_fix_web_ctcx_path()
            GF.replace_AutoUpdate_to_fix_web_ctcx()

            fix_web_ctcx_file = 'fix_web_ctcx.json'
            auto_update_file = 'autoUpdate_path.json'
            # Đọc dữ liệu từ file accounts.json
            fix_web_ctcx_data = GF.read_json_file(fix_web_ctcx_file)
            auto_update_data = GF.read_json_file(auto_update_file)

            print("Đã chạy AutoUpdate của các server!")
            auto_update_thread = threading.Thread(target=thread_auto_update, args=(auto_update_data, fix_web_ctcx_data, on_auto_update_success))
            auto_update_thread.daemon = True
            auto_update_thread.start()  # Bắt đầu luồng login
            
        else:
            return
    else:
        is_running_AutoUpdate = False
        stop_AutoUpdate_event = True  # Kích hoạt trạng thái dừng
        run_auto_update_button.config(text="AutoUpdate")  # Đổi nhãn nút thành "Bắt đầu"

def check_delete_fail_servers():
    # Đường dẫn tới file accounts.json và fail_server.json
    accounts_file = 'accounts.json'
    fail_server_file = 'fail_servers.json'

    # Đọc dữ liệu từ file accounts.json
    data = GF.read_json_file(accounts_file)

    # Kiểm tra nếu tất cả các tài khoản đều đã đăng nhập
    all_logged_in = all(account['is_logged_in'] for account in data['accounts'])

    # Nếu tất cả tài khoản đã đăng nhập, xóa dữ liệu trong fail_server.json
    if all_logged_in:
        with open(os.path.join(GF.join_directory_data(), fail_server_file), 'w', encoding='utf-8') as f:
            f.write('')  # Ghi file trống để xóa dữ liệu
        print("Dữ liệu trong fail_server.json đã được xóa.")
    else:
        # Nếu không phải tất cả tài khoản đã đăng nhập, mở các đường dẫn trong fail_server.json
        fail_data = GF.read_json_file(fail_server_file)

        for path in fail_data['server_fail']:
            # Mở từng file .exe
            pyautogui.hotkey('win', 'r')
            time.sleep(global_time_sleep)
            pyautogui.write(path)
            time.sleep(global_time_sleep)
            pyautogui.press('enter')
            time.sleep(2)  # Chờ 2 giây để đảm bảo file được mở
        print("Đã chạy AutoUpdate của các server lỗi!")

def stop_login():
    try:
        START_LOGIN.stop()
        if login_thread and login_thread.is_alive():
            login_thread.join()
        messagebox.showinfo("Stopped", "Dừng đăng nhập thành công.")
    except Exception as e:
        messagebox.showerror("Error", f"Không thể dừng quá trình đăng nhập: {e}")

def test_accounts():
    # try:
    run_check_status(1)
    messagebox.showinfo("Success", "Kiểm tra thành công.")
    load_to_gui()
    # except Exception as e:
    #     messagebox.showerror("Error", f"Có lỗi xảy ra dòng 309 autoLogin!")

# Tạo cửa sổ giao diện chính
root = tk.Tk()
version = get_current_version()

root.title(f"Auto Login Htechnology - {version}")
root.geometry("850x700+0+0")
root.resizable(True, True)

server_names = list(servers.keys())
print(server_names)

selected_server = tk.StringVar(value="Chọn server")
print(selected_server)

def create_server_buttons():
    # Duyệt qua từng server trong JSON
    for server_name, path in servers.items():

        server_frame = ttk.LabelFrame(open_game_tab, text=server_name, padding=(10, 5))
        server_frame.pack(padx=5, pady=10, fill="x")

        # Hiển thị tên server
        server_label = tk.Label(server_frame, text=server_name, font=("Arial", 10, "bold"))
        server_label.pack()

        # Hiển thị số tài khoản đã đăng nhập (chưa có nghiệp vụ, sẽ để mặc định là 0)
        account_label = tk.Label(server_frame, text="Số tài khoản đã đăng nhập: 0", font=("Arial", 9))
        account_label.pack()

        # Tạo nút "Chạy Auto Update"
        auto_update_button = tk.Button(server_frame, text="Chạy Auto Update", width=20, command=lambda s=server_name: print(f"Chạy Auto Update cho {s}"))
        auto_update_button.pack(pady=5)

        # Tạo nút "Chạy Game"
        game_button = tk.Button(server_frame, text="Chạy Game", width=20, command=lambda s=server_name: print(f"Chạy Game cho {s}"))
        game_button.pack(pady=5)

# Tạo biến để lưu trạng thái của checkbox clickAuto
varCheckBox = tk.IntVar()
varGomCheckBox = tk.IntVar()
varXe2CheckBox = tk.IntVar()
varMoGameLau = tk.IntVar()

def check_checkbox(var):
    # So sánh giá trị của var (IntVar) với 1 và trả về 0 hoặc 1
    print(var.get())
    return var.get()

# Styling với ttk
style = ttk.Style()
style.theme_use('clam')  # Sử dụng theme 'clam' để giao diện đẹp hơn

style.configure("TButton",
                padding=6,
                relief="flat",
                background="#5783db",
                foreground="white")

style.map("TButton",
          background=[('active', '#4681f4')])

style.configure("TLabel",
                padding=6,
                font=('Arial', 10))

style.configure("Treeview.Heading",
                font=('Arial', 10, 'bold'))

style.configure("Treeview", rowheight=25)

# Tạo tab control
tab_control = ttk.Notebook(root)

# Tab Quản lý Tài khoản
account_tab = ttk.Frame(tab_control)
tab_control.add(account_tab, text="Quản lý Tài khoản")

# Tab Quản lý Đường dẫn
open_game_tab = ttk.Frame(tab_control)
tab_control.add(open_game_tab, text="Mở Autologin và game")

# Tab Quản lý Đường dẫn
path_tab = ttk.Frame(tab_control)
tab_control.add(path_tab, text="Quản lý Đường dẫn")

path_tab.bind("<Visibility>", lambda e: load_auto_data())  # Tải dữ liệu khi tab được hiển thị

status_account_tab = ttk.Frame(tab_control)
tab_control.add(status_account_tab, text="Trạng thái Tài khoản")

# Hàm kiểm tra tab được chọn
def on_tab_selected(event):
    # Kiểm tra tab hiện tại
    selected_tab = tab_control.index(tab_control.select())
    if selected_tab == tab_control.index(status_account_tab):
        load_initial_deposit_account()  # Gọi hàm khi chọn tab "Trạng thái Tài khoản"
        save_gom_account()
        load_to_tab_money_manager()
    elif selected_tab == tab_control.index(account_tab):
        load_to_gui()

tab_control.pack(expand=1, fill="both")
tab_control.bind("<<NotebookTabChanged>>", on_tab_selected)

# ================================ Tab Quản lý Tài khoản ======================================

# Frame thông tin nhập
input_frame = ttk.LabelFrame(account_tab, text="Thông tin tài khoản", padding=(10, 5))
input_frame.pack(padx=5, pady=10, fill="x")

# Nhập Username
ttk.Label(input_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5)
entry_username = ttk.Entry(input_frame)
entry_username.grid(row=0, column=1, columnspan=1, padx=5, pady=5, sticky="ew")

# Nhập Password
ttk.Label(input_frame, text="Password:").grid(row=0, column=2, padx=5, pady=5)
entry_password = ttk.Entry(input_frame)
entry_password.grid(row=0, column=3, columnspan=1, padx=5, pady=5, sticky="ew")

# Nhập Server
ttk.Label(input_frame, text="Server:").grid(row=1, column=0, padx=5, pady=5)
# Tạo Combobox servers
servers_dropdown = ttk.Combobox(input_frame, textvariable=selected_server, values=server_names, state="readonly")
servers_dropdown.grid(row=1, column=1, columnspan=3, padx=10, pady=10, sticky="ew")

mo_game_lau_checkbox = tk.Checkbutton(input_frame, text="Server mở game lâu", variable=varMoGameLau, command=lambda: check_checkbox(varMoGameLau))
mo_game_lau_checkbox.grid(row=1, column=4, columnspan=1)

# Nút chọn đường dẫn game
hide_game_button = ttk.Button(input_frame, text="Ẩn All game", command=lambda: GF.hideWindow("Vo Lam Truyen Ky"))
hide_game_button.grid(row=1, column=5, padx=5, pady=5)

# Nhập Game Path
ttk.Label(input_frame, text="Đường dẫn Game:").grid(row=2, column=0, padx=5, pady=5)
entry_game_path = ttk.Entry(input_frame)
entry_game_path.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")



# Hàm cập nhật path
def update_path():

    def save_servers_data(data):
        with open(os.path.join(GF.join_directory_config(), servers_path), 'w') as file:
            json.dump(data, file, ensure_ascii=True, indent=4)
            print(f"Dữ liệu đã được ghi vào tệp {servers_path}.")

    server = selected_server.get()
    new_path = entry_game_path.get()

    if server and new_path:
        # Cập nhật path trong dữ liệu
        servers[server] = new_path
        servers_data["servers"] = servers

        # Ghi lại vào file JSON
        save_servers_data(servers_data)
        print(f"Path của server '{server}' đã được cập nhật thành:\n{new_path}")
    else:
        print("Vui lòng chọn server và nhập đường dẫn mới.")

# Hàm xử lý khi chọn server
def on_server_select(event):
    server = selected_server.get()
    path = servers[server]
    entry_game_path.insert(0, path)
    entry_auto_update_path.delete(0, tk.END)
    entry_auto_update_path.insert(0, path.replace("game.exe", "AutoUpdate.exe"))
    print(f"Server đã chọn: {server}")
    print(f"Đường dẫn: {path}")

# Gắn sự kiện
servers_dropdown.bind("<<ComboboxSelected>>", on_server_select)

# Nhập AutoUpdate Path
ttk.Label(input_frame, text="Đường dẫn AutoUpdate:").grid(row=3, column=0, padx=5, pady=5)
entry_auto_update_path = ttk.Entry(input_frame)
entry_auto_update_path.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

# Nút chọn đường dẫn game
browse_button = ttk.Button(input_frame, text="Browse", command=browse_game_path)
browse_button.grid(row=2, column=4, padx=5, pady=5)

update_button = ttk.Button(input_frame, text="Update path", command=update_path)
update_button.grid(row=2, column=5, padx=5, pady=5)

gom_checkbox = tk.Checkbutton(input_frame, text="TK gom", variable=varGomCheckBox, command=lambda: check_checkbox(varGomCheckBox))
gom_checkbox.grid(row=3, column=3, columnspan=1, padx=5, pady=5, sticky="ew")

xe_2_checkbox = tk.Checkbutton(input_frame, text="Xe 2", variable=varXe2CheckBox, command=lambda: check_checkbox(varXe2CheckBox))
xe_2_checkbox.grid(row=3, column=4,columnspan=1, padx=5, pady=5, sticky="ew")

small_frame = ttk.Frame(input_frame, width=10)
small_frame.grid(row=3, column=5, columnspan=1, padx=0, pady=0)

entry_solanxuong = ttk.Entry(small_frame, width=4)
entry_solanxuong.pack(side="left", padx=(0, 2))

entry_solanxuong2 = ttk.Entry(small_frame, width=4)
entry_solanxuong2.pack(side="right", padx=(2, 0))

# entry_solanxuong = ttk.Entry(input_frame, width=3)
# entry_solanxuong.grid(row=3, column=5, padx=5, pady=5)

# entry_solanxuong2 = ttk.Entry(input_frame, width=3)
# entry_solanxuong2.grid(row=3, column=6, padx=5, pady=5)

# Nút tải dữ liệu
# load_button = ttk.Button(input_frame, text="Refresh", command=load_to_gui)
# load_button.grid(row=0, column=4, padx=10, pady=5)

# Nhập Ingame
ttk.Label(input_frame, text="Ingame:").grid(row=0, column=4, padx=0, pady=5)
entry_ingame = ttk.Entry(input_frame, width=10)
entry_ingame.grid(row=0, column=5, columnspan=1, padx=0, pady=5, sticky="ew")

# Frame chứa các nút chức năng
button_frame = ttk.Frame(input_frame)
button_frame.grid(row=4, column=0, columnspan=3, pady=10)

start_frame = ttk.LabelFrame(input_frame)
start_frame.grid(row=4, column=3, columnspan=3, pady=10)

add_button = ttk.Button(button_frame, text="Thêm", command=add_account)
add_button.grid(row=0, column=0, padx=5, pady=10)

edit_button = ttk.Button(button_frame, text="Sửa", command=edit_account)
edit_button.grid(row=0, column=1, padx=5, pady=10)

update_button = ttk.Button(button_frame, text="Cập nhật", command=update_account)
cancel_button = ttk.Button(button_frame, text="Hủy", command=lambda: (update_button.grid_forget(), cancel_button.grid_forget(), edit_button.grid(row=0, column=1, padx=5, pady=10)))

delete_button = ttk.Button(button_frame, text="Xoá", command=delete_account)
delete_button.grid(row=0, column=2, padx=5, pady=10)

cancel_button = ttk.Button(button_frame, text="Hủy", command=cancel_edit)
cancel_button.grid(row=0, column=3, padx=5, pady=10)
cancel_button.grid_remove()

# Tạo nút update
update_app_button = ttk.Button(button_frame, text="Check For Update Auto Login", command=update_app)
update_app_button.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

alway_update_app_button = ttk.Button(button_frame, text="Alway Update", command=alway_update_app)
alway_update_app_button.grid(row=1, column=2, columnspan=1, padx=5, pady=10, sticky="ew")

# Tạo checkbox
checkbox = tk.Checkbutton(start_frame, text="Tự động click AutoVLBS", variable=varCheckBox, command=lambda: check_checkbox(varCheckBox))
checkbox.grid(row=2, columnspan=2, column=1, padx=5, pady=10, sticky="ew")

start_check_fix_VLBS_button = ttk.Button(start_frame, text="Tự động fix lỗi VLBS")
start_check_fix_VLBS_button.grid(row=2, column=3, padx=5, pady=10)

start_login_button = ttk.Button(start_frame, text="Bắt đầu", command=lambda: start_login(check_checkbox(varCheckBox)))
start_login_button.grid(row=3, column=1, padx=5, pady=10)

stop_login_button = ttk.Button(start_frame, text="Dừng", command=stop_login)
stop_login_button.grid(row=3, column=2, padx=5, pady=10)

test_button = ttk.Button(start_frame, text="Test", command=test_accounts)
test_button.grid(row=3, column=3, padx=5, pady=10)

run_auto_update_button = ttk.Button(start_frame, text="AutoUpdate", command=run_all_auto_update)
run_auto_update_button.grid(row=3, column=4, padx=5, pady=10)

def on_check(item):
    checked = tree_accounts.item(item, 'values')[-1]  # Lấy trạng thái checkbox
    tree_accounts.item(item, values=(*tree_accounts.item(item, 'values')[:-1], not bool(checked)))  # Cập nhật lại trạng thái

# Treeview hiển thị danh sách tài khoản
tree_frame = ttk.LabelFrame(account_tab, text="Danh sách tài khoản", padding=(10, 5))
tree_frame.pack(padx=5, pady=10, fill="x")

columns = ("stt", "is_select", "username", "ingame", "game_path", "is_logged_in", "is_gom_tien", "is_xe_2", "so_lan_xuong", "so_lan_xuong2")
tree_accounts = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
tree_accounts.heading("stt", text="Stt")  # Cột stt
tree_accounts.heading("is_select", text="Bỏ qua")  # Cột checkbox
tree_accounts.heading("username", text="Username")
tree_accounts.heading("ingame", text="Ingame")
tree_accounts.heading("game_path", text="PathGame")
tree_accounts.heading("is_logged_in", text="Trạng thái")
tree_accounts.heading("is_gom_tien", text="Tk gom tiền")
tree_accounts.heading("is_xe_2", text="Xe 2")
tree_accounts.heading("so_lan_xuong", text="Số lần xuống cum server")
tree_accounts.heading("so_lan_xuong2", text="Số lần xuống server")

tree_accounts.column("stt", width=30)
tree_accounts.column("is_select", width=50)
tree_accounts.column("username", width=100)
tree_accounts.column("ingame", width=100)
tree_accounts.column("game_path", width=200)
tree_accounts.column("is_logged_in", width=60)
tree_accounts.column("is_gom_tien", width=40)
tree_accounts.column("is_xe_2", width=40)
tree_accounts.column("so_lan_xuong", width=40)
tree_accounts.column("so_lan_xuong2", width=40)


# Tạo thanh cuộn dọc (vertical scrollbar)
v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree_accounts.yview)
v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree_accounts.configure(yscrollcommand=v_scrollbar.set)

# Tạo thanh cuộn ngang (horizontal scrollbar)
h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree_accounts.xview)
h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
tree_accounts.configure(xscrollcommand=h_scrollbar.set)

tree_accounts.pack(fill="both", expand=True)

# ================================ Tab Quản lý Đường dẫn ======================================

# Frame thông tin đường dẫn
auto_frame = ttk.LabelFrame(path_tab, text="Cài đặt Tự động", padding=(10, 5))
auto_frame.pack(padx=5, pady=10, fill="x")

# Nhập đường dẫn tool auto
ttk.Label(auto_frame, text="Đường dẫn Tool auto:").grid(row=0, column=0, padx=5, pady=5)
entry_auto_path = ttk.Entry(auto_frame)
entry_auto_path.grid(row=0, column=1, columnspan=4, padx=5, pady=5, sticky="ew")

# Nút chọn đường dẫn auto
browse_auto_button = ttk.Button(auto_frame, text="Browse", command=browse_auto_path)
browse_auto_button.grid(row=0, column=5, padx=5, pady=5)

ttk.Label(auto_frame, text="Thời gian load game (s):").grid(row=4, column=0, padx=5, pady=5)
entry_wait_game_open = ttk.Entry(auto_frame)
entry_wait_game_open.grid(row=4, column=1, columnspan=1, padx=5, pady=5, sticky="ew")

ttk.Label(auto_frame, text="Thời gian load game nếu game mở lâu (s):").grid(row=5, column=0, padx=5, pady=5)
entry_wait_game_open2 = ttk.Entry(auto_frame)
entry_wait_game_open2.grid(row=5, column=1, columnspan=1, padx=5, pady=5, sticky="ew")

ttk.Label(auto_frame, text="Thời gian load nhân vật (s):").grid(row=6, column=0, padx=5, pady=5)
entry_wait_character_open = ttk.Entry(auto_frame)
entry_wait_character_open.grid(row=6, column=1, columnspan=1, padx=5, pady=5, sticky="ew")

ttk.Label(auto_frame, text="Thời gian load server (s):").grid(row=7, column=0, padx=5, pady=5)
entry_wait_server_open = ttk.Entry(auto_frame)
entry_wait_server_open.grid(row=7, column=1, columnspan=1, padx=5, pady=5, sticky="ew")

ttk.Label(auto_frame, text="Thời gian load TrainJX (s):").grid(row=8, column=0, padx=5, pady=5)
entry_wait_time_trainjx_open = ttk.Entry(auto_frame)
entry_wait_time_trainjx_open.grid(row=8, column=1, columnspan=1, padx=5, pady=5, sticky="ew")

ttk.Label(auto_frame, text="Thời gian load AutoVLBS (s):").grid(row=9, column=0, padx=5, pady=5)
entry_wait_time_autovlbs_open = ttk.Entry(auto_frame)
entry_wait_time_autovlbs_open.grid(row=9, column=1, columnspan=1, padx=5, pady=5, sticky="ew")

ttk.Label(auto_frame, text="Số lần thử lại:").grid(row=10, column=0, padx=5, pady=5)
entry_try_number = ttk.Entry(auto_frame)
entry_try_number.grid(row=10, column=1, columnspan=1, padx=5, pady=5, sticky="ew")

ttk.Label(auto_frame, text="Chờ cục bộ (0.5 hoặc 1 nếu máy nhanh):").grid(row=11, column=0, padx=5, pady=5)
entry_global_time_sleep = ttk.Entry(auto_frame)
entry_global_time_sleep.grid(row=11, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
     
# Lưu dữ liệu đường dẫn auto
save_button = ttk.Button(auto_frame, text="Lưu Cài đặt", command=save_auto_data)
save_button.grid(row=12, column=5, padx=5, pady=5)

# Cấu hình lưới để mở rộng đúng cách
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)

# ================================ Tab Quản lý Trạng thái kiếm Tiền ======================================

def run_load_to_tab_money_manager():
    load_to_tab_money_manager()
    messagebox.showinfo("Success", "Làm mới thành công.")

def load_to_tab_money_manager():
    data = checkAcountMoneyAndInfo.readAcountMoneyAndInfo()  # Tải dữ liệu từ file JSON
    if not data:
        return False
    
    # Xóa dữ liệu hiện tại trong Treeview
    for i in tree_money_accounts.get_children():
        tree_money_accounts.delete(i)

    # Thêm dữ liệu vào Treeview
    stt = 1
    for key, item in data.items():  # `item` bây giờ là một từ điển chứa thông tin tài khoản
        if item:  # Kiểm tra xem `item` có hợp lệ không
            tree_money_accounts.insert("", "end", values=(
                stt,  # Số thứ tự (STT)
                key,  # Tên nhân vật (key)
                item['tong_tien'],  # Trực tiếp truy cập vào các trường
                item['thu_nhap'],
                item['thoi_gian'],
                item['TDP/C'],
                item['ban_do'],
                item['server']
            ))
            stt += 1  # Tăng STT

def update_to_tab_money_manager():
    save_monitor_time()
    checkAcountMoneyAndInfo.updateAcountMoneyAndInfo(currentAutoName, on_update_success)
    load_to_tab_money_manager()
    
def on_update_success():
    print("Cập nhật thành công.")

def monitor_money_manager():
    global monitor_thread, is_running_monitor, stop_monitor_event
    if not is_running_monitor:
        confirm = messagebox.askyesno(
            "Thông báo",
            "Thao tác này sẽ chạy theo dõi tài khoản của các server mà dữ liệu đang có!"
        )
        if confirm:  # Nếu người dùng xác nhận
            save_monitor_time()
            is_running_monitor = True
            checkAcountMoneyAndInfo.updateAcountMoneyAndInfo(currentAutoName, on_update_success)
            update_status_square(status_canvas, "theo dõi")
            stop_monitor_event.clear()
            monitor_money_button.config(text="Dừng")

            now = datetime.datetime.now()
            print(f"Đã chạy theo dõi tài khoản vào {now}!")
            monitor_thread = threading.Thread(target=checkAcountMoneyAndInfo.check_income_increase, args=(currentAutoName, call_from_monitor_thread, stop_monitor_event, stop_monitor_success))
            monitor_thread.daemon = True
            monitor_thread.start()  # Bắt đầu luồng login
        else:
            return
    else:
        is_running_monitor = False
        stop_monitor_event.set()  # Kích hoạt trạng thái dừng
        monitor_money_button.config(text="Theo dõi")  # Đổi nhãn nút thành "Bắt đầu"

def send_data():
    client.send_data()
    now = datetime.datetime.now()
    print(f"Đã gửi dữ liệu lúc {now}!")

def stop_monitor_success():
    messagebox.showinfo("Success", "Dừng theo dõi thành công.")
    update_status_square(status_canvas, "không theo dõi")

def call_from_monitor_thread():
    status_account_tab.after(0, load_to_tab_money_manager)

def update_status_square(canvas, status):
    # Xóa nội dung cũ của canvas (nếu có)
    canvas.delete("all")
    
    # Vẽ hình tròn với màu tương ứng với trạng thái
    color = "green" if status == "theo dõi" else "red"
    
    # Vẽ hình tròn (điểm giữa 20, 20 với bán kính 15)
    canvas.create_rectangle(5, 5, 35, 35, fill=color)

def move_to_selected():
    selected_accounts = listbox_left.curselection()  # Lấy tài khoản được chọn
    for i in selected_accounts[::-1]:
        account = listbox_left.get(i)
        listbox_left.delete(i)
        listbox_right.insert(tk.END, account)

# Hàm chuyển tài khoản từ bên phải sang trái
def move_to_all():
    selected_accounts = listbox_right.curselection()  # Lấy tài khoản được chọn
    for i in selected_accounts[::-1]:
        account = listbox_right.get(i)
        listbox_right.delete(i)
        listbox_left.insert(tk.END, account)

def save_gom_account():
    selected_accounts = listbox_right.get(0, tk.END)  # Lấy tất cả tài khoản bên phải
    selected_accounts = list(selected_accounts)  # Chuyển đổi thành danh sách
    gom_account_file = 'gom_accounts.json'
    # Bước 1: Đọc dữ liệu từ file accounts.json
    data = GF.read_json_file(accounts_file_path)

    # Bước 2: Cập nhật trường is_gom_tien cho từng tài khoản
    for account in data['accounts']:
        # Nếu tài khoản có trong danh sách selected_accounts (bên phải), is_gom_tien = 1, ngược lại = 0
        if account['ingame'] in selected_accounts:
            account['is_gom_tien'] = 1  # Tài khoản được chọn
        else:
            account['is_gom_tien'] = 0  # Tài khoản không được chọn

    # Bước 3: Ghi lại toàn bộ dữ liệu vào file accounts.json
    with open(os.path.join(GF.join_directory_data(), accounts_file_path), 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    
    with open(os.path.join(GF.join_directory_data(), gom_account_file), 'w', encoding='utf-8') as file:
        json.dump(selected_accounts, file, ensure_ascii=False, indent=4)

    print(f"Đã cập nhật trường 'is_gom_tien' cho các tài khoản trong {accounts_file_path}")


status_frame = tk.Frame(status_account_tab)
status_frame.pack(side="right", padx=10, pady=10)

status_canvas = tk.Canvas(status_frame, width=40, height=40)
status_canvas.pack()

# Treeview thông tin tiền vạn
tree_money_frame = ttk.LabelFrame(status_account_tab, text="Tiền vạn theo thời gian", padding=(10, 5))
tree_money_frame.pack(padx=5, pady=10, fill="x")

button_money_frame = ttk.Frame(status_account_tab, padding=(10, 5))
button_money_frame.pack(padx=5, pady=10, fill="x")

money_columns = ("stt", "ingame", "tong_tien", "thu_nhap", "thoi_gian", "TDP/C", "ban_do", "server")
tree_money_accounts = ttk.Treeview(tree_money_frame, columns=money_columns, show="headings", height=10)
tree_money_accounts.heading("stt", text="Stt")  # Cột stt
tree_money_accounts.heading("ingame", text="Tên nv")
tree_money_accounts.heading("tong_tien", text="Tổng tiền")
tree_money_accounts.heading("thu_nhap", text="Thu nhập")
tree_money_accounts.heading("thoi_gian", text="Thời gian")
tree_money_accounts.heading("TDP/C", text="TDP/C")
tree_money_accounts.heading("ban_do", text="Bản đồ")
tree_money_accounts.heading("server", text="Server")

tree_money_accounts.column("stt", width=50)
tree_money_accounts.column("ingame", width=100)
tree_money_accounts.column("tong_tien", width=100)
tree_money_accounts.column("thu_nhap", width=80)
tree_money_accounts.column("thoi_gian", width=80)
tree_money_accounts.column("TDP/C", width=80)
tree_money_accounts.column("ban_do", width=80)
tree_money_accounts.column("server", width=80)
tree_money_accounts.pack(fill="both", expand=True)

# Tạo frame trái để hiển thị tất cả tài khoản
frame_left = ttk.LabelFrame(status_account_tab, text="Tài khoản", padding=(10, 5))
frame_left.pack(side="left", expand=True, fill="both", padx=10, pady=10)

# Tạo frame phải để hiển thị các tài khoản đã chọn
frame_right = ttk.LabelFrame(status_account_tab, text="Tài khoản gom vạn", padding=(10, 5))
frame_right.pack(side="right", expand=True, fill="both", padx=10, pady=10)

# Tạo frame giữa chứa nút chuyển đổi
frame_middle = ttk.Frame(status_account_tab)
frame_middle.pack(side="left", padx=10)

# Tạo listbox hiển thị tất cả tài khoản
listbox_left = tk.Listbox(frame_left, selectmode=tk.MULTIPLE, width=30, height=15)
listbox_left.pack(expand=True, fill="both")

# Tạo listbox hiển thị các tài khoản đã chọn
listbox_right = tk.Listbox(frame_right, selectmode=tk.MULTIPLE, width=30, height=15)
listbox_right.pack(expand=True, fill="both")

def get_accounts_with_gom_tien():
    data = GF.read_json_file(accounts_file_path)
    un_gom_tien_accounts = []
    gom_tien_accounts = []
    for account in data['accounts']:
        if account["ingame"] == "":
            continue
        if account["is_gom_tien"] == 1:
            gom_tien_accounts.append(account["ingame"])
        else:
            un_gom_tien_accounts.append(account["ingame"])
    return un_gom_tien_accounts, gom_tien_accounts

# Thêm một số tài khoản mẫu vào listbox bên trái
def load_initial_deposit_account():
    listbox_left.delete(0, tk.END)
    listbox_right.delete(0, tk.END)
    all_accounts, gomtien_accounts = get_accounts_with_gom_tien()
    for account in all_accounts:
        listbox_left.insert(tk.END, account)
    for account in gomtien_accounts:
        listbox_right.insert(tk.END, account)

# Tạo nút chuyển từ phải sang trái
btn_to_left = ttk.Button(frame_middle, text="<", command=move_to_all)
btn_to_left.pack(pady=5)

# Tạo nút chuyển từ trái sang phải
btn_to_right = ttk.Button(frame_middle, text=">", command=move_to_selected)
btn_to_right.pack(pady=5)

btn_save_gom_accounts = ttk.Button(frame_middle, text="Lưu", command=save_gom_account)
btn_save_gom_accounts.pack(pady=5)

# # Nút tải dữ liệu
# load_money_button = ttk.Button(button_money_frame, text="Refresh", command=run_load_to_tab_money_manager)
# load_money_button.grid(row=1, column=2, padx=10, pady=5)

# Nút tải dữ liệu
update_money_button = ttk.Button(button_money_frame, text="Cập nhật mới nhất", command=update_to_tab_money_manager)
update_money_button.grid(row=1, column=3, padx=10, pady=5)

monitor_money_button = ttk.Button(button_money_frame, text="Theo dõi", command=monitor_money_manager)
monitor_money_button.grid(row=1, column=4, padx=10, pady=5)

send_data_button = ttk.Button(button_money_frame, text="Send data", command=send_data)
send_data_button.grid(row=1, column=5, padx=10, pady=5)

def load_monitor_time(filepath='monitor_time.json'):
    try:
        with open(os.path.join(GF.join_directory_data(), filepath), 'r') as f:
            data = json.load(f)
            return data['monitor_time']
    except FileNotFoundError:
        # Nếu file không tồn tại, trả về giá trị mặc định
        return "5"

def load_kpi(filepath='monitor_time.json'):
    try:
        with open(os.path.join(GF.join_directory_data(), filepath), 'r') as f:
            data = json.load(f)
            return data['kpi']
    except FileNotFoundError:
        # Nếu file không tồn tại, trả về giá trị mặc định
        return "1000"
    
def load_total_servers(filepath='monitor_time.json'):
    try:
        with open(os.path.join(GF.join_directory_data(), filepath), 'r') as f:
            data = json.load(f)
            return data['total_servers']
    except FileNotFoundError:
        # Nếu file không tồn tại, trả về giá trị mặc định
        return "10"

def load_title_mail(filepath='monitor_time.json'):
    try:
        with open(os.path.join(GF.join_directory_data(), filepath), 'r') as f:
            data = json.load(f)
            return data['title_mail']
    except FileNotFoundError:
        # Nếu file không tồn tại, trả về giá trị mặc định
        return "Máy chủ AutoVLBS"

def save_monitor_time(filepath='monitor_time.json'):
    data = {}
    data['monitor_time'] = entry_monitor_time.get().strip()
    data['kpi'] = entry_kpi.get().strip()
    data['total_servers'] = entry_total_servers.get().strip()
    data['title_mail'] = entry_title_mail.get().strip()
    with open(os.path.join(GF.join_directory_data(), filepath), 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

ttk.Label(button_money_frame, text="Thời gian(phút):").grid(row=0, column=0, padx=5, pady=5)
entry_monitor_time = ttk.Entry(button_money_frame)
entry_monitor_time.grid(row=0, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
entry_monitor_time.insert(0, load_monitor_time())

ttk.Label(button_money_frame, text="Tên/Số máy gửi Mail:").grid(row=1, column=0, padx=5, pady=5)
entry_title_mail = ttk.Entry(button_money_frame)
entry_title_mail.grid(row=1, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
entry_title_mail.insert(0, load_title_mail())

ttk.Label(button_money_frame, text="Chỉ tiêu (Kv/day):").grid(row=0, column=2, padx=5, pady=5)
entry_kpi = ttk.Entry(button_money_frame)
entry_kpi.grid(row=0, column=3, columnspan=1, padx=5, pady=5, sticky="ew")
entry_kpi.insert(0, load_kpi())

ttk.Label(button_money_frame, text="Tổng server:").grid(row=0, column=4, padx=5, pady=5)
entry_total_servers = ttk.Entry(button_money_frame)
entry_total_servers.grid(row=0, column=5, columnspan=1, padx=5, pady=5, sticky="ew")
entry_total_servers.insert(0, load_total_servers())

# Tải dữ liệu khi khởi động
# try:

# print("isAutoVLBS running: ", is_running)
if currentAutoName != None:
    print("isAutoVLBS running: True")
    run_check_status(1)
load_to_gui()
# except Exception as e:
#     messagebox.showerror("Error", f"Có lỗi xảy ra dòng 497 autoLogin!")
create_server_buttons()
# Bắt đầu vòng lặp giao diện
root.mainloop()
