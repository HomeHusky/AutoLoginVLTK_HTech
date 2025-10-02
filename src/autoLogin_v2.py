# ===============================
# 🧠 AUTO LOGIN VÕ LÂM TRUYỀN KỲ - VERSION 2.0
# ===============================
"""
Version 2.0 - Refactored với kiến trúc module hóa
Tách biệt logic thành các module độc lập, dễ bảo trì và mở rộng
"""

# ================================================================
# 📦 IMPORT THƯ VIỆN
# ================================================================
import tkinter as tk
from tkinter import ttk
import pyautogui

# Import modules
from modules.config import *
from modules.data_manager import data_manager
from modules.version_manager import version_manager
from modules.login_manager import login_manager
from modules.auto_update_manager import auto_update_manager
from modules.system_manager import system_manager

# Import tabs
from tabs.tab_dashboard import DashboardTab
from tabs.tab_account_manager import AccountManagerTab
from tabs.tab_path_manager import PathManagerTab
# from tabs.tab_status_manager import StatusManagerTab  # Tạm thời ẩn

# Import other modules
import GlobalFunction as GF
import checkStatusAcounts

# ================================================================
# ⚙️ GLOBAL SETTINGS
# ================================================================
pyautogui.FAILSAFE = PYAUTOGUI_FAILSAFE

# Global flags
is_checking_fix_vlbs = False


# ================================================================
# MAIN APPLICATION CLASS
# ================================================================

