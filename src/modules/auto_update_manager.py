# ===============================
# 🔄 AUTO UPDATE MANAGER MODULE
# ===============================
"""
Module quản lý auto update servers
Tách biệt logic auto update khỏi UI
"""

import os
import subprocess
import threading
from typing import Callable, Optional, List
from tkinter import messagebox

import GlobalFunction as GF
from modules.config import FIX_WEB_CTCX_FILE, AUTO_UPDATE_FILE, get_message


class AutoUpdateManager:
    """
    Class quản lý auto update servers
    """
    
    def __init__(self):
        self.auto_update_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.stop_event = False
        
        # Callbacks
        self.on_success_callback: Optional[Callable] = None
        self.on_error_callback: Optional[Callable] = None
    
    # ==================== UPDATE METHODS ====================
    
    def run_all_auto_update(self, show_confirm: bool = True) -> bool:
        """
        Chạy tất cả auto update của các server
        
        Args:
            show_confirm: Hiển thị confirm dialog
        
        Returns:
            bool: True nếu bắt đầu thành công
        """
        if self.is_running:
            # Đang chạy -> Dừng lại
            self.stop_auto_update()
            return False
        
        # Show confirmation
        if show_confirm:
            confirm = messagebox.askyesno(
                "Thông báo",
                get_message("auto_update_confirm")
            )
            if not confirm:
                return False
        
        try:
            # Prepare data
            self._prepare_update_data()
            
            # Load data
            fix_web_ctcx_data = GF.read_json_file(FIX_WEB_CTCX_FILE)
            auto_update_data = GF.read_json_file(AUTO_UPDATE_FILE)
            
            # Start thread
            self.is_running = True
            self.stop_event = False
            
            self.auto_update_thread = threading.Thread(
                target=self._run_update_thread,
                args=(auto_update_data, fix_web_ctcx_data)
            )
            self.auto_update_thread.daemon = True
            self.auto_update_thread.start()
            
            print("Đã bắt đầu AutoUpdate của các server!")
            return True
            
        except Exception as e:
            self.is_running = False
            messagebox.showerror("Error", f"Không thể chạy AutoUpdate: {e}")
            # print(f"Không thể chạy AutoUpdate: {e}")
            return False
    
    def stop_auto_update(self) -> bool:
        """
        Dừng auto update
        
        Returns:
            bool: True nếu dừng thành công
        """
        self.is_running = False
        self.stop_event = True
        
        if self.auto_update_thread and self.auto_update_thread.is_alive():
            self.auto_update_thread.join(timeout=5)
        
        return True
    
    def _prepare_update_data(self):
        """Chuẩn bị dữ liệu update"""
        try:
            GF.copy_auto_update_path_to_auto_update_path()
            GF.copy_auto_update_path_to_fix_web_ctcx_path()
            GF.replace_AutoUpdate_to_fix_web_ctcx()
        except Exception as e:
            print(f"Error preparing update data: {e}")
            raise
    
    def _run_update_thread(self, auto_update_data: dict, fix_web_ctcx_data: dict):
        """
        Thread chạy auto update
        
        Args:
            auto_update_data: Dữ liệu auto update
            fix_web_ctcx_data: Dữ liệu fix web
        """
        try:
            # Run fix web first
            self._run_fix_web_updates(fix_web_ctcx_data)
            
            # Then run auto updates
            self._run_auto_updates(auto_update_data)
            
            # Success
            self.is_running = False
            self.stop_event = False
            
            if self.on_success_callback:
                self.on_success_callback()
            else:
                messagebox.showinfo("Thông báo", get_message("auto_update_success"))
                
        except Exception as e:
            self.is_running = False
            self.stop_event = False
            
            if self.on_error_callback:
                self.on_error_callback(str(e))
            else:
                messagebox.showerror("Error", f"Lỗi khi chạy AutoUpdate: {e}")
    
    def _run_fix_web_updates(self, fix_web_ctcx_data: dict):
        """
        Chạy fix web updates
        
        Args:
            fix_web_ctcx_data: Dữ liệu fix web
        """
        paths = fix_web_ctcx_data.get('fix_web_ctcx_paths', [])
        
        for path in paths:
            if self.stop_event:
                messagebox.showinfo("Thông báo", get_message("auto_update_stopped"))
                return
            
            self._run_executable(path, "fix_web")
    
    def _run_auto_updates(self, auto_update_data: dict):
        """
        Chạy auto updates
        
        Args:
            auto_update_data: Dữ liệu auto update
        """
        paths = auto_update_data.get('auto_update_paths', [])
        
        for path in paths:
            if self.stop_event:
                messagebox.showinfo("Thông báo", get_message("auto_update_stopped"))
                return
            
            self._run_executable(path, "AutoUpdate")
    
    def _run_executable(self, path: str, exe_type: str):
        """
        Chạy file executable
        
        Args:
            path: Đường dẫn file
            exe_type: Loại executable (fix_web hoặc AutoUpdate)
        """
        try:
            print(f"Running {exe_type}: {path}")
            
            working_dir = os.path.dirname(path)
            subprocess.Popen(path, cwd=working_dir)
            
        except Exception as e:
            print(f"Lỗi khi mở {exe_type}: {e}")
            # messagebox.showerror("Lỗi", f"Không thể mở file {path}: {str(e)}")
    
    # ==================== CALLBACK METHODS ====================
    
    def set_on_success_callback(self, callback: Callable):
        """
        Set callback khi auto update thành công
        
        Args:
            callback: Function callback
        """
        self.on_success_callback = callback
    
    def set_on_error_callback(self, callback: Callable):
        """
        Set callback khi auto update lỗi
        
        Args:
            callback: Function callback nhận error message
        """
        self.on_error_callback = callback
    
    # ==================== UTILITY METHODS ====================
    
    def is_update_running(self) -> bool:
        """
        Kiểm tra auto update có đang chạy không
        
        Returns:
            bool: True nếu đang chạy
        """
        return self.is_running
    
    def get_status(self) -> str:
        """
        Lấy trạng thái hiện tại
        
        Returns:
            str: Trạng thái
        """
        if self.is_running:
            return "running"
        elif self.stop_event:
            return "stopping"
        else:
            return "stopped"


# Singleton instance
auto_update_manager = AutoUpdateManager()
