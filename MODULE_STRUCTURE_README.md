# 🏗️ KIẾN TRÚC MODULE HÓA - VERSION 2.0

## 📋 Tổng quan

Version 2.0 áp dụng kiến trúc **module hóa chuyên nghiệp**, tách biệt hoàn toàn logic nghiệp vụ khỏi UI, giúp code:
- ✅ Dễ bảo trì
- ✅ Dễ test
- ✅ Dễ mở rộng
- ✅ Tái sử dụng cao
- ✅ Tuân thủ SOLID principles

## 📁 Cấu trúc thư mục

```
src/
├── autoLogin.py                    # File gốc (backup)
├── autoLogin_refactored.py         # Version 1.0 (tách tabs)
├── autoLogin_v2.py                 # Version 2.0 (module hóa) ⭐ CHẠY FILE NÀY
│
├── modules/                        # 📦 Thư mục chứa các module nghiệp vụ
│   ├── __init__.py
│   ├── config.py                   # Constants & Configuration
│   ├── data_manager.py             # Quản lý dữ liệu JSON
│   ├── version_manager.py          # Quản lý version & update
│   ├── login_manager.py            # Quản lý login & authentication
│   ├── auto_update_manager.py      # Quản lý auto update servers
│   └── system_manager.py           # Quản lý system & startup
│
└── tabs/                           # 🎨 Thư mục chứa các tab UI
    ├── __init__.py
    ├── tab_account_manager.py      # Tab Quản lý Tài khoản
    ├── tab_path_manager.py         # Tab Quản lý Đường dẫn
    └── tab_status_manager.py       # Tab Quản lý Trạng thái
```

## 🔧 Chi tiết các Module

### 1. **config.py** - Configuration Module
**Mục đích**: Tập trung tất cả constants và cấu hình

**Chứa**:
- File paths (JSON files, version file, etc.)
- URLs (GitHub, API endpoints)
- Default settings (sleep times, auto names, etc.)
- UI settings (window size, colors, fonts)
- Treeview columns configuration
- Messages templates

**Ưu điểm**:
- Thay đổi config ở 1 chỗ, áp dụng toàn bộ app
- Dễ quản lý và maintain
- Tránh hard-code values

**Sử dụng**:
```python
from modules.config import ACCOUNTS_FILE, get_message

# Lấy message
msg = get_message("login_confirm")

# Lấy column config
columns = get_column_config('account')
```

---

### 2. **data_manager.py** - Data Management Module
**Mục đích**: Quản lý tất cả thao tác đọc/ghi dữ liệu JSON

**Chức năng chính**:
- ✅ Load/Save accounts data
- ✅ CRUD operations cho accounts
- ✅ Load/Save global time settings
- ✅ Load/Save servers data
- ✅ Cache mechanism
- ✅ Singleton pattern

**API Methods**:
```python
from modules.data_manager import data_manager

# Accounts
accounts = data_manager.get_all_accounts()
account = data_manager.get_account_by_username("user123")
data_manager.add_account(account_data)
data_manager.update_account("user123", new_data)
data_manager.delete_account("user123")
data_manager.account_exists("user123", "path/to/game")

# Status
is_logged_in = data_manager.all_accounts_logged_in()
data_manager.update_account_login_status("user123", True)

# Global Time
sleep_time = data_manager.get_sleep_time()
data_manager.save_global_time(time_data)

# Servers
servers = data_manager.get_servers_list()
data_manager.update_server_path("server1", "new/path")
```

**Ưu điểm**:
- Tách biệt data logic khỏi UI
- Dễ test (mock data)
- Dễ thay đổi storage (từ JSON sang DB)
- Singleton đảm bảo consistency

---

### 3. **version_manager.py** - Version & Update Module
**Mục đích**: Quản lý version và update ứng dụng

**Chức năng chính**:
- ✅ Get current version
- ✅ Get latest version from GitHub
- ✅ Compare versions
- ✅ Download update
- ✅ Extract update
- ✅ Apply update
- ✅ Cleanup temp files
- ✅ Restart app

