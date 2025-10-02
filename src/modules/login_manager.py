# ===============================
# 🔐 LOGIN MANAGER MODULE
# ===============================
"""
Module quản lý login và authentication
Tách biệt logic login khỏi UI
"""

import threading
import json
import os
from typing import Callable, Optional, List
from tkinter import messagebox
from datetime import datetime

import GlobalFunction as GF
import startLogin as START_LOGIN
import checkStatusAcounts
import notifier as NOTIFIER

from modules.config import PASS_MONITOR_FILE, SPECIAL_MONITOR_PASSWORD, get_message
from modules.data_manager import data_manager
from modules.mongodb_manager import mongodb_manager


class LoginManager:
    """
    Class quản lý quá trình login
    """
    
    def __init__(self):
        self.login_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.current_auto_name: Optional[str] = None
        self.auto_tool_path: Optional[str] = None
        self.sleep_time: Optional[dict] = None
        self.pass_accounts: List[str] = []
        
        # Callbacks
        self.on_login_complete_callback: Optional[Callable] = None
        self.on_login_username_callback: Optional[Callable] = None
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """Khởi tạo các giá trị ban đầu"""
        try:
            self.current_auto_name = GF.getNameAutoVLBS()
            self.auto_tool_path = START_LOGIN.load_auto_tool_path()
            self.sleep_time = START_LOGIN.load_sleepTime()
        except Exception as e:
            print(f"Error initializing LoginManager: {e}")
    
    # ==================== STATUS CHECK METHODS ====================
    
    def check_auto_vlbs_status(self, try_count: int = 1, auto_open: bool = True) -> bool:
        """
        Kiểm tra trạng thái Auto VLBS
        
        Args:
            try_count: Số lần thử lại
            auto_open: Tự động mở Auto VLBS nếu chưa chạy
        
        Returns:
            bool: True nếu Auto VLBS đang chạy
        """
        try:
            # Reload paths
            self.auto_tool_path = START_LOGIN.load_auto_tool_path()
            self.sleep_time = START_LOGIN.load_sleepTime()
            self.current_auto_name = GF.getNameAutoVLBS()
            
            # Nếu không tìm thấy Auto VLBS và auto_open = True
            if not self.current_auto_name and auto_open:
                print("Không tìm thấy Auto VLBS, đang tự động mở...")
                self.current_auto_name = START_LOGIN.auto_open_autoVLBS(
                    self.auto_tool_path, 
                    self.sleep_time
                )
                if self.current_auto_name:
                    print(f"Đã mở Auto VLBS thành công: {self.current_auto_name}")
                    return True
                else:
                    print("Không thể mở Auto VLBS!")
                    return False
            
            # Check status
            if not checkStatusAcounts.checkStatusAcounts(
                self.auto_tool_path, 
                self.current_auto_name, 
                self.sleep_time
            ):
                # Update auto name after check
                self.current_auto_name = GF.getNameAutoVLBS()
                
                # Check if Auto VLBS is running in background
                if not GF.checkAutoVlbsBackGroundRunning():
                    # Nếu auto_open = True, thử mở Auto VLBS
                    if auto_open and try_count > 0:
                        print("Auto VLBS không chạy, đang tự động mở...")
                        self.current_auto_name = START_LOGIN.auto_open_autoVLBS(
                            self.auto_tool_path, 
                            self.sleep_time
                        )
                        if self.current_auto_name:
                            print(f"Đã mở Auto VLBS thành công: {self.current_auto_name}")
                            return True
                    
                    # Retry if try_count > 0
                    if try_count > 0:
                        print(f"Auto VLBS không chạy, thử lại... (còn {try_count} lần)")
                        return self.check_auto_vlbs_status(try_count - 1, auto_open=False)
                    else:
                        print("Đã hết số lần thử, Auto VLBS không chạy!")
                        messagebox.showerror("Error", "Có lỗi xảy ra khi kiểm tra Auto VLBS!")
                        return False
                else:
                    # Auto VLBS is running, return True
                    print("Auto VLBS đang chạy trong background")
                    return True
            
            # Check passed successfully
            print("Kiểm tra Auto VLBS thành công")
            return True
            
        except Exception as e:
            print(f"Error checking Auto VLBS status: {e}")
            return False
    
    def all_accounts_logged_in(self) -> bool:
        """
        Kiểm tra tất cả account đã login chưa
        
        Returns:
            bool: True nếu tất cả đã login
        """
        return data_manager.all_accounts_logged_in()
    
    # ==================== LOGIN METHODS ====================
    
    def start_login(self, is_auto_click_vlbs: bool, 
                   pass_accounts: List[str] = None,
                   show_confirm: bool = True) -> bool:
        """
        Bắt đầu quá trình đăng nhập
        
        Args:
            is_auto_click_vlbs: Tự động click AutoVLBS
            pass_accounts: Danh sách accounts bỏ qua
            show_confirm: Hiển thị confirm dialog
        
        Returns:
            bool: True nếu bắt đầu thành công
        """
        if self.is_running:
            messagebox.showwarning("Warning", "Đăng nhập đang chạy!")
            return False
        
        # Show confirmation
        if show_confirm:
            confirm = messagebox.askyesno(
                "Thông báo",
                get_message("login_confirm")
            )
            if not confirm:
                messagebox.showinfo("Thông báo", get_message("login_reminder"))
                return False
        
        try:
            # Check Auto VLBS status
            if not self.check_auto_vlbs_status(1):
                return False
            
            # Update pass accounts
            if pass_accounts is not None:
                self.pass_accounts = pass_accounts
            
            # Start login thread
            self.is_running = True
            self.login_thread = threading.Thread(
                target=START_LOGIN.runStartLogin,
                args=(
                    is_auto_click_vlbs,
                    self._on_login_complete_internal,
                    self.current_auto_name,
                    self.pass_accounts,
                    self._on_login_username_internal
                )
            )
            self.login_thread.daemon = True
            self.login_thread.start()
            
            print("Đã bắt đầu quá trình đăng nhập")
            return True
            
        except Exception as e:
            self.is_running = False
            messagebox.showerror("Error", get_message("login_error", str(e)))
            return False
    
    def stop_login(self) -> bool:
        """
        Dừng quá trình đăng nhập
        
        Returns:
            bool: True nếu dừng thành công
        """
        try:
            print("Đang dừng quá trình đăng nhập...")
            
            # Gọi hàm stop để set cờ stop_login = True
            START_LOGIN.stop()
            
            # Đợi thread kết thúc (timeout 5s)
            if self.login_thread and self.login_thread.is_alive():
                print("Đang đợi thread kết thúc...")
                self.login_thread.join(timeout=5)
                
                # Nếu thread vẫn còn sống sau 5s
                if self.login_thread.is_alive():
                    print("⚠️ Thread vẫn đang chạy sau 5s, có thể cần thời gian để dừng hoàn toàn")
            
            # Set flag
            self.is_running = False
            
            print("✅ Đã dừng thành công")
            messagebox.showinfo("Stopped", get_message("login_stopped"))
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi dừng: {e}")
            messagebox.showerror("Error", get_message("login_stop_error", str(e)))
            return False
    
    # ==================== CALLBACK METHODS ====================
    
    def set_on_login_complete_callback(self, callback: Callable):
        """
        Set callback khi login hoàn tất
        
        Args:
            callback: Function callback
        """
        self.on_login_complete_callback = callback
    
    def set_on_login_username_callback(self, callback: Callable):
        """
        Set callback khi login username thành công
        
        Args:
            callback: Function callback nhận username
        """
        self.on_login_username_callback = callback
    
    def _on_login_complete_internal(self):
        """Internal callback khi login hoàn tất"""
        self.is_running = False
        self.pass_accounts.clear()
        
        # Check Auto VLBS status
        self.check_auto_vlbs_status(1)
        
        # Check if all accounts logged in
        time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        is_all_logged_in = self.all_accounts_logged_in()
        
        # Get pass monitor
        pass_monitor = self._get_pass_monitor()
        
        print(f"MAU KHAU THEO DOI: {pass_monitor}")

        # Handle retry logic if not all accounts are logged in
        if not is_all_logged_in and not hasattr(self, '_has_retried_login'):
            print("⏳ Chưa đăng nhập đủ tài khoản, thử lại lần nữa...")
            self._has_retried_login = True
            self.start_login(is_auto_click_vlbs=True, show_confirm=False)
            return
        
        # Reset retry flag
        if hasattr(self, '_has_retried_login'):
            delattr(self, '_has_retried_login')
        
        if is_all_logged_in:
            print("✅ Tất cả account đã login.")
        else:
            print("❌ Vẫn còn account chưa login sau 2 lần thử.")
        
        # Send notification and update MongoDB if special password
        if pass_monitor == SPECIAL_MONITOR_PASSWORD:
            try:
                # Get title mail from monitor_time.json
                title_mail = self._get_title_mail()
                
                # Send Discord notification
                NOTIFIER.send_discord_login_report(
                    title_mail, 
                    time_stamp, 
                    is_all_logged_in
                )
                
                # Update server status to MongoDB
                self._update_mongodb_status()

                # Start VLBS check if all accounts are logged in
                if (is_all_logged_in and 
                    hasattr(self, 'app') and 
                    hasattr(self.app, 'dashboard_tab') and
                    hasattr(self.app.dashboard_tab, 'on_start_check_fix_VLBS_button_click') and
                    not self.callbacks.get('is_checking_fix_vlbs')()):
                    
                    print("🔄 Tự động bắt đầu kiểm tra fix lỗi VLBS...")
                    self.app.dashboard_tab.on_start_check_fix_VLBS_button_click()
            except Exception as e:
                print(f"Error sending notification: {e}")
        
        # Call external callback
        if self.on_login_complete_callback:
            self.on_login_complete_callback()
    
    def _on_login_username_internal(self, username: str):
        """
        Internal callback khi login username thành công
        
        Args:
            username: Username đã login
        """
        # Update account status in data
        data_manager.update_account_login_status(username, True)
        
        # Call external callback
        if self.on_login_username_callback:
            self.on_login_username_callback(username)
    
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
    
    def _get_title_mail(self) -> str:
        """
        Lấy title mail từ file monitor_time.json
        
        Returns:
            str: Title mail hoặc giá trị mặc định
        """
        try:
            import GlobalFunction as GF
            monitor_file = os.path.join(GF.join_directory_data(), 'monitor_time.json')
            
            if os.path.exists(monitor_file):
                with open(monitor_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('title_mail', 'AutoVLBS Server')
            else:
                print("File monitor_time.json không tồn tại.")
                return 'AutoVLBS Server'
        except Exception as e:
            print(f"Error reading title mail: {e}")
            return 'AutoVLBS Server'
    
    def _update_mongodb_status(self):
        """
        Cập nhật thông tin máy chủ lên MongoDB
        Tự động tạo collection nếu chưa tồn tại
        """
        try:
            print("📤 Đang cập nhật thông tin lên MongoDB...")
            mongodb_manager.update_server_status()
            mongodb_manager.close()
        except Exception as e:
            print(f"❌ Lỗi cập nhật MongoDB: {e}")
    
    # ==================== UTILITY METHODS ====================
    
    def get_current_auto_name(self) -> Optional[str]:
        """
        Lấy tên Auto VLBS hiện tại
        
        Returns:
            str: Tên auto hoặc None
        """
        return self.current_auto_name
    
    def reload_config(self):
        """Reload cấu hình từ file"""
        self._initialize()
    
    def is_login_running(self) -> bool:
        """
        Kiểm tra login có đang chạy không
        
        Returns:
            bool: True nếu đang chạy
        """
        return self.is_running


# Singleton instance
login_manager = LoginManager()
