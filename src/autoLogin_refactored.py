# ===============================
# 🧠 AUTO LOGIN VÕ LÂM TRUYỀN KỲ - REFACTORED
# ===============================

# ================================================================
# 📦 1. IMPORT THƯ VIỆN
# ================================================================
import json
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import startLogin as START_LOGIN
import realTimeCheckBugAutoVLBS as REAL_TIME_CHECK
import GlobalFunction as GF
import checkStatusAcounts
import threading
import pyautogui
import time
import os
import requests
import zipfile
import sys
import shutil
import notifier as NOTIFIER
import psutil
from datetime import datetime, timedelta

# Import các tab modules
from tabs.tab_account_manager import AccountManagerTab
from tabs.tab_path_manager import PathManagerTab
from tabs.tab_status_manager import StatusManagerTab

# ================================================================
# ⚙️ 2. BIẾN TOÀN CỤC / CẤU HÌNH
# ================================================================

is_checking_fix_vlbs = False
is_testing_code = False
pyautogui.FAILSAFE = False

# ================================================================
# 📁 3. DATA MANAGER CLASS
# ================================================================

class DataManager:
    """Class quản lý việc đọc/ghi dữ liệu JSON"""
    
    def __init__(self):
        self.accounts_file_path = 'accounts.json'
        self.global_time_file = 'global_time.json'
        self.servers_path = 'servers.json'
    
    def load_data(self):
        """Tải dữ liệu từ accounts.json"""
        try:
            return GF.read_json_file(self.accounts_file_path)
        except FileNotFoundError:
            return {
                "accounts": [],
                "autoNames": ["vocongtruyenky", "congthanhchienxua", "AutoVLBS"],
                "auto_tool_path": "D:/VoLamTruyenKy/AutoVLBS19/TrainJX.exe"
            }
    
    def load_global_time(self):
        """Tải dữ liệu thời gian global"""
        try:
            return GF.read_config_file(self.global_time_file)
        except FileNotFoundError:
            return {
                "sleepTime": [{
                    "wait_time_open": 15,
                    "wait_time_open2": 45,
                    "wait_time_load": 2,
                    "wait_time_server": 8,
                    "wait_time_open_trainjx": 3,
                    "wait_time_load_autovlbs": 5,
                    "try_number": 3,
                    "global_time_sleep": 1,
                    "hide_effects": 1,
                    "start_up": 1
                }]
            }
    
    def save_data(self, data):
        """Lưu dữ liệu vào accounts.json"""
        with open(os.path.join(GF.join_directory_data(), self.accounts_file_path), 'w') as file:
            json.dump(data, file, ensure_ascii=True, indent=4)
    
    def save_global_time_data(self, data):
        """Lưu dữ liệu thời gian global"""
        with open(os.path.join(GF.join_directory_config(), self.global_time_file), 'w') as file:
            json.dump(data, file, ensure_ascii=True, indent=4)

# ================================================================
# 🎯 4. MAIN APPLICATION CLASS
# ================================================================