**API Methods**:
```python
from modules.version_manager import version_manager

# Version
current = version_manager.get_current_version()
latest = version_manager.get_latest_version()
comparison = version_manager.compare_versions(current, latest)

# Update
has_update, version = version_manager.check_for_update(show_ui=True)
success = version_manager.download_and_update()
version_manager.restart_app()

# High-level
if version_manager.update_app(show_messages=True):
    version_manager.restart_app()

# Force update
if version_manager.force_update(show_messages=True):
    version_manager.restart_app()
```

**Ưu điểm**:
- Tách biệt update logic
- Dễ test từng bước
- Có thể reuse cho app khác
- Error handling tốt

---

### 4. **login_manager.py** - Login & Authentication Module
**Mục đích**: Quản lý quá trình login

**Chức năng chính**:
- ✅ Check Auto VLBS status
- ✅ Start/Stop login
- ✅ Login callbacks
- ✅ Check all accounts logged in
- ✅ Thread management
- ✅ Pass monitor

**API Methods**:
```python
from modules.login_manager import login_manager

# Status
is_running = login_manager.check_auto_vlbs_status(try_count=1)
all_logged = login_manager.all_accounts_logged_in()
auto_name = login_manager.get_current_auto_name()

# Login
login_manager.start_login(
    is_auto_click_vlbs=True,
    pass_accounts=["user1", "user2"],
    show_confirm=True
)
login_manager.stop_login()

# Callbacks
login_manager.set_on_login_complete_callback(my_callback)
login_manager.set_on_login_username_callback(username_callback)

# Config
login_manager.reload_config()
```

**Ưu điểm**:
- Tách biệt login logic
- Thread-safe
- Callback pattern linh hoạt
- Dễ test và debug

---

### 5. **auto_update_manager.py** - Auto Update Servers Module
**Mục đích**: Quản lý auto update các servers

**Chức năng chính**:
- ✅ Run all auto updates
- ✅ Stop auto update
- ✅ Run fix web updates
- ✅ Run executable files
- ✅ Thread management
- ✅ Callbacks

**API Methods**:
```python
from modules.auto_update_manager import auto_update_manager

# Update
auto_update_manager.run_all_auto_update(show_confirm=True)
auto_update_manager.stop_auto_update()

# Status
is_running = auto_update_manager.is_update_running()
status = auto_update_manager.get_status()  # "running", "stopping", "stopped"

# Callbacks
auto_update_manager.set_on_success_callback(success_callback)
auto_update_manager.set_on_error_callback(error_callback)
```

**Ưu điểm**:
- Tách biệt auto update logic
- Thread-safe
- Error handling tốt
- Dễ mở rộng

---

### 6. **system_manager.py** - System & Startup Module
**Mục đích**: Quản lý system và startup

**Chức năng chính**:
- ✅ Get boot time & uptime
- ✅ Check if just booted
- ✅ Enable/Disable startup
- ✅ Get system info
- ✅ Process management
- ✅ Shortcut management

**API Methods**:
```python
from modules.system_manager import system_manager

# Boot time
boot_time = system_manager.get_boot_time()
uptime = system_manager.get_uptime()
just_booted = system_manager.is_system_just_booted(threshold_minutes=2)

# Startup
is_enabled = system_manager.is_startup_enabled()
system_manager.enable_startup()
system_manager.disable_startup()
system_manager.set_startup(enable=True)

# System info
info = system_manager.get_system_info()
system_manager.print_system_info()

# Process
is_running = system_manager.is_process_running("game.exe")
count = system_manager.get_process_count("game.exe")
killed = system_manager.kill_process("game.exe")
```

**Ưu điểm**:
- Tách biệt system logic
- Dễ test
- Reusable
- Cross-platform ready

---

## 🎨 Tabs (UI Layer)

### 1. **tab_account_manager.py**
- Quản lý UI cho tab Tài khoản
- Sử dụng `data_manager` để CRUD
- Callbacks cho login

