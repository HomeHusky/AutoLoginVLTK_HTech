# ===============================
# 🗄️ MONGODB MANAGER MODULE
# ===============================
"""
Module quản lý kết nối và lưu trữ dữ liệu lên MongoDB
Tự động tạo collection và quản lý thông tin máy chủ
"""

import os
import json
from typing import Optional, Dict, Any
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

import GlobalFunction as GF


class MongoDBManager:
    """
    Class quản lý MongoDB connection và operations
    """
    
    def __init__(self, uri: Optional[str] = None, db_name: str = "HtechVolam"):
        """
        Khởi tạo MongoDB Manager
        
        Args:
            uri: MongoDB connection string URI
            db_name: Tên database
        """
        self.uri = uri or "mongodb+srv://htechvolam:Htech317@htechvolam.oefc26z.mongodb.net/?retryWrites=true&w=majority&appName=HtechVolam"
        self.db_name = db_name
        self.client: Optional[MongoClient] = None
        self.db = None
    
    def connect(self) -> bool:
        """
        Kết nối tới MongoDB
        
        Returns:
            bool: True nếu kết nối thành công
        """
        try:
            self.client = MongoClient(self.uri, server_api=ServerApi('1'))
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            print("✅ Kết nối MongoDB thành công!")
            return True
        except Exception as e:
            print(f"❌ Lỗi kết nối MongoDB: {e}")
            return False
    
    def close(self):
        """Đóng kết nối MongoDB"""
        if self.client:
            self.client.close()
            print("🔒 Đã đóng kết nối MongoDB")
    
    def ensure_collection_exists(self, collection_name: str) -> bool:
        """
        Kiểm tra và tạo collection nếu chưa tồn tại
        
        Args:
            collection_name: Tên collection
            
        Returns:
            bool: True nếu collection đã tồn tại hoặc tạo thành công
        """
        try:
            if collection_name not in self.db.list_collection_names():
                self.db.create_collection(collection_name)
                print(f"✅ Đã tạo collection '{collection_name}'")
            return True
        except Exception as e:
            print(f"❌ Lỗi tạo collection: {e}")
            return False
    
    def get_title_mail(self) -> str:
        """
        Lấy title mail từ file monitor_time.json
        
        Returns:
            str: Title mail hoặc giá trị mặc định
        """
        try:
            monitor_file = os.path.join(GF.join_directory_data(), 'monitor_time.json')
            
            if os.path.exists(monitor_file):
                with open(monitor_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('title_mail', 'AutoVLBS Server')
            else:
                return 'AutoVLBS Server'
        except Exception as e:
            print(f"❌ Lỗi đọc title mail: {e}")
            return 'AutoVLBS Server'
    
    def count_online_offline_accounts(self) -> Dict[str, int]:
        """
        Đếm số account online và offline từ accounts.json
        
        Returns:
            dict: {"online": int, "offline": int, "total": int}
        """
        try:
            accounts_file = os.path.join(GF.join_directory_data(), 'accounts.json')
            
            if not os.path.exists(accounts_file):
                return {"online": 0, "offline": 0, "total": 0}
            
            with open(accounts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                accounts = data.get('accounts', [])
                
                online_count = sum(1 for acc in accounts if acc.get('is_logged_in', False))
                offline_count = len(accounts) - online_count
                
                return {
                    "online": online_count,
                    "offline": offline_count,
                    "total": len(accounts)
                }
        except Exception as e:
            print(f"❌ Lỗi đếm account: {e}")
            return {"online": 0, "offline": 0, "total": 0}
    
    def update_server_status(self, collection_name: str = "server_status") -> bool:
        """
        Cập nhật hoặc tạo mới thông tin máy chủ trong MongoDB
        
        Args:
            collection_name: Tên collection (mặc định: server_status)
            
        Returns:
            bool: True nếu thành công
        """
        try:
            # Đảm bảo đã kết nối
            if not self.client:
                if not self.connect():
                    return False
            
            # Đảm bảo collection tồn tại
            self.ensure_collection_exists(collection_name)
            
            # Lấy thông tin
            ten_may = self.get_title_mail()
            account_stats = self.count_online_offline_accounts()
            
            # Tạo document
            server_data = {
                "ten_may": ten_may,
                "so_acc_online": account_stats["online"],
                "so_acc_offline": account_stats["offline"],
                "tong_so_acc": account_stats["total"],
                "cap_nhat_luc": datetime.now(),
                "timestamp": datetime.now().isoformat()
            }
            
            # Lấy collection
            collection = self.db[collection_name]
            
            # Kiểm tra xem máy đã tồn tại chưa
            existing_server = collection.find_one({"ten_may": ten_may})
            
            if existing_server:
                # Cập nhật thông tin
                collection.update_one(
                    {"ten_may": ten_may},
                    {"$set": server_data}
                )
                print(f"✅ Đã cập nhật thông tin máy '{ten_may}': {account_stats['online']} online, {account_stats['offline']} offline")
            else:
                # Thêm mới
                server_data["ngay_tao"] = datetime.now()
                collection.insert_one(server_data)
                print(f"✅ Đã thêm mới máy '{ten_may}': {account_stats['online']} online, {account_stats['offline']} offline")
            
            return True
            
        except Exception as e:
            print(f"❌ Lỗi cập nhật server status: {e}")
            return False
    
    def get_server_status(self, ten_may: Optional[str] = None, collection_name: str = "server_status") -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin máy chủ từ MongoDB
        
        Args:
            ten_may: Tên máy (None = lấy máy hiện tại)
            collection_name: Tên collection
            
        Returns:
            dict: Thông tin máy chủ hoặc None
        """
        try:
            if not self.client:
                if not self.connect():
                    return None
            
            if ten_may is None:
                ten_may = self.get_title_mail()
            
            collection = self.db[collection_name]
            server_info = collection.find_one({"ten_may": ten_may})
            
            return server_info
            
        except Exception as e:
            print(f"❌ Lỗi lấy server status: {e}")
            return None
    
    def get_all_servers(self, collection_name: str = "server_status") -> list:
        """
        Lấy danh sách tất cả máy chủ
        
        Args:
            collection_name: Tên collection
            
        Returns:
            list: Danh sách các máy chủ
        """
        try:
            if not self.client:
                if not self.connect():
                    return []
            
            collection = self.db[collection_name]
            servers = list(collection.find())
            
            return servers
            
        except Exception as e:
            print(f"❌ Lỗi lấy danh sách servers: {e}")
            return []


# Singleton instance
mongodb_manager = MongoDBManager()


# ==================== HELPER FUNCTIONS ====================

def update_server_status_to_mongo() -> bool:
    """
    Helper function để cập nhật server status lên MongoDB
    
    Returns:
        bool: True nếu thành công
    """
    try:
        result = mongodb_manager.update_server_status()
        mongodb_manager.close()
        return result
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False


def get_current_server_status() -> Optional[Dict[str, Any]]:
    """
    Helper function để lấy thông tin máy chủ hiện tại
    
    Returns:
        dict: Thông tin máy chủ hoặc None
    """
    try:
        result = mongodb_manager.get_server_status()
        mongodb_manager.close()
        return result
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return None


if __name__ == "__main__":
    # Test module
    print("=== TEST MONGODB MANAGER ===")
    
    # Test kết nối
    if mongodb_manager.connect():
        # Test cập nhật server status
        mongodb_manager.update_server_status()
        
        # Test lấy thông tin
        server_info = mongodb_manager.get_server_status()
        if server_info:
            print(f"\n📊 Thông tin máy chủ:")
            print(f"   Tên máy: {server_info.get('ten_may')}")
            print(f"   Online: {server_info.get('so_acc_online')}")
            print(f"   Offline: {server_info.get('so_acc_offline')}")
            print(f"   Tổng: {server_info.get('tong_so_acc')}")
        
        # Đóng kết nối
        mongodb_manager.close()
