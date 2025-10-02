# ===============================
# 📁 DATA MANAGER MODULE
# ===============================
"""
Module quản lý tất cả các thao tác đọc/ghi dữ liệu JSON
Tách biệt logic data khỏi UI, dễ test và tái sử dụng
"""

import json
import os
from typing import Dict, List, Any, Optional
import GlobalFunction as GF
from modules.config import (
    ACCOUNTS_FILE, GLOBAL_TIME_FILE, SERVERS_FILE,
    DEFAULT_AUTO_NAMES, DEFAULT_AUTO_TOOL_PATH, DEFAULT_SLEEP_TIME
)


class DataManager:
    """
    Class quản lý việc đọc/ghi dữ liệu JSON
    Singleton pattern để đảm bảo chỉ có 1 instance
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.accounts_file_path = ACCOUNTS_FILE
        self.global_time_file = GLOBAL_TIME_FILE
        self.servers_path = SERVERS_FILE
        self._cache = {}
        self._initialized = True
    
    # ==================== ACCOUNTS DATA ====================
    
    def load_accounts(self) -> Dict[str, Any]:
        """
        Tải dữ liệu tài khoản từ file JSON
        
        Returns:
            Dict chứa thông tin accounts
        """
        try:
            return GF.read_json_file(self.accounts_file_path)
        except FileNotFoundError:
            return self._get_default_accounts_data()
    
    def load_data(self) -> Dict[str, Any]:
        """
        Alias cho load_accounts() để tương thích với code cũ
        
        Returns:
            Dict chứa thông tin accounts
        """
        return self.load_accounts()
    
    def save_accounts(self, data: Dict[str, Any]) -> bool:
        """
        Lưu dữ liệu tài khoản vào file JSON
        
        Args:
            data: Dictionary chứa dữ liệu accounts
        
        Returns:
            bool: True nếu lưu thành công
        """
        try:
            file_path = os.path.join(GF.join_directory_data(), self.accounts_file_path)
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving accounts: {e}")
            return False
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """
        Alias cho save_accounts() để tương thích với code cũ
        
        Args:
            data: Dictionary chứa dữ liệu accounts
        
        Returns:
            bool: True nếu lưu thành công
        """
        return self.save_accounts(data)
    
    def get_account_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin account theo username
        
        Args:
            username: Tên tài khoản
        
        Returns:
            Dict chứa thông tin account hoặc None
        """
        data = self.load_accounts()
        for account in data.get('accounts', []):
            if account.get('username') == username:
                return account
        return None
    
    def add_account(self, account_data: Dict[str, Any]) -> bool:
        """
        Thêm tài khoản mới
        
        Args:
            account_data: Dictionary chứa thông tin account
        
        Returns:
            bool: True nếu thêm thành công
        """
        data = self.load_accounts()
        
        # Check if account exists
        if self.account_exists(account_data.get('username'), account_data.get('game_path')):
            return False
        
        data['accounts'].append(account_data)
        return self.save_accounts(data)
    
    def update_account(self, username: str, account_data: Dict[str, Any]) -> bool:
        """
        Cập nhật thông tin tài khoản
        
        Args:
            username: Tên tài khoản cần update
            account_data: Dictionary chứa thông tin mới
        
        Returns:
            bool: True nếu update thành công
        """
        data = self.load_accounts()
        
        for i, account in enumerate(data['accounts']):
            if account.get('username') == username:
                data['accounts'][i] = account_data
                return self.save_accounts(data)
        
        return False
    
    def delete_account(self, username: str) -> bool:
        """
        Xóa tài khoản
        
        Args:
            username: Tên tài khoản cần xóa
        
        Returns:
            bool: True nếu xóa thành công
        """
        data = self.load_accounts()
        
        for i, account in enumerate(data['accounts']):
            if account.get('username') == username:
                del data['accounts'][i]
                return self.save_accounts(data)
        
        return False
    
    def account_exists(self, username: str, game_path: str) -> bool:
        """
        Kiểm tra tài khoản đã tồn tại chưa
        
        Args:
            username: Tên tài khoản
            game_path: Đường dẫn game
        
        Returns:
            bool: True nếu tồn tại
        """
        data = self.load_accounts()
        for account in data.get('accounts', []):
            if (account.get('username') == username and 
                account.get('game_path') == game_path):
                return True
        return False
    
    def get_all_accounts(self) -> List[Dict[str, Any]]:
        """
        Lấy danh sách tất cả tài khoản
        
        Returns:
            List các account dictionaries
        """
        data = self.load_accounts()
        return data.get('accounts', [])
    
    def update_account_login_status(self, username: str, is_logged_in: bool) -> bool:
        """
        Cập nhật trạng thái đăng nhập của tài khoản
        
        Args:
            username: Tên tài khoản
            is_logged_in: Trạng thái đăng nhập
        
        Returns:
            bool: True nếu update thành công
        """
        data = self.load_accounts()
        
        for account in data['accounts']:
            if account.get('username') == username:
                account['is_logged_in'] = is_logged_in
                return self.save_accounts(data)
        
        return False
    
    def all_accounts_logged_in(self) -> bool:
        """
        Kiểm tra tất cả account đã login chưa (chỉ kiểm tra những account có is_select = false)
        
        Returns:
            bool: True nếu tất cả đã login
        """
        accounts = self.get_all_accounts()
        if not accounts:
            return False
        
        # Chỉ kiểm tra những accounts có is_select = false (không bị bỏ qua)
        selected_accounts = [account for account in accounts if not account.get('is_select', False)]
        
        for account in selected_accounts:
            if not account.get('is_logged_in', False):
                return False
        
        return True
    
    # ==================== GLOBAL TIME DATA ====================
    
    def load_global_time(self) -> Dict[str, Any]:
        """
        Tải dữ liệu thời gian global
        
        Returns:
            Dict chứa thông tin sleep time
        """
        try:
            return GF.read_config_file(self.global_time_file)
        except FileNotFoundError:
            return {"sleepTime": [DEFAULT_SLEEP_TIME]}
    
    def save_global_time(self, data: Dict[str, Any]) -> bool:
        """
        Lưu dữ liệu thời gian global
        
        Args:
            data: Dictionary chứa sleep time data
        
        Returns:
            bool: True nếu lưu thành công
        """
        try:
            file_path = os.path.join(GF.join_directory_config(), self.global_time_file)
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving global time: {e}")
            return False
    
    def save_global_time_data(self, data: Dict[str, Any]) -> bool:
        """
        Alias cho save_global_time() để tương thích với code cũ
        
        Args:
            data: Dictionary chứa sleep time data
        
        Returns:
            bool: True nếu lưu thành công
        """
        return self.save_global_time(data)
    
    def get_sleep_time(self) -> Dict[str, Any]:
        """
        Lấy thông tin sleep time
        
        Returns:
            Dict chứa sleep time settings
        """
        data = self.load_global_time()
        sleep_times = data.get('sleepTime', [])
        return sleep_times[0] if sleep_times else DEFAULT_SLEEP_TIME
    
    # ==================== SERVERS DATA ====================
    
    def load_servers(self) -> Dict[str, Any]:
        """
        Tải dữ liệu servers
        
        Returns:
            Dict chứa thông tin servers
        """
        try:
            return GF.read_config_file(self.servers_path)
        except FileNotFoundError:
            return {"servers": {}, "folder_game": ""}
    
    def save_servers(self, data: Dict[str, Any]) -> bool:
        """
        Lưu dữ liệu servers
        
        Args:
            data: Dictionary chứa servers data
        
        Returns:
            bool: True nếu lưu thành công
        """
        try:
            file_path = os.path.join(GF.join_directory_config(), self.servers_path)
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving servers: {e}")
            return False
    
    def get_servers_list(self) -> Dict[str, str]:
        """
        Lấy danh sách servers
        
        Returns:
            Dict mapping server name -> path
        """
        data = self.load_servers()
        return data.get('servers', {})
    
    def update_server_path(self, server_name: str, path: str) -> bool:
        """
        Cập nhật đường dẫn server
        
        Args:
            server_name: Tên server
            path: Đường dẫn mới
        
        Returns:
            bool: True nếu update thành công
        """
        data = self.load_servers()
        data['servers'][server_name] = path
        return self.save_servers(data)
    
    # ==================== HELPER METHODS ====================
    
    def _get_default_accounts_data(self) -> Dict[str, Any]:
        """
        Lấy dữ liệu accounts mặc định
        
        Returns:
            Dict chứa cấu trúc mặc định
        """
        return {
            "accounts": [],
            "autoNames": DEFAULT_AUTO_NAMES,
            "auto_tool_path": DEFAULT_AUTO_TOOL_PATH
        }
    
    def clear_cache(self):
        """Xóa cache dữ liệu"""
        self._cache.clear()
    
    def read_json_file(self, filename: str, use_data_dir: bool = True) -> Dict[str, Any]:
        """
        Đọc file JSON tổng quát
        
        Args:
            filename: Tên file
            use_data_dir: True nếu file trong thư mục data
        
        Returns:
            Dict chứa dữ liệu JSON
        """
        try:
            if use_data_dir:
                return GF.read_json_file(filename)
            else:
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            return {}
    
    def write_json_file(self, filename: str, data: Dict[str, Any], 
                       use_data_dir: bool = True) -> bool:
        """
        Ghi file JSON tổng quát
        
        Args:
            filename: Tên file
            data: Dữ liệu cần ghi
            use_data_dir: True nếu file trong thư mục data
        
        Returns:
            bool: True nếu ghi thành công
        """
        try:
            if use_data_dir:
                file_path = os.path.join(GF.join_directory_data(), filename)
            else:
                file_path = filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, file, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error writing {filename}: {e}")
            return False


# Singleton instance
data_manager = DataManager()
