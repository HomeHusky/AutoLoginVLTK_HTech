# 🗄️ MongoDB Manager Module

## Mô tả
Module quản lý kết nối MongoDB và tự động cập nhật thông tin máy chủ (server status) lên database.

## Tính năng

### ✅ Tự động tạo Collection
- Kiểm tra collection `server_status` có tồn tại chưa
- Tự động tạo collection nếu chưa có
- Không cần setup thủ công

### 📊 Quản lý thông tin máy chủ
Module tự động lưu và cập nhật các thông tin sau:

- **ten_may**: Tên máy (lấy từ `monitor_time.json`)
- **so_acc_online**: Số account đang online
- **so_acc_offline**: Số account đang offline
- **tong_so_acc**: Tổng số account
- **cap_nhat_luc**: Thời gian cập nhật (datetime)
- **timestamp**: Timestamp dạng ISO string
- **ngay_tao**: Ngày tạo record (chỉ khi thêm mới)

### 🔄 Logic cập nhật
1. **Nếu chưa có máy trong database**: Thêm mới record
2. **Nếu đã có máy trong database**: Cập nhật số account online/offline

## Cách sử dụng

### 1. Import module
```python
from modules.mongodb_manager import mongodb_manager, update_server_status_to_mongo
```

### 2. Cập nhật thông tin lên MongoDB
```python
# Cách 1: Sử dụng helper function (đơn giản)
update_server_status_to_mongo()

# Cách 2: Sử dụng trực tiếp manager
mongodb_manager.connect()
mongodb_manager.update_server_status()
mongodb_manager.close()
```

### 3. Lấy thông tin máy chủ
```python
# Lấy thông tin máy hiện tại
server_info = mongodb_manager.get_server_status()
print(f"Online: {server_info['so_acc_online']}")
print(f"Offline: {server_info['so_acc_offline']}")

# Lấy thông tin máy khác
server_info = mongodb_manager.get_server_status(ten_may="Máy chủ 1")

# Lấy tất cả máy chủ
all_servers = mongodb_manager.get_all_servers()
for server in all_servers:
    print(f"{server['ten_may']}: {server['so_acc_online']} online")
```

## Tích hợp tự động

Module đã được tích hợp vào `LoginManager`:
- Tự động cập nhật thông tin lên MongoDB sau khi login hoàn tất
- Được gọi trong hàm `_on_login_complete_internal()`
- Không cần can thiệp thủ công

## Cấu trúc Database

### Database: `HtechVolam`
### Collection: `server_status`

#### Document Schema:
```json
{
  "_id": ObjectId("..."),
  "ten_may": "Máy chủ AutoVLBS",
  "so_acc_online": 15,
  "so_acc_offline": 5,
  "tong_so_acc": 20,
  "cap_nhat_luc": ISODate("2025-10-02T01:30:00.000Z"),
  "timestamp": "2025-10-02T01:30:00.123456",
  "ngay_tao": ISODate("2025-10-01T10:00:00.000Z")
}
```

## Test Module

Chạy file trực tiếp để test:
```bash
python modules/mongodb_manager.py
```

Output mẫu:
```
=== TEST MONGODB MANAGER ===
✅ Kết nối MongoDB thành công!
✅ Đã cập nhật thông tin máy 'Máy chủ AutoVLBS': 15 online, 5 offline

📊 Thông tin máy chủ:
   Tên máy: Máy chủ AutoVLBS
   Online: 15
   Offline: 5
   Tổng: 20
🔒 Đã đóng kết nối MongoDB
```

## Lưu ý

1. **Connection String**: URI MongoDB đã được cấu hình sẵn trong module
2. **Auto Close**: Module tự động đóng kết nối sau mỗi operation
3. **Error Handling**: Tất cả functions đều có xử lý lỗi và log chi tiết
4. **Thread Safe**: Có thể sử dụng trong môi trường multi-threading

## Dependencies

```python
pymongo>=4.0.0
```

Cài đặt:
```bash
pip install pymongo
```