class AutoLoginApp:
    def __init__(self, root):
        self.root = root
        
        # Setup window TRƯỚC để app hiện ra ngay
        self.setup_window()
        self.root.update()  # Force update để window hiện ngay
        
        # Di chuyển console xuống góc dưới trái SAU KHI app đã hiện
        try:
            from move_console import move_console_to_bottom_left
            self.root.after(1000, move_console_to_bottom_left)  # Delay 1s
        except Exception as e:
            print(f"Không thể di chuyển console: {e}")
        
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
        
        # Thiết lập giao diện (setup_window đã gọi ở trên)
        self.setup_styles()
        self.create_tabs()
        
        # Load dữ liệu ban đầu
        self.initialize_data()
        
        # Print system info
        system_manager.print_system_info()
    
    # ==================== SETUP METHODS ====================
    
    def setup_window(self):
        """Thiết lập cửa sổ chính"""
        version = version_manager.get_current_version() or "Unknown"
        self.root.title(f"{WINDOW_TITLE_PREFIX} - {version}")
        # Bắt đầu với kích thước Dashboard nhỏ (bảng ẩn) - Góc trái trên
        self.root.geometry("650x450+0+0")
        self.root.resizable(*WINDOW_RESIZABLE)
    
    def setup_styles(self):
        """Thiết lập styles cho giao diện - Simple UI like original"""
        style = ttk.Style()
        style.theme_use(THEME)
        
        # Button styles - Simple
        style.configure("TButton",
                       padding=BUTTON_PADDING,
                       relief="flat",
                       background=BUTTON_BACKGROUND,
                       foreground=BUTTON_FOREGROUND)
        style.map("TButton", 
                 background=[('active', BUTTON_ACTIVE_BACKGROUND)])
        
        # Label styles
        style.configure("TLabel", 
                       padding=LABEL_PADDING, 
                       font=('Arial', 10))
        
        # Treeview styles
        style.configure("Treeview.Heading", 
                       font=('Arial', 10, 'bold'))
        style.configure("Treeview", 
                       rowheight=25)
    
    def create_tabs(self):
        """Tạo các tab"""
        self.tab_control = ttk.Notebook(self.root)
        
        # Tạo các frame cho tabs
        self.dashboard_tab_frame = ttk.Frame(self.tab_control)
        self.account_tab_frame = ttk.Frame(self.tab_control)
        self.path_tab_frame = ttk.Frame(self.tab_control)
        # self.status_tab_frame = ttk.Frame(self.tab_control)  # Tạm thời ẩn
        
        # Thêm tabs vào notebook với thứ tự mới
        self.tab_control.add(self.dashboard_tab_frame, text="📊 Dashboard")
        self.tab_control.add(self.account_tab_frame, text="👥 Quản lý Tài khoản")
        self.tab_control.add(self.path_tab_frame, text="⚙️ Cài đặt")
        # self.tab_control.add(self.status_tab_frame, text="Trạng thái Tài khoản")  # Tạm thời ẩn
        
        # Tạo callbacks dictionary
        callbacks = self.create_callbacks()
        
        # Khởi tạo các tab managers
        self.dashboard_tab = DashboardTab(
            self.dashboard_tab_frame,
            data_manager,
            callbacks
        )
        self.account_tab = AccountManagerTab(
            self.account_tab_frame, 
            data_manager, 
            callbacks
        )
        self.path_tab = PathManagerTab(
            self.path_tab_frame, 
            data_manager
        )
        # self.status_tab = StatusManagerTab(
        #     self.status_tab_frame, 
        #     data_manager, 
        #     callbacks
        # )
        
        # Bind events
        self.path_tab_frame.bind("<Visibility>", lambda e: self.path_tab.load_auto_data())
        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_selected)
        
        # Progress bar ở trên đầu
        self.create_progress_bar()
        
        self.tab_control.pack(expand=1, fill="both")
    
    def create_progress_bar(self):
        """Tạo progress bar ở trên đầu"""
        # Frame chứa progress bar
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(side="top", fill="x", padx=5, pady=5)
        
        # Label hiển thị trạng thái
        self.status_label = ttk.Label(progress_frame, 
                                      text="Sẵn sàng",
                                      font=('Segoe UI', 9),
                                      foreground=COLOR_TEXT_SECONDARY)
        self.status_label.pack(side="left", padx=5)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                           mode='determinate',
                                           length=200)
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=5)
        
        # Ẩn progress bar ban đầu
        self.progress_bar.pack_forget()
    
    def show_progress(self, message: str, value: int = 0):
        """Hiển thị progress bar với message"""
        self.status_label.config(text=message)
        if value >= 0:
            self.progress_bar.pack(side="left", fill="x", expand=True, padx=5)
            self.progress_bar['value'] = value
            self.root.update_idletasks()
    
    def hide_progress(self):
        """Ẩn progress bar"""
        self.status_label.config(text="Sẵn sàng")
        self.progress_bar.pack_forget()
        self.progress_bar['value'] = 0
    
    def setup_managers(self):
        """Setup các managers với callbacks"""
        # Setup login manager callbacks
        login_manager.set_on_login_complete_callback(self.on_login_complete)
        login_manager.set_on_login_username_callback(self.on_login_username)
        login_manager.get_title_mail_callback = self.get_title_mail  # Set callback để lấy title_mail
        
        # Setup auto update manager callbacks
        auto_update_manager.set_on_success_callback(self.on_auto_update_success)
    
    def create_callbacks(self):
        """Tạo dictionary chứa các callback functions"""
        return {
            # Version & Update
            'update_app': self.update_app,
            'alway_update_app': self.alway_update_app,
            
            # Login
            'start_login': self.start_login,
            'stop_login': self.stop_login,
            'test_accounts': self.test_accounts,
            
            # Auto Update
            'run_all_auto_update': self.run_all_auto_update,
            
            # Status
            'is_checking_fix_vlbs': lambda: is_checking_fix_vlbs,
            'set_checking_fix_vlbs': self.set_checking_fix_vlbs,
            
            # Getters
            'get_entry_title_mail': self.get_title_mail,
            'get_current_auto_name': lambda: login_manager.get_current_auto_name()
        }
    
    def initialize_data(self):
        """Khởi tạo dữ liệu ban đầu"""
        # Check Auto VLBS status
        if login_manager.get_current_auto_name():
            print("isAutoVLBS running: True")
            login_manager.check_auto_vlbs_status(1)
        
        # Load GUI data cho các tab
        self.dashboard_tab.load_to_gui()
        self.account_tab.load_to_gui()
        
        # Schedule startup check
        self.root.after(STARTUP_DELAY, self.run_after_ui)
    
    # ==================== EVENT HANDLERS ====================
    
    def on_tab_selected(self, event):
        """Xử lý khi chuyển tab - Auto resize window vừa khít"""
        selected_tab = self.tab_control.index(self.tab_control.select())
        
        # Update để tính toán kích thước
        self.root.update_idletasks()
        
        if selected_tab == self.tab_control.index(self.dashboard_tab_frame):
            # Dashboard tab - Auto resize theo nội dung
            if not self.dashboard_tab.is_table_visible:
                width = max(650, self.dashboard_tab_frame.winfo_reqwidth() + 20)
                height = max(450, self.dashboard_tab_frame.winfo_reqheight() + 80)
            else:
                width = max(650, self.dashboard_tab_frame.winfo_reqwidth() + 20)
                height = max(750, self.dashboard_tab_frame.winfo_reqheight() + 80)
            self.root.geometry(f"{width}x{height}+0+0")
            self.dashboard_tab.load_to_gui()
        elif selected_tab == self.tab_control.index(self.account_tab_frame):
            # Account tab - Auto resize
            width = max(750, self.account_tab_frame.winfo_reqwidth() + 20)
            height = max(700, self.account_tab_frame.winfo_reqheight() + 80)
            self.root.geometry(f"{width}x{height}+0+0")
            self.account_tab.load_to_gui()
        elif selected_tab == self.tab_control.index(self.path_tab_frame):
            # Settings tab - Auto resize (có scrollbar nên cố định)
            self.root.geometry("700x550+0+0")
        # elif selected_tab == self.tab_control.index(self.status_tab_frame):
        #     self.status_tab.load_initial_deposit_account()
        #     self.status_tab.save_gom_account()
        #     self.status_tab.load_to_tab_money_manager()
    
    # ==================== VERSION & UPDATE METHODS ====================
    
    def update_app(self):
        """Cập nhật ứng dụng"""
        if version_manager.update_app(show_messages=True):
            version_manager.restart_app()
    
    def alway_update_app(self):
        """Luôn cập nhật ứng dụng"""
        if version_manager.force_update(show_messages=True):
            version_manager.restart_app()
    
    # ==================== LOGIN METHODS ====================
    
    def start_login(self, is_auto_click_vlbs: bool):
        """
        Bắt đầu đăng nhập
        
        Args:
            is_auto_click_vlbs: Tự động click AutoVLBS
        """
        pass_accounts = self.dashboard_tab.get_pass_accounts()
        login_manager.start_login(
            is_auto_click_vlbs=is_auto_click_vlbs,
            pass_accounts=pass_accounts,
            show_confirm=True
        )
    
    def stop_login(self):
        """Dừng đăng nhập"""
        login_manager.stop_login()
    
    def test_accounts(self):
        """Test tài khoản"""
        self.show_progress("Đang kiểm tra Auto VLBS...", 30)
        login_manager.check_auto_vlbs_status(1)
        self.show_progress("Đang tải dữ liệu...", 70)
        self.dashboard_tab.load_to_gui()
        self.account_tab.load_to_gui()
        self.show_progress("Hoàn thành!", 100)
        from tkinter import messagebox
        messagebox.showinfo("Success", get_message("test_success"))
        self.hide_progress()

    def _get_pass_monitor(self) -> Optional[str]:
        """
        Lấy password monitor từ file
        
        Returns:
            str: Password hoặc None
        """
        try:
            with open(PASS_MONITOR_FILE, "r", encoding='utf-8') as file:
                return file.read().strip()
        except FileNotFoundError:
            print(f"File {PASS_MONITOR_FILE} không tồn tại.")
            return None
        except Exception as e:
            print(f"Error reading pass monitor: {e}")
            return None

    def is_all_logged_in(self) -> bool:
        """
        Kiểm tra tất cả account đã login
        
        Returns:
            bool: True nếu tất cả account đã login, False nếu còn account chưa login
        """
        try:
            data = self.data_manager.load_data()
            return all(account['is_logged_in'] for account in data['accounts'])
        except Exception as e:
            print(f"Error checking all logged in: {e}")
            return False

    def on_login_complete(self):
        """Callback khi đăng nhập hoàn tất"""
        try:
            # Clear and update dashboard
            self.dashboard_tab.clear_pass_accounts()
            
            # Check Auto VLBS status
            login_manager.check_auto_vlbs_status(1)
            
            # Force update all UI components
            self.dashboard_tab.load_to_gui()
            self.account_tab.load_to_gui()

            print("✅ Đã cập nhật giao diện sau khi đăng nhập")

            if self.is_all_logged_in() and self._get_pass_monitor() == SPECIAL_MONITOR_PASSWORD:
                try:
                    DashboardTab.on_start_check_fix_VLBS_button_click()
                except Exception as e:
                    print(f"❌ Lỗi khi tự động theo dõi: {e}")
            
        except Exception as e:
            print(f"❌ Lỗi khi cập nhật giao diện: {e}")
            # Try to recover by forcing a full UI refresh
            try:
                # Force update all UI components
                self.dashboard_tab.load_to_gui()
                self.account_tab.load_to_gui()
            except:
                pass
    
    def on_login_username(self, username: str):
        """
        Callback khi đăng nhập username thành công
        
        Args:
            username: Username đã login
        """
        self.dashboard_tab.update_status_to_logged_in(username)
    
    # ==================== AUTO UPDATE METHODS ====================
    
    def run_all_auto_update(self):
        """Chạy tất cả auto update"""
        auto_update_manager.run_all_auto_update(show_confirm=True)
    
    def on_auto_update_success(self):
        """Callback khi auto update thành công"""
        from tkinter import messagebox
        messagebox.showinfo("Thông báo", get_message("auto_update_success"))
    
    # ==================== UTILITY METHODS ====================
    
    def set_checking_fix_vlbs(self, value: bool):
        """Set trạng thái checking fix vlbs"""
        global is_checking_fix_vlbs
        is_checking_fix_vlbs = value
    
    def get_title_mail(self) -> str:
        """Lấy title mail từ config hoặc data"""
        try:
            # Thử lấy từ monitor_time.json hoặc config
            import os
            import json
            
            # Thử đọc từ monitor_time.json
            monitor_file = os.path.join(GF.join_directory_data(), 'monitor_time.json')
            if os.path.exists(monitor_file):
                with open(monitor_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('title_mail', DEFAULT_TITLE_MAIL)
            
            # Fallback về default
            return DEFAULT_TITLE_MAIL
        except Exception as e:
            print(f"Error getting title_mail: {e}")
            return DEFAULT_TITLE_MAIL
    
    def run_after_ui(self):
        """Chạy sau khi UI load xong"""
        try:
            sleep_time = data_manager.get_sleep_time()
            is_start_up = sleep_time.get('start_up', 0)
            
            if is_start_up == 1:
                if system_manager.is_system_just_booted():
                    print("is_start_up: True - System just booted, starting auto login...")
                    pass_accounts = self.dashboard_tab.get_pass_accounts()
                    login_manager.start_login(
                        is_auto_click_vlbs=True,
                        pass_accounts=pass_accounts,
                        show_confirm=False
                    )
                else:
                    print("is_start_up: True - But system has been running for a while, skipping auto login.")
            else:
                print("is_start_up: False")
        except Exception as e:
            print(f"Error in run_after_ui: {e}")


# ================================================================
# 🚀 MAIN ENTRY POINT
# ================================================================

def main():
    """Main entry point của ứng dụng"""
    root = tk.Tk()
    app = AutoLoginApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
