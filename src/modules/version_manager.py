# ===============================
# 🔄 VERSION MANAGER MODULE
# ===============================
"""
Module quản lý version và update ứng dụng
Tách biệt logic update khỏi UI
"""

import os
import sys
import shutil
import zipfile
import requests
from tkinter import messagebox
from typing import Optional, Tuple
from modules.config import (
    VERSION_FILE, GITHUB_VERSION_URL, GITHUB_DOWNLOAD_URL,
    get_message
)


class VersionManager:
    """
    Class quản lý version và update ứng dụng
    """
    
    def __init__(self):
        # Lấy đường dẫn tuyệt đối đến thư mục gốc project
        current_dir = os.path.dirname(os.path.abspath(__file__))  # modules/
        src_dir = os.path.dirname(current_dir)  # src/
        project_root = os.path.dirname(src_dir)  # project root
        
        self.version_file = os.path.join(project_root, VERSION_FILE)
        self.github_version_url = GITHUB_VERSION_URL
        self.github_download_url = GITHUB_DOWNLOAD_URL
        self.current_version = None
    
    # ==================== VERSION METHODS ====================
    
    def get_current_version(self) -> Optional[str]:
        """
        Lấy phiên bản hiện tại từ file
        
        Returns:
            str: Version string hoặc None nếu không tìm thấy
        """
        if self.current_version:
            return self.current_version
        
        try:
            with open(self.version_file, "r", encoding='utf-8') as file:
                self.current_version = file.read().strip()
                return self.current_version
        except FileNotFoundError:
            print(get_message("file_not_found", self.version_file))
            return None
        except Exception as e:
            print(f"Error reading version file: {e}")
            return None
    
    def get_latest_version(self) -> Optional[str]:
        """
        Lấy phiên bản mới nhất từ GitHub
        
        Returns:
            str: Latest version string hoặc None nếu lỗi
        """
        try:
            response = requests.get(self.github_version_url, timeout=10)
            if response.status_code == 200:
                return response.text.strip()
            else:
                print(f"Cannot connect to GitHub. Status code: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"Error fetching latest version: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def compare_versions(self, current: str, latest: str) -> int:
        """
        So sánh 2 version
        
        Args:
            current: Version hiện tại
            latest: Version mới nhất
        
        Returns:
            int: -1 nếu current < latest, 0 nếu bằng, 1 nếu current > latest
        """
        try:
            current_parts = [int(x) for x in current.split('.')]
            latest_parts = [int(x) for x in latest.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(current_parts), len(latest_parts))
            current_parts += [0] * (max_len - len(current_parts))
            latest_parts += [0] * (max_len - len(latest_parts))
            
            for c, l in zip(current_parts, latest_parts):
                if c < l:
                    return -1
                elif c > l:
                    return 1
            
            return 0
        except Exception as e:
            print(f"Error comparing versions: {e}")
            return 0
    
    # ==================== UPDATE METHODS ====================
    
    def check_for_update(self, show_ui: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Kiểm tra có update mới không
        
        Args:
            show_ui: Hiển thị messagebox hay không
        
        Returns:
            Tuple[bool, str]: (has_update, latest_version)
        """
        current_version = self.get_current_version()
        
        if current_version is None:
            print("Không thể kiểm tra phiên bản hiện tại.")
            return False, None
        
        latest_version = self.get_latest_version()
        
        if latest_version is None:
            print("Không thể kết nối đến GitHub.")
            return False, None
        
        # Compare versions
        comparison = self.compare_versions(current_version, latest_version)
        
        if comparison < 0:  # Current < Latest
            if show_ui:
                confirm = messagebox.askyesno("Thông báo", get_message("update_available"))
                return confirm, latest_version
            return True, latest_version
        else:
            if show_ui:
                print(get_message("update_latest"))
            return False, None
    
    def download_update(self, temp_dir: str = "temp_update", 
                       zip_path: str = "update.zip") -> bool:
        """
        Tải update từ GitHub
        
        Args:
            temp_dir: Thư mục tạm
            zip_path: Đường dẫn file zip
        
        Returns:
            bool: True nếu tải thành công
        """
        try:
            print("Đang tải update từ GitHub...")
            response = requests.get(self.github_download_url, timeout=30)
            
            if response.status_code != 200:
                print(f"Cannot download update. Status code: {response.status_code}")
                return False
            
            # Save zip file
            with open(zip_path, "wb") as file:
                file.write(response.content)
            
            print("Tải update thành công!")
            return True
            
        except requests.RequestException as e:
            print(f"Error downloading update: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False
    
    def extract_update(self, zip_path: str = "update.zip", 
                      temp_dir: str = "temp_update") -> bool:
        """
        Giải nén update
        
        Args:
            zip_path: Đường dẫn file zip
            temp_dir: Thư mục tạm
        
        Returns:
            bool: True nếu giải nén thành công
        """
        try:
            print("Đang giải nén update...")
            
            # Extract zip
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
            
            print("Giải nén thành công!")
            return True
            
        except zipfile.BadZipFile as e:
            print(f"Invalid zip file: {e}")
            return False
        except Exception as e:
            print(f"Error extracting update: {e}")
            return False
    
    def apply_update(self, temp_dir: str = "temp_update") -> bool:
        """
        Áp dụng update vào thư mục hiện tại
        
        Args:
            temp_dir: Thư mục tạm chứa update
        
        Returns:
            bool: True nếu áp dụng thành công
        """
        try:
            print("Đang áp dụng update...")
            
            # Get extracted directory
            extracted_dir = os.path.join(temp_dir, os.listdir(temp_dir)[0])
            
            # Move files
            for item in os.listdir(extracted_dir):
                source = os.path.join(extracted_dir, item)
                destination = os.path.join(".", item)
                
                if os.path.isdir(source):
                    if os.path.exists(destination):
                        shutil.rmtree(destination)
                    shutil.move(source, destination)
                else:
                    if os.path.exists(destination):
                        os.remove(destination)
                    shutil.move(source, destination)
            
            print("Áp dụng update thành công!")
            return True
            
        except Exception as e:
            print(f"Error applying update: {e}")
            return False
    
    def cleanup_update(self, zip_path: str = "update.zip", 
                      temp_dir: str = "temp_update") -> bool:
        """
        Dọn dẹp file tạm sau khi update
        
        Args:
            zip_path: Đường dẫn file zip
            temp_dir: Thư mục tạm
        
        Returns:
            bool: True nếu dọn dẹp thành công
        """
        try:
            # Remove zip file
            if os.path.exists(zip_path):
                os.remove(zip_path)
            
            # Remove temp directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            print("Dọn dẹp thành công!")
            return True
            
        except Exception as e:
            print(f"Error cleaning up: {e}")
            return False
    
    def download_and_update(self) -> bool:
        """
        Tải và cập nhật ứng dụng (full process)
        
        Returns:
            bool: True nếu update thành công
        """
        try:
            # Download
            if not self.download_update():
                return False
            
            # Extract
            if not self.extract_update():
                self.cleanup_update()
                return False
            
            # Apply
            if not self.apply_update():
                self.cleanup_update()
                return False
            
            # Cleanup
            self.cleanup_update()
            
            print("Cập nhật thành công!")
            return True
            
        except Exception as e:
            print(f"Lỗi khi cập nhật: {e}")
            self.cleanup_update()
            return False
    
    def restart_app(self):
        """Khởi động lại ứng dụng"""
        try:
            python = sys.executable
            os.execl(python, python, *sys.argv)
        except Exception as e:
            print(f"Error restarting app: {e}")
    
    # ==================== HIGH-LEVEL METHODS ====================
    
    def update_app(self, show_messages: bool = True) -> bool:
        """
        Kiểm tra và cập nhật ứng dụng (với UI)
        
        Args:
            show_messages: Hiển thị messagebox hay không
        
        Returns:
            bool: True nếu đã update và cần restart
        """
        try:
            has_update, latest_version = self.check_for_update(show_ui=show_messages)
            
            if not has_update:
                if show_messages:
                    messagebox.showinfo("Update", get_message("update_latest"))
                return False
            
            # Download and update
            if self.download_and_update():
                if show_messages:
                    messagebox.showinfo("Update", get_message("update_success"))
                return True
            else:
                if show_messages:
                    messagebox.showerror("Update Failed", "Không thể cập nhật ứng dụng")
                return False
                
        except Exception as e:
            if show_messages:
                messagebox.showerror("Update Failed", get_message("update_failed", str(e)))
            return False
    
    def force_update(self, show_messages: bool = True) -> bool:
        """
        Cập nhật ứng dụng không cần kiểm tra version
        
        Args:
            show_messages: Hiển thị messagebox hay không
        
        Returns:
            bool: True nếu đã update và cần restart
        """
        try:
            if self.download_and_update():
                if show_messages:
                    messagebox.showinfo("Update", get_message("update_success"))
                return True
            else:
                if show_messages:
                    messagebox.showerror("Update Failed", "Không thể cập nhật ứng dụng")
                return False
                
        except Exception as e:
            if show_messages:
                messagebox.showerror("Update Failed", get_message("update_failed", str(e)))
            return False


# Singleton instance
version_manager = VersionManager()