### 2. **tab_path_manager.py**
- Quản lý UI cho tab Đường dẫn
- Sử dụng `data_manager` và `system_manager`
- Cấu hình startup

### 3. **tab_status_manager.py**
- Quản lý UI cho tab Trạng thái
- Monitor tiền vạn
- Gom accounts

---

## 🚀 Cách sử dụng

### **Chạy ứng dụng:**

```bash
# Version 2.0 (Module hóa)
python src/autoLogin_v2.py
```

### **Import và sử dụng modules:**

```python
# Import modules
from modules.data_manager import data_manager
from modules.login_manager import login_manager
from modules.version_manager import version_manager

# Sử dụng
accounts = data_manager.get_all_accounts()
login_manager.start_login(is_auto_click_vlbs=True)
version_manager.update_app()
```

---

## 💡 Ưu điểm của kiến trúc mới

### **1. Separation of Concerns**
- UI tách biệt khỏi Logic
- Mỗi module có 1 nhiệm vụ rõ ràng

### **2. Testability**
- Dễ test từng module độc lập
- Mock data dễ dàng

### **3. Maintainability**
- Sửa 1 module không ảnh hưởng module khác
- Code rõ ràng, dễ đọc

### **4. Reusability**
- Modules có thể dùng cho project khác
- Không phụ thuộc vào UI

### **5. Scalability**
- Dễ thêm tính năng mới
- Dễ refactor

### **6. SOLID Principles**
- Single Responsibility
- Open/Closed
- Dependency Inversion

---

## 📊 So sánh các version

| Tiêu chí | Original | V1.0 (Tabs) | V2.0 (Modules) |
|----------|----------|-------------|----------------|
| Số files | 1 (1824 dòng) | 5 files | 10 files |
| Tách UI/Logic | ❌ | Một phần | ✅ Hoàn toàn |
| Testability | ❌ Khó | ⚠️ Trung bình | ✅ Dễ |
| Reusability | ❌ Không | ⚠️ Tabs only | ✅ Cao |
| Maintainability | ❌ Khó | ⚠️ Khá | ✅ Dễ |
| Scalability | ❌ Khó | ⚠️ Khá | ✅ Dễ |
| SOLID | ❌ | ⚠️ | ✅ |

---

## 🔄 Migration Path

### **Từ Original → V2.0:**

1. **Backup file gốc**
2. **Chạy V2.0** để test
3. **Nếu OK**, update `quick_run.vbs`:
   ```vbs
   WshShell.Run """" & pythonPath & """ """ & scriptDir & "\src\autoLogin_v2.py""", 7, False
   ```

### **Rollback nếu cần:**
```vbs
WshShell.Run """" & pythonPath & """ """ & scriptDir & "\src\autoLogin.py""", 7, False
```

---

## 🎯 Best Practices

### **1. Sử dụng Singleton instances:**
```python
from modules.data_manager import data_manager  # Đã là singleton
```

### **2. Sử dụng config:**
```python
from modules.config import ACCOUNTS_FILE, get_message
```

### **3. Error handling:**
```python
try:
    data_manager.add_account(account_data)
except Exception as e:
    print(f"Error: {e}")
```

### **4. Callbacks:**
```python
login_manager.set_on_login_complete_callback(my_callback)
```

---

## 📝 TODO - Mở rộng tương lai

- [ ] Thêm logging module
- [ ] Thêm database support
- [ ] Thêm API module
- [ ] Thêm testing suite
- [ ] Thêm documentation generator
- [ ] Thêm CI/CD pipeline

---

## 🎉 Kết luận

Version 2.0 mang lại:
- ✅ **Code chuyên nghiệp hơn**
- ✅ **Dễ bảo trì hơn nhiều**
- ✅ **Dễ mở rộng**
- ✅ **Dễ test**
- ✅ **Tái sử dụng cao**

**Đây là kiến trúc production-ready, phù hợp cho dự án lớn!** 🚀
