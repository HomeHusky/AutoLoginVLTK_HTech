# Hướng dẫn Startup với Game Fix

## Cách hoạt động

Khi bạn tick cả 2 options:
1. ✅ **Có server fix game** - Chọn đường dẫn game fix
2. ✅ **Khởi động cùng Window** - Tự động chạy khi khởi động Windows

Hệ thống sẽ tạo 2 shortcuts trong thư mục Startup:

### 1. `0_FixGame.lnk` (Chạy trước)
- Tên bắt đầu bằng `0_` để đảm bảo chạy trước
- Chạy game fix server
- Windows sẽ chạy file này đầu tiên (theo thứ tự alphabet)

### 2. `QuickRun.lnk` (Chạy sau)
- Chạy ứng dụng Auto Login chính
- Chạy sau khi game fix đã khởi động

## Thứ tự khởi động

```
Windows Startup
    ↓
1. 0_FixGame.lnk → Mở game fix server
    ↓
2. QuickRun.lnk → Mở ứng dụng Auto Login
    ↓
3. Ứng dụng tự động login vào game
```

## Cách sử dụng

1. Vào tab **Cài đặt**
2. Tick ✅ **Có server fix game**
3. Click **Browse** và chọn file `.exe` của game fix
4. Tick ✅ **Khởi động cùng Window**
5. Click **Lưu Cài đặt**

## Kiểm tra

Sau khi lưu, bạn có thể kiểm tra:
- Mở thư mục: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`
- Sẽ thấy 2 shortcuts:
  - `0_FixGame.lnk`
  - `QuickRun.lnk`

## Gỡ bỏ

Để gỡ bỏ khỏi startup:
1. Bỏ tick ✅ **Có server fix game** hoặc **Khởi động cùng Window**
2. Click **Lưu Cài đặt**
3. Shortcuts sẽ tự động bị xóa
