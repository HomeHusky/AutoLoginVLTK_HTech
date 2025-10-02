"""
Script test kết nối MongoDB và kiểm tra collection
Chạy để verify MongoDB hoạt động đúng
"""

import sys
import os

# Thêm thư mục src vào path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.mongodb_manager import mongodb_manager

def test_connection():
    """Test kết nối MongoDB"""
    print("=" * 60)
    print("🔍 TEST KẾT NỐI MONGODB")
    print("=" * 60)
    print()
    
    # Test kết nối
    print("1️⃣ Đang kết nối MongoDB...")
    if mongodb_manager.connect():
        print("✅ Kết nối thành công!\n")
        
        # Kiểm tra database
        print(f"📊 Database: {mongodb_manager.db_name}")
        print(f"📋 Collections hiện có:")
        collections = mongodb_manager.db.list_collection_names()
        for col in collections:
            count = mongodb_manager.db[col].count_documents({})
            print(f"   - {col}: {count} documents")
        print()
        
        # Test cập nhật server status
        print("2️⃣ Đang test cập nhật server status...")
        success = mongodb_manager.update_server_status(collection_name="server_status")
        
        if success:
            print("✅ Cập nhật server status thành công!\n")
            
            # Lấy thông tin vừa cập nhật
            print("3️⃣ Đang lấy thông tin máy chủ...")
            server_info = mongodb_manager.get_server_status()
            
            if server_info:
                print("✅ Thông tin máy chủ:")
                print(f"   - Tên máy: {server_info.get('ten_may')}")
                print(f"   - Accounts online: {server_info.get('so_acc_online')}")
                print(f"   - Accounts offline: {server_info.get('so_acc_offline')}")
                print(f"   - Tổng accounts: {server_info.get('tong_so_acc')}")
                print(f"   - Cập nhật lúc: {server_info.get('cap_nhat_luc')}")
            else:
                print("⚠️ Không tìm thấy thông tin máy chủ")
        else:
            print("❌ Cập nhật server status thất bại!")
        
        # Đóng kết nối
        mongodb_manager.close()
        
        print()
        print("=" * 60)
        print("✅ TEST HOÀN TẤT!")
        print("=" * 60)
        return True
    else:
        print("❌ Kết nối thất bại!")
        print()
        print("Kiểm tra:")
        print("1. MongoDB URI có đúng không?")
        print("2. Internet connection có ổn định không?")
        print("3. MongoDB Atlas có cho phép IP của bạn không?")
        return False

if __name__ == "__main__":
    test_connection()
    input("\nNhấn Enter để thoát...")