class AutoLoginApp:
    def __init__(self, root):
        self.root = root
        self.data_manager = DataManager()
        
        # Biến toàn cục
        self.login_thread = None
        self.auto_update_thread = None
        self.is_running_AutoUpdate = False
        self.stop_AutoUpdate_event = False
        self.currentAutoName = None
        self.auto_tool_path = None
        self.sleepTime = None
        self.global_time_sleep = GF.load_global_time_sleep()
        
        # Khởi tạo currentAutoName
        try:
            self.currentAutoName = GF.getNameAutoVLBS()
        except Exception as e:
            print("Error", str(e))
        
        # Thiết lập giao diện
        self.setup_window()
        self.setup_styles()
        self.create_tabs()
        
        # Load dữ liệu ban đầu
        self.initialize_data()
    
    def setup_window(self):
        """Thiết lập cửa sổ chính"""
        version = self.get_current_version()
        self.root.title(f"Auto Login Htechnology - {version}")
        self.root.geometry("850x700+0+0")
        self.root.resizable(True, True)
    
    def setup_styles(self):
        """Thiết lập styles cho giao diện"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("TButton",
                       padding=6,
                       relief="flat",
                       background="#5783db",
                       foreground="white")
        
        style.map("TButton", background=[('active', '#4681f4')])
        
        style.configure("TLabel", padding=6, font=('Arial', 10))
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        style.configure("Treeview", rowheight=25)
    
    def create_tabs(self):
        """Tạo các tab"""
        self.tab_control = ttk.Notebook(self.root)
        
        # Tạo các frame cho tabs
        self.account_tab_frame = ttk.Frame(self.tab_control)
        self.path_tab_frame = ttk.Frame(self.tab_control)
        self.status_tab_frame = ttk.Frame(self.tab_control)
        
        # Thêm tabs vào notebook
        self.tab_control.add(self.account_tab_frame, text="Quản lý Tài khoản")
        self.tab_control.add(self.path_tab_frame, text="Quản lý Đường dẫn")
        self.tab_control.add(self.status_tab_frame, text="Trạng thái Tài khoản")
        
        # Tạo callbacks dictionary
        callbacks = self.create_callbacks()
        
        # Khởi tạo các tab managers
        self.account_tab = AccountManagerTab(self.account_tab_frame, self.data_manager, callbacks)
        self.path_tab = PathManagerTab(self.path_tab_frame, self.data_manager)
        self.status_tab = StatusManagerTab(self.status_tab_frame, self.data_manager, callbacks)
        
        # Bind events
        self.path_tab_frame.bind("<Visibility>", lambda e: self.path_tab.load_auto_data())
        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_selected)
        
        self.tab_control.pack(expand=1, fill="both")
    
    def create_callbacks(self):
        """Tạo dictionary chứa các callback functions"""
        return {
            'update_app': self.update_app,
            'alway_update_app': self.alway_update_app,
            'start_login': self.start_login,
            'stop_login': self.stop_login,
            'test_accounts': self.test_accounts,
            'run_all_auto_update': self.run_all_auto_update,
            'is_checking_fix_vlbs': lambda: is_checking_fix_vlbs,
            'set_checking_fix_vlbs': self.set_checking_fix_vlbs,
            'get_entry_title_mail': lambda: self.status_tab.get_entry_title_mail(),
            'get_current_auto_name': lambda: self.currentAutoName
        }
    
    def initialize_data(self):
        """Khởi tạo dữ liệu ban đầu"""
        if self.currentAutoName != None:
            print("isAutoVLBS running: True")
            self.run_check_status(1)
        
        self.account_tab.load_to_gui()
        
        # Chạy sau khi UI load xong
        self.root.after(4000, self.run_after_ui)
    
    def on_tab_selected(self, event):
        """Xử lý khi chuyển tab"""
        selected_tab = self.tab_control.index(self.tab_control.select())
        if selected_tab == self.tab_control.index(self.status_tab_frame):
            self.status_tab.load_initial_deposit_account()
            self.status_tab.save_gom_account()
            self.status_tab.load_to_tab_money_manager()
        elif selected_tab == self.tab_control.index(self.account_tab_frame):
            self.account_tab.load_to_gui()
    
    # ==================== VERSION & UPDATE METHODS ====================
    
    def get_current_version(self):
        """Lấy phiên bản hiện tại"""
        version_file = "version.txt"
        try:
            with open(version_file, "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            print(f"File {version_file} không tồn tại.")
            return None
    
    def check_for_update(self):
        """Kiểm tra cập nhật"""
        url = "https://raw.githubusercontent.com/HomeHusky/AutoLoginVLTK_HTech/master/version.txt"
        current_version = self.get_current_version()
        
        if current_version is None:
            print("Không thể kiểm tra phiên bản hiện tại.")
            return False
        
        try:
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
    
    def download_and_update(self):
        """Tải và cập nhật ứng dụng"""
        url = "https://github.com/HomeHusky/AutoLoginVLTK_HTech/archive/refs/heads/master.zip"
        zip_path = "update.zip"
        
        try:
            response = requests.get(url)
            with open(zip_path, "wb") as file:
                file.write(response.content)
            
            temp_dir = "temp_update"
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
            
            extracted_dir = os.path.join(temp_dir, os.listdir(temp_dir)[0])
            for item in os.listdir(extracted_dir):
                s = os.path.join(extracted_dir, item)
                d = os.path.join(".", item)
                if os.path.isdir(s):
                    if os.path.exists(d):
                        shutil.rmtree(d)
                    shutil.move(s, d)
                else:
                    shutil.move(s, d)
            
            os.remove(zip_path)
            shutil.rmtree(temp_dir)
            
            print("Cập nhật thành công!")
        except Exception as e:
            print(f"Lỗi khi cập nhật: {e}")
    
    def restart_app(self):
        """Khởi động lại ứng dụng"""
        python = sys.executable
        os.execl(python, python, *sys.argv)
    
    def update_app(self):
        """Cập nhật ứng dụng"""
        try:
            result = self.check_for_update()
            
            if not result:
                messagebox.showinfo("Update", "Bạn đang sử dụng phiên bản mới nhất.")
            elif result == 2:
                pass
            else:
                self.download_and_update()
                messagebox.showinfo("Update", "Ứng dụng đã được cập nhật thành công. Bắt đầu khởi động lại.")
                self.restart_app()
        except Exception as e:
            messagebox.showerror("Update Failed", f"Quá trình cập nhật thất bại: {e}")
    
    def alway_update_app(self):
        """Luôn cập nhật ứng dụng"""
        try:
            self.download_and_update()
            messagebox.showinfo("Update", "Ứng dụng đã được cập nhật thành công. Bắt đầu khởi động lại.")
            self.restart_app()
        except Exception as e:
            messagebox.showerror("Update Failed", f"Quá trình cập nhật thất bại: {e}")
    
    # ==================== LOGIN METHODS ====================
    
    def run_check_status(self, tryTest):
        """Kiểm tra trạng thái Auto VLBS"""
        self.auto_tool_path = START_LOGIN.load_auto_tool_path()
        self.sleepTime = START_LOGIN.load_sleepTime()
        self.currentAutoName = GF.getNameAutoVLBS()
        
        if not checkStatusAcounts.checkStatusAcounts(self.auto_tool_path, self.currentAutoName, self.sleepTime):
            self.currentAutoName = GF.getNameAutoVLBS()
            
            # Kiểm tra Auto VLBS có chạy trong background không
            if not GF.checkAutoVlbsBackGroundRunning():
                # Nếu không chạy và còn lần thử -> thử lại
                if tryTest > 0:
                    print(f"Auto VLBS không chạy, thử lại... (còn {tryTest} lần)")
                    self.run_check_status(tryTest-1)
                    return
                else:
                    # Hết lần thử -> báo lỗi
                    print("Đã hết số lần thử, Auto VLBS không chạy!")
                    messagebox.showerror("Error", f"Có lỗi xảy ra dòng 32 autoLogin!")
                    return
            else:
                # Auto VLBS đang chạy -> thành công
                print("Auto VLBS đang chạy trong background")
                return
    
    def start_login(self, isAutoClickVLBS):
        """Bắt đầu đăng nhập"""
        confirm = messagebox.askyesno(
            "Thông báo",
            "Vui lòng chuyển sang tiếng Anh và tắt CAPS LOCK trước khi bắt đầu. Bạn đã thực hiện chưa?"
        )
        
        if confirm:
            try:
                self.run_check_status(1)
                pass_accounts = self.account_tab.get_pass_accounts()
                self.login_thread = threading.Thread(
                    target=START_LOGIN.runStartLogin,
                    args=(isAutoClickVLBS, self.on_login_complete, self.currentAutoName, 
                         pass_accounts, self.on_login_username)
                )
                self.login_thread.start()
            except Exception as e:
                messagebox.showerror("Error", f"Không thể bắt đầu quá trình đăng nhập: {e}")
        else:
            messagebox.showinfo("Thông báo", "Vui lòng thực hiện yêu cầu trước khi tiếp tục.")
    
    def start_login_without_confirm(self, isAutoClickVLBS):
        """Bắt đầu đăng nhập không cần xác nhận"""
        try:
            self.run_check_status(1)
            pass_accounts = self.account_tab.get_pass_accounts()
            self.login_thread = threading.Thread(
                target=START_LOGIN.runStartLogin,
                args=(isAutoClickVLBS, self.on_login_complete, self.currentAutoName, 
                     pass_accounts, self.on_login_username)
            )
            self.login_thread.start()
        except Exception as e:
            messagebox.showerror("Error", f"Không thể bắt đầu quá trình đăng nhập: {e}")
    
    def stop_login(self):
        """Dừng đăng nhập"""
        try:
            START_LOGIN.stop()
            if self.login_thread and self.login_thread.is_alive():
                self.login_thread.join()
            messagebox.showinfo("Stopped", "Dừng đăng nhập thành công.")
        except Exception as e:
            messagebox.showerror("Error", f"Không thể dừng quá trình đăng nhập: {e}")
    
    def test_accounts(self):
        """Test tài khoản"""
        self.run_check_status(1)
        messagebox.showinfo("Success", "Kiểm tra thành công.")
        self.account_tab.load_to_gui()
    
    def on_login_complete(self):
        """Callback khi đăng nhập hoàn tất"""
        self.account_tab.clear_pass_accounts()
        print(self.account_tab.get_pass_accounts())
        self.run_check_status(1)
        self.account_tab.load_to_gui()
        
        time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        is_all_accounts_logged_in = False
        file_path = "accounts.json"
        pass_monitor = self.get_pass_monitor()
        
        print("MAU KHAU THEO DOI:", pass_monitor)
        if self.all_accounts_logged_in(file_path):
            print("✅ Tất cả account đã login.")
            if is_checking_fix_vlbs:
                return
            is_all_accounts_logged_in = True
            
            print(pass_monitor == '0919562182qQ!')
            if pass_monitor == '0919562182qQ!':
                # Gọi hàm start check fix VLBS
                pass
        else:
            print("❌ Vẫn còn account chưa login.")
        
        if pass_monitor == '0919562182qQ!':
            entry_title_mail = self.status_tab.get_entry_title_mail()
            NOTIFIER.send_discord_login_report(entry_title_mail, time_stamp, is_all_accounts_logged_in)
    
    def on_login_username(self, username):
        """Callback khi đăng nhập username"""
        self.account_tab.update_status_to_logged_in(username)
    
    def all_accounts_logged_in(self, json_path: str) -> bool:
        """Kiểm tra tất cả account đã login chưa"""
        with open(os.path.join(GF.join_directory_data(), json_path), "r") as f:
            data = json.load(f)
        
        accounts = data.get("accounts", [])
        if not accounts:
            return False
        
        for acc in accounts:
            if not acc.get("is_logged_in", False):
                return False
        
        return True
    
    def get_pass_monitor(self):
        """Lấy password monitor"""
        pass_file = "pass_monitor.txt"
        try:
            with open(pass_file, "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            print(f"File {pass_file} không tồn tại.")
            return None
    
    # ==================== AUTO UPDATE METHODS ====================
    
    def run_all_auto_update(self):
        """Chạy tất cả auto update"""
        global is_running_AutoUpdate, stop_AutoUpdate_event, auto_update_thread
        
        if not self.is_running_AutoUpdate:
            confirm = messagebox.askyesno(
                "Thông báo",
                "Thao tác này sẽ chạy tất cả AutoUpdate của các server mà dữ liệu đang có!"
            )
            if confirm:
                self.stop_AutoUpdate_event = False
                self.is_running_AutoUpdate = True
                
                GF.copy_auto_update_path_to_auto_update_path()
                GF.copy_auto_update_path_to_fix_web_ctcx_path()
                GF.replace_AutoUpdate_to_fix_web_ctcx()
                
                fix_web_ctcx_file = 'fix_web_ctcx.json'
                auto_update_file = 'autoUpdate_path.json'
                fix_web_ctcx_data = GF.read_json_file(fix_web_ctcx_file)
                auto_update_data = GF.read_json_file(auto_update_file)
                
                print("Đã chạy AutoUpdate của các server!")
                self.auto_update_thread = threading.Thread(
                    target=self.thread_auto_update,
                    args=(auto_update_data, fix_web_ctcx_data, self.on_auto_update_success)
                )
                self.auto_update_thread.daemon = True
                self.auto_update_thread.start()
            else:
                return
        else:
            self.is_running_AutoUpdate = False
            self.stop_AutoUpdate_event = True
    
    def thread_auto_update(self, auto_update_data, fix_web_ctcx_data, callback):
        """Thread chạy auto update"""
        for path in fix_web_ctcx_data['fix_web_ctcx_paths']:
            if self.stop_AutoUpdate_event:
                messagebox.showinfo("Thông báo", "Dừng AutoUpdate thành công!")
                return
            try:
                print(path)
                working_dir = os.path.dirname(path)
                try:
                    subprocess.Popen(path, cwd=working_dir)
                except Exception as e:
                    print("Lỗi khi mở fix_web:", e)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể mở file {path}: {str(e)}")
        
        for path in auto_update_data['auto_update_paths']:
            if self.stop_AutoUpdate_event:
                messagebox.showinfo("Thông báo", "Dừng AutoUpdate thành công!")
                return
            try:
                print(path)
                working_dir = os.path.dirname(path)
                try:
                    subprocess.Popen(path, cwd=working_dir)
                except Exception as e:
                    print("Lỗi khi mở AutoUpdate:", e)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể mở file {path}: {str(e)}")
        callback()
    
    def on_auto_update_success(self):
        """Callback khi auto update thành công"""
        self.is_running_AutoUpdate = False
        self.stop_AutoUpdate_event = True
        messagebox.showinfo("Thông báo", "Chạy AutoUpdate thành công!")
    
    # ==================== STARTUP METHODS ====================
    
    def is_system_just_booted(self, threshold_minutes=2):
        """Kiểm tra xem hệ thống vừa mới khởi động hay không"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            current_time = datetime.now()
            uptime = current_time - boot_time
            
            print(f"Boot time: {boot_time}")
            print(f"Current time: {current_time}")
            print(f"Uptime: {uptime}")
            
            return uptime < timedelta(minutes=threshold_minutes)
        except Exception as e:
            print(f"Error checking boot time: {e}")
            return False
    
    def run_after_ui(self):
        """Chạy sau khi UI load xong"""
        try:
            is_start_up = START_LOGIN.load_sleepTime()[0]['start_up']
            if is_start_up == 1:
                if self.is_system_just_booted(threshold_minutes=2):
                    print("is_start_up: True - System just booted, starting auto login...")
                    self.start_login_without_confirm(1)
                else:
                    print("is_start_up: True - But system has been running for a while, skipping auto login.")
            else:
                print("is_start_up: False")
        except Exception as e:
            print("Error", str(e))
    
    def set_checking_fix_vlbs(self, value):
        """Set trạng thái checking fix vlbs"""
        global is_checking_fix_vlbs
        is_checking_fix_vlbs = value

# ================================================================
# 🚀 5. MAIN ENTRY POINT
# ================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoLoginApp(root)
    root.mainloop()
