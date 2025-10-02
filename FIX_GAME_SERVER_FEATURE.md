# 🎮 Tính năng Server Fix Game

## ✅ Đã hoàn thành

### 1. **Thêm UI trong tab Quản lý Đường dẫn**

**File:** `src/tabs/tab_path_manager.py`

**Các thành phần UI:**
- ✅ Checkbox "Có server fix game" (row 14)
- ✅ Entry "Đường dẫn game fix" (row 15) - Disable mặc định
- ✅ Button "Browse" để chọn file game fix - Disable mặc định

**Logic UI:**
- Khi tick checkbox → Enable entry và button browse
- Khi bỏ tick → Disable entry và button browse
- Khi click Browse → Mở dialog chọn file .exe

### 2. **Lưu/Load cấu hình**

**Lưu vào:** `config/global_time.json` trong `sleepTime[0]`

**Cấu trúc dữ liệu:**
```json
{
  "sleepTime": [{
    ...
    "has_fix_game_server": 1,
    "fix_game_path": "D:/path/to/fix_game.exe"
  }]
}
```

**Hàm đã thêm:**
- `on_fix_game_checkbox_change()` - Xử lý khi thay đổi checkbox
- `browse_fix_game_path()` - Chọn file game fix
- Cập nhật `save_auto_data()` - Lưu cấu hình
- Cập nhật `load_auto_data()` - Load cấu hình

### 3. **Logic Login**

**File:** `src/startLogin.py`

**Luồng hoạt động:**
```
1. Bắt đầu login (runStartLogin)
2. Load sleepTime từ global_time.json
3. Kiểm tra has_fix_game_server
4. Nếu có tick và có đường dẫn:
   - Mở game fix bằng subprocess.Popen()
   - Chờ 5 giây để game khởi động
5. Tiếp tục login bình thường
```

**Code đã thêm:**
```python
# Kiểm tra và mở game fix nếu có
has_fix_game_server = sleepTime[0].get('has_fix_game_server', 0)
fix_game_path = sleepTime[0].get('fix_game_path', '')

if has_fix_game_server and fix_game_path:
    print(f"🎮 Phát hiện server fix game, đang mở: {fix_game_path}")
    try:
        subprocess.Popen(fix_game_path)
        print("✅ Đã mở game fix thành công!")
        print("⏳ Chờ 5 giây để game fix khởi động...")
        time.sleep(5)
    except Exception as e:
        print(f"❌ Lỗi khi mở game fix: {e}")
```

## 📋 Hướng dẫn sử dụng

### Bước 1: Cấu hình
1. Mở tab "Quản lý Đường dẫn"
2. Tick vào checkbox "Có server fix game"
3. Click "Browse" và chọn file game fix (ví dụ: `game.exe`)
4. Click "Lưu Cài đặt"

### Bước 2: Login
1. Khi click "Bắt đầu đăng nhập"
2. Hệ thống sẽ:
   - Tự động mở game fix trước
   - Chờ 5 giây
   - Tiếp tục login các accounts bình thường

### Bước 3: Kiểm tra log
Khi login, bạn sẽ thấy log:
```
🎮 Phát hiện server fix game, đang mở: D:/path/to/fix_game.exe
✅ Đã mở game fix thành công!
⏳ Chờ 5 giây để game fix khởi động...
```

## 🔧 Chi tiết kỹ thuật

### Files đã sửa đổi

1. **`src/tabs/tab_path_manager.py`**
   - Thêm biến `self.varHasFixGameServer`
   - Thêm UI components (rows 14-15)
   - Thêm hàm `on_fix_game_checkbox_change()`
   - Thêm hàm `browse_fix_game_path()`
   - Cập nhật `save_auto_data()` để lưu config
   - Cập nhật `load_auto_data()` để load config

2. **`src/startLogin.py`**
   - Thêm logic kiểm tra `has_fix_game_server`
   - Thêm logic mở game fix bằng `subprocess.Popen()`
   - Thêm delay 5 giây sau khi mở game

### Cấu trúc dữ liệu

**File:** `config/global_time.json`
```json
{
  "sleepTime": [
    {
      "wait_time_open": 15,
      "wait_time_open2": 45,
      "wait_time_load": 2,
      "wait_time_server": 8,
      "wait_time_open_trainjx": 3,
      "wait_time_load_autovlbs": 5,
      "try_number": 3,
      "global_time_sleep": 1,
      "hide_effects": 1,
      "start_up": 0,
      "has_fix_game_server": 1,
      "fix_game_path": "D:/VoLamTruyenKy/FixGame/game.exe"
    }
  ]
}
```

## ⚙️ Tùy chỉnh

### Thay đổi thời gian chờ
Mặc định: 5 giây

Để thay đổi, sửa trong `startLogin.py`:
```python
time.sleep(5)  # Đổi thành số giây mong muốn
```

### Thêm tham số khi mở game
Nếu cần truyền tham số cho game fix:
```python
subprocess.Popen([fix_game_path, "--param1", "value1"])
```

### Kiểm tra game đã mở chưa
Có thể thêm logic kiểm tra process:
```python
import psutil

def is_game_running(game_name):
    for proc in psutil.process_iter(['name']):
        if game_name.lower() in proc.info['name'].lower():
            return True
    return False
```

## 🐛 Troubleshooting

### Lỗi: Game fix không mở
**Nguyên nhân:**
- Đường dẫn sai
- File không tồn tại
- Thiếu quyền thực thi

**Giải pháp:**
1. Kiểm tra đường dẫn có đúng không
2. Chạy thử file game fix thủ công
3. Chạy autoLogin với quyền Administrator

### Lỗi: Game fix mở nhưng login vẫn lỗi
**Nguyên nhân:**
- Game fix chưa khởi động xong trong 5 giây

**Giải pháp:**
- Tăng thời gian chờ trong code (từ 5 lên 10 giây)

### Checkbox không hiển thị
**Nguyên nhân:**
- Chưa reload UI

**Giải pháp:**
- Đóng và mở lại ứng dụng

## 📊 Version

- **Version:** 2.1
- **Ngày thêm:** 2025-10-02
- **Tính năng:** Server Fix Game Support

## 🎯 Tương lai

Có thể mở rộng:
- ✨ Thêm nhiều game fix (danh sách)
- ✨ Tự động phát hiện game fix đã chạy
- ✨ Cấu hình thời gian chờ trong UI
- ✨ Log chi tiết hơn về trạng thái game fix
