# 📊 Tóm tắt cập nhật MongoDB

## ✅ Đã hoàn thành

### 1. Cập nhật KPI mặc định
- **Tài khoản thường**: 48 Kv/day (1 giờ tăng 2 Kv)
- **Tài khoản gom tiền**: 96 Kv/day (1 giờ tăng 4 Kv - gấp đôi)

**Files đã sửa:**
- `src/modules/config.py` - DEFAULT_KPI và DEFAULT_KPI_GOM
- `src/autoLogin.py` - load_kpi() return "48"
- `src/tabs/tab_status_manager.py` - load_kpi() return "48"
- `src/realTimeCheckBugAutoVLBS.py` - kpi_1m và kpi_gom_1m

### 2. Thêm cập nhật MongoDB vào realTimeCheckBugAutoVLBS

**Đã thêm:**
- Import `mongodb_manager` từ `modules.mongodb_manager`
- Hàm `update_mongodb_server_status()` - Cập nhật thông tin máy chủ lên MongoDB
- Gọi `update_mongodb_server_status()` ngay sau khi cập nhật accounts.json và trước khi gửi Discord

**Luồng hoạt động:**
```
1. Kiểm tra accounts (mỗi X phút)
2. Cập nhật trạng thái is_logged_in trong accounts.json
3. ✨ CẬP NHẬT MONGODB (collection: server_status)
4. Gửi báo cáo Discord
5. Fix lỗi accounts
```

### 3. Cấu trúc MongoDB

**Database:** `HtechVolam`

**Collections:**
1. `money_monitor` - Lưu thông tin tiền/lợi nhuận
2. `server_status` - Lưu trạng thái máy chủ (dùng cho web monitor)

**Collection `server_status` structure:**
```json
{
  "ten_may": "Tên máy chủ",
  "so_acc_online": 10,
  "so_acc_offline": 2,
  "tong_so_acc": 12,
  "cap_nhat_luc": "2025-10-02T11:30:00",
  "timestamp": "2025-10-02T11:30:00",
  "ngay_tao": "2025-10-02T10:00:00"
}
```

### 4. Web Monitor

**File:** `web_monitor/app.py`

**Cấu hình:**
- Database: `HtechVolam`
- Collection: `server_status` ✅ (Đúng!)
- Offline threshold: 70 phút

**Endpoints:**
- `/` - Trang chủ hiển thị danh sách máy chủ
- `/api/servers` - API lấy danh sách máy chủ (JSON)
- `/api/stats` - API thống kê tổng quan
- `/health` - Health check

## 🧪 Cách test

### Test 1: Kiểm tra kết nối MongoDB
```bash
cd src
python test_mongodb_connection.py
```

Kết quả mong đợi:
- ✅ Kết nối thành công
- ✅ Hiển thị collections hiện có
- ✅ Cập nhật server_status thành công
- ✅ Lấy được thông tin máy chủ

### Test 2: Chạy monitoring
1. Mở autoLogin
2. Chạy "Theo dõi tài khoản"
3. Đợi 1 vòng lặp hoàn thành
4. Kiểm tra log:
   ```
   ✅ Đã cập nhật trạng thái online cho X accounts
   📤 Đang cập nhật thông tin máy chủ lên MongoDB...
   ✅ Đã cập nhật MongoDB thành công!
   ✅ Đã gửi Discord thành công.
   ```

### Test 3: Kiểm tra MongoDB Atlas
1. Vào https://cloud.mongodb.com/
2. Browse Collections
3. Database: `HtechVolam`
4. Collection: `server_status`
5. Kiểm tra có document với tên máy của bạn

### Test 4: Kiểm tra Web Monitor
1. Chạy web monitor local:
   ```bash
   cd web_monitor
   python app.py
   ```
2. Mở http://localhost:5000
3. Kiểm tra hiển thị máy chủ và số accounts

## 📝 Lưu ý

### Khi nào MongoDB được cập nhật?
- ✅ Khi chạy "Theo dõi tài khoản" (realTimeCheckBugAutoVLBS)
- ✅ Khi login xong tất cả accounts (login_manager)

### Collection nào được sử dụng?
- `money_monitor` - Lưu lợi nhuận (từ realTimeCheckBugAutoVLBS)
- `server_status` - Lưu trạng thái máy chủ (cho web monitor)

### Tự động tạo collection
- Nếu collection `server_status` chưa tồn tại, code sẽ tự động tạo
- Nếu máy chủ chưa có trong collection, sẽ thêm mới
- Nếu máy chủ đã có, sẽ cập nhật thông tin

## 🔧 Troubleshooting

### Lỗi: Không kết nối được MongoDB
**Nguyên nhân:**
- Internet không ổn định
- MongoDB URI sai
- IP chưa được whitelist

**Giải pháp:**
1. Kiểm tra internet
2. Verify MongoDB URI trong `src/modules/mongodb_manager.py`
3. Vào MongoDB Atlas → Network Access → Add IP `0.0.0.0/0`

### Lỗi: Web monitor không hiển thị dữ liệu
**Nguyên nhân:**
- Chưa chạy monitoring
- Collection name sai
- MongoDB URI sai trong web_monitor

**Giải pháp:**
1. Chạy monitoring ít nhất 1 lần
2. Kiểm tra collection name = `server_status`
3. Set MONGO_URI environment variable

### Lỗi: Dữ liệu không cập nhật
**Nguyên nhân:**
- Monitoring chưa chạy đến vòng lặp tiếp theo
- Lỗi kết nối MongoDB

**Giải pháp:**
1. Đợi monitoring chạy xong 1 vòng lặp
2. Kiểm tra log có thông báo "✅ Đã cập nhật MongoDB thành công!"
3. Chạy test_mongodb_connection.py để verify

## 🎯 Kết luận

✅ **Hoàn thành:**
- Cập nhật KPI mặc định: 48 Kv/day (1 giờ tăng 2 Kv)
- Thêm cập nhật MongoDB vào realTimeCheckBugAutoVLBS
- Tự động tạo collection nếu chưa có
- Cập nhật hoặc thêm mới thông tin máy chủ
- Web monitor đã lấy đúng collection `server_status`

✅ **Luồng hoạt động:**
```
Monitoring → Cập nhật accounts.json → Cập nhật MongoDB → Gửi Discord
```

✅ **Sẵn sàng sử dụng!**
