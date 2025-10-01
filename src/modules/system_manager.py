# ===============================
# 💻 SYSTEM MANAGER MODULE  
# ===============================
"""
Module quản lý system và startup
Tách biệt logic system khỏi UI
"""

import os
import psutil
import winshell
from datetime import datetime, timedelta
from win32com.client import Dispatch
from typing import Optional

from modules.config import BOOT_TIME_THRESHOLD


class SystemManager:
    """
    Class quản lý system và startup
    """
    
    def __init__(self):
        self.quick_run_path = self._get_quick_run_path()
        self.startup_folder = winshell.startup()
        self.shortcut_name = "QuickRun.lnk"
    
    # ==================== PATH METHODS ====================
    
    def _get_quick_run_path(self) -> str:
        """
        Lấy đường dẫn tới quick_run.vbs
        
        Returns:
            str: Đường dẫn đầy đủ
        """
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)  # src
            parent_dir = os.path.dirname(parent_dir)   # project root
            return os.path.join(parent_dir, "quick_run.vbs")
        except Exception as e:
            print(f"Error getting quick_run path: {e}")
            return ""
    
    # ==================== BOOT TIME METHODS ====================
    
    def get_boot_time(self) -> Optional[datetime]:
        """
        Lấy thời gian boot của hệ thống
        
        Returns:
            datetime: Thời gian boot hoặc None nếu lỗi
        """
        try:
            return datetime.fromtimestamp(psutil.boot_time())
        except Exception as e:
            print(f"Error getting boot time: {e}")
            return None
    
    def get_uptime(self) -> Optional[timedelta]:
        """
        Lấy thời gian hệ thống đã chạy
        
        Returns:
            timedelta: Uptime hoặc None nếu lỗi
        """
        try:
            boot_time = self.get_boot_time()
            if boot_time:
                return datetime.now() - boot_time
            return None
        except Exception as e:
            print(f"Error getting uptime: {e}")
            return None
    
    def is_system_just_booted(self, threshold_minutes: int = BOOT_TIME_THRESHOLD) -> bool:
        """
        Kiểm tra xem hệ thống vừa mới khởi động hay không
        
        Args:
            threshold_minutes: Số phút để coi là "vừa mới bật"
        
        Returns:
            bool: True nếu máy vừa bật trong vòng threshold_minutes phút
        """
        try:
            boot_time = self.get_boot_time()
            if not boot_time:
                return False
            
            current_time = datetime.now()
            uptime = current_time - boot_time
            
            print(f"Boot time: {boot_time}")
            print(f"Current time: {current_time}")
            print(f"Uptime: {uptime}")
            
            return uptime < timedelta(minutes=threshold_minutes)
            
        except Exception as e:
            print(f"Error checking boot time: {e}")
            return False
    
    # ==================== STARTUP METHODS ====================
    
    def is_startup_enabled(self) -> bool:
        """
        Kiểm tra startup có được bật không
        
        Returns:
            bool: True nếu startup được bật
        """
        shortcut_path = os.path.join(self.startup_folder, self.shortcut_name)
        return os.path.exists(shortcut_path)
    
    def enable_startup(self) -> bool:
        """
        Bật startup (tạo shortcut)
        
        Returns:
            bool: True nếu thành công
        """
        try:
            shortcut_path = os.path.join(self.startup_folder, self.shortcut_name)
            
            if os.path.exists(shortcut_path):
                print("ℹ️ Shortcut đã tồn tại.")
                return True
            
            if not self.quick_run_path or not os.path.exists(self.quick_run_path):
                print(f"❌ Không tìm thấy file quick_run.vbs tại: {self.quick_run_path}")
                return False
            
            # Create shortcut
            target = self.quick_run_path
            working_dir = os.path.dirname(target)
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = working_dir
            shortcut.save()
            
            print(f"✅ Đã tạo shortcut: {shortcut_path}")
            return True
            
        except Exception as e:
            print(f"Error enabling startup: {e}")
            return False
    
    def disable_startup(self) -> bool:
        """
        Tắt startup (xóa shortcut)
        
        Returns:
            bool: True nếu thành công
        """
        try:
            shortcut_path = os.path.join(self.startup_folder, self.shortcut_name)
            
            if not os.path.exists(shortcut_path):
                print("ℹ️ Không có shortcut để xóa.")
                return True
            
            os.remove(shortcut_path)
            print("❌ Đã xóa shortcut, ứng dụng sẽ không tự chạy nữa.")
            return True
            
        except Exception as e:
            print(f"Error disabling startup: {e}")
            return False
    
    def set_startup(self, enable: bool) -> bool:
        """
        Bật/tắt startup
        
        Args:
            enable: True để bật, False để tắt
        
        Returns:
            bool: True nếu thành công
        """
        if enable:
            return self.enable_startup()
        else:
            return self.disable_startup()
    
    # ==================== SYSTEM INFO METHODS ====================
    
    def get_system_info(self) -> dict:
        """
        Lấy thông tin hệ thống
        
        Returns:
            dict: Dictionary chứa thông tin hệ thống
        """
        try:
            boot_time = self.get_boot_time()
            uptime = self.get_uptime()
            
            return {
                'boot_time': boot_time.strftime("%Y-%m-%d %H:%M:%S") if boot_time else "Unknown",
                'uptime': str(uptime) if uptime else "Unknown",
                'uptime_seconds': uptime.total_seconds() if uptime else 0,
                'is_just_booted': self.is_system_just_booted(),
                'startup_enabled': self.is_startup_enabled(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            }
        except Exception as e:
            print(f"Error getting system info: {e}")
            return {}
    
    def print_system_info(self):
        """In thông tin hệ thống ra console"""
        info = self.get_system_info()
        print("\n" + "="*50)
        print("SYSTEM INFORMATION")
        print("="*50)
        for key, value in info.items():
            print(f"{key:20}: {value}")
        print("="*50 + "\n")
    
    # ==================== PROCESS METHODS ====================
    
    def is_process_running(self, process_name: str) -> bool:
        """
        Kiểm tra process có đang chạy không
        
        Args:
            process_name: Tên process (ví dụ: "game.exe")
        
        Returns:
            bool: True nếu process đang chạy
        """
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() == process_name.lower():
                    return True
            return False
        except Exception as e:
            print(f"Error checking process: {e}")
            return False
    
    def get_process_count(self, process_name: str) -> int:
        """
        Đếm số lượng process đang chạy
        
        Args:
            process_name: Tên process
        
        Returns:
            int: Số lượng process
        """
        try:
            count = 0
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() == process_name.lower():
                    count += 1
            return count
        except Exception as e:
            print(f"Error counting processes: {e}")
            return 0
    
    def kill_process(self, process_name: str) -> int:
        """
        Kill tất cả process với tên cho trước
        
        Args:
            process_name: Tên process
        
        Returns:
            int: Số lượng process đã kill
        """
        try:
            killed = 0
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() == process_name.lower():
                    proc.kill()
                    killed += 1
            return killed
        except Exception as e:
            print(f"Error killing processes: {e}")
            return 0


# Singleton instance
system_manager = SystemManager()
