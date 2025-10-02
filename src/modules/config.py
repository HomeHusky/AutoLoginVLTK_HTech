# ===============================
# 📋 CONFIGURATION & CONSTANTS
# ===============================
"""
File chứa tất cả các constants và cấu hình của ứng dụng
Dễ dàng thay đổi và quản lý tập trung
"""

import os

# ================================================================
# 📁 FILE PATHS
# ================================================================

# Version file
VERSION_FILE = "version.txt"

# JSON files
ACCOUNTS_FILE = 'accounts.json'
GLOBAL_TIME_FILE = 'global_time.json'
SERVERS_FILE = 'servers.json'
ACCOUNTS_MONEY_STATUS_FILE = 'accounts_money_status.json'
MONITOR_TIME_FILE = 'monitor_time.json'
GOM_ACCOUNTS_FILE = 'gom_accounts.json'
FIX_WEB_CTCX_FILE = 'fix_web_ctcx.json'
AUTO_UPDATE_FILE = 'autoUpdate_path.json'
FAIL_SERVERS_FILE = 'fail_servers.json'
PASS_MONITOR_FILE = 'pass_monitor.txt'

# ================================================================
# 🌐 URLS
# ================================================================

# GitHub URLs
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/HomeHusky/AutoLoginVLTK_HTech/master/version.txt"
GITHUB_DOWNLOAD_URL = "https://github.com/HomeHusky/AutoLoginVLTK_HTech/archive/refs/heads/master.zip"

# ================================================================
# ⚙️ DEFAULT SETTINGS
# ================================================================

# Default auto names
DEFAULT_AUTO_NAMES = ["vocongtruyenky", "congthanhchienxua", "AutoVLBS"]

# Default auto tool path
DEFAULT_AUTO_TOOL_PATH = "D:/VoLamTruyenKy/AutoVLBS19/TrainJX.exe"

# Default sleep times
DEFAULT_SLEEP_TIME = {
    "wait_time_open": 15,
    "wait_time_open2": 45,
    "wait_time_load": 2,
    "wait_time_server": 8,
    "wait_time_open_trainjx": 3,
    "wait_time_load_autovlbs": 5,
    "try_number": 3,
    "global_time_sleep": 1,
    "hide_effects": 1,
    "start_up": 1
}

# Default monitor settings
DEFAULT_MONITOR_TIME = "5"
DEFAULT_KPI = "48"  # KPI cho tài khoản thường (Kv/day) - 1 giờ tăng 2 Kv
DEFAULT_KPI_GOM = "96"  # KPI cho tài khoản gom tiền (Kv/day) - 1 giờ tăng 4 Kv (gấp đôi)
DEFAULT_TOTAL_SERVERS = "10"
DEFAULT_TITLE_MAIL = "Máy chủ AutoVLBS"

# ================================================================
# 🎨 UI SETTINGS
# ================================================================

# Window settings
WINDOW_TITLE_PREFIX = "Auto Login Htechnology"
WINDOW_GEOMETRY = "1000x750+50+50"
WINDOW_RESIZABLE = (True, True)

# Simple Color Palette - Like Original autoLogin.py
COLOR_PRIMARY = "#5783db"      # Simple blue
COLOR_PRIMARY_HOVER = "#4681f4"  # Lighter blue on hover
COLOR_SUCCESS = "#5783db"      # Same as primary (simple)
COLOR_SUCCESS_HOVER = "#4681f4"  # Same as primary hover
COLOR_DANGER = "#5783db"       # Same as primary (simple)
COLOR_DANGER_HOVER = "#4681f4"   # Same as primary hover
COLOR_WARNING = "#5783db"      # Same as primary (simple)
COLOR_INFO = "#5783db"         # Same as primary (simple)
COLOR_BACKGROUND = "#f0f0f0"   # Light gray background
COLOR_SURFACE = "#ffffff"      # White
COLOR_TEXT = "#000000"         # Black text
COLOR_TEXT_SECONDARY = "#666666"  # Gray text
COLOR_BORDER = "#cccccc"       # Gray border

# Style settings
THEME = 'clam'
BUTTON_PADDING = 8
BUTTON_BACKGROUND = COLOR_PRIMARY
BUTTON_FOREGROUND = "white"
BUTTON_ACTIVE_BACKGROUND = COLOR_PRIMARY_HOVER

LABEL_PADDING = 6
LABEL_FONT = ('Segoe UI', 10)
LABEL_FONT_BOLD = ('Segoe UI', 10, 'bold')

TREEVIEW_HEADING_FONT = ('Segoe UI', 10, 'bold')
TREEVIEW_ROW_HEIGHT = 28

# Tab settings
TAB_PADDING = 15

# ================================================================
# 🔧 SYSTEM SETTINGS
# ================================================================

# PyAutoGUI settings
PYAUTOGUI_FAILSAFE = False

# Boot time threshold (minutes)
BOOT_TIME_THRESHOLD = 2

# Startup delay (milliseconds)
STARTUP_DELAY = 4000

# ================================================================
# 🔐 SECURITY SETTINGS
# ================================================================

# Special password for monitoring
SPECIAL_MONITOR_PASSWORD = '0919562182qQ!'

# ================================================================
# 📊 TREEVIEW COLUMNS
# ================================================================

# Account treeview columns
ACCOUNT_COLUMNS = {
    "stt": {"text": "Stt", "width": 30},
    "is_select": {"text": "Bỏ qua", "width": 50},
    "username": {"text": "Username", "width": 100},
    "ingame": {"text": "Ingame", "width": 100},
    "game_path": {"text": "PathGame", "width": 200},
    "is_logged_in": {"text": "Trạng thái", "width": 60},
    "is_gom_tien": {"text": "Tk gom tiền", "width": 40},
    "is_xe_2": {"text": "Xe 2", "width": 40},
    "so_lan_xuong": {"text": "Số lần xuống cum server", "width": 40},
    "so_lan_xuong2": {"text": "Số lần xuống server", "width": 40}
}

# Money treeview columns
MONEY_COLUMNS = {
    "stt": {"text": "Stt", "width": 50},
    "ingame": {"text": "Tên nv", "width": 100},
    "tong_tien": {"text": "Tổng tiền", "width": 100},
    "thu_nhap": {"text": "Thu nhập", "width": 80},
    "thoi_gian": {"text": "Thời gian", "width": 80},
    "TDP/C": {"text": "TDP/C", "width": 80},
    "ban_do": {"text": "Bản đồ", "width": 80},
    "server": {"text": "Server", "width": 80}
}

# ================================================================
# 📝 MESSAGES
# ================================================================

MESSAGES = {
    "update_available": "Có bản cập nhật mới, bạn có muốn cập nhật?",
    "update_latest": "Bạn đang sử dụng phiên bản mới nhất.",
    "update_success": "Ứng dụng đã được cập nhật thành công. Bắt đầu khởi động lại.",
    "update_failed": "Quá trình cập nhật thất bại: {}",
    
    "login_confirm": "Vui lòng chuyển sang tiếng Anh và tắt CAPS LOCK trước khi bắt đầu. Bạn đã thực hiện chưa?",
    "login_reminder": "Vui lòng thực hiện yêu cầu trước khi tiếp tục.",
    "login_error": "Không thể bắt đầu quá trình đăng nhập: {}",
    "login_stopped": "Dừng đăng nhập thành công.",
    "login_stop_error": "Không thể dừng quá trình đăng nhập: {}",
    
    "account_exists": "Tài khoản đã có trong dữ liệu!",
    "account_deleted": "Đã xoá tài khoản!",
    "account_delete_confirm": "Bạn có chắc chắn muốn xoá tài khoản này?",
    "account_select_to_delete": "Vui lòng chọn tài khoản để xóa!",
    "account_select_editing": "Vui lòng chọn tài khoản đang chỉnh sửa!",
    "account_missing_info": "Vui lòng nhập đủ thông tin!",
    
    "auto_update_confirm": "Thao tác này sẽ chạy tất cả AutoUpdate của các server mà dữ liệu đang có!",
    "auto_update_stopped": "Dừng AutoUpdate thành công!",
    "auto_update_success": "Chạy AutoUpdate thành công!",
    
    "monitor_confirm": "Thao tác này sẽ chạy theo dõi tài khoản của các server mà dữ liệu đang có!",
    "monitor_stopped": "Dừng theo dõi thành công.",
    
    "save_success": "Đã lưu thành công dữ liệu Auto Tool!",
    "refresh_success": "Làm mới thành công.",
    "test_success": "Kiểm tra thành công.",
    
    "error_generic": "Có lỗi xảy ra: {}",
    "file_not_found": "File {} không tồn tại.",
    "path_missing": "Vui lòng nhập đường dẫn tool auto!",
    "server_updated": "Đã cập nhật servers.json thành công!"
}

# ================================================================
# 🎯 HELPER FUNCTIONS
# ================================================================

def get_message(key, *args):
    """
    Lấy message từ dictionary và format nếu cần
    
    Args:
        key: Key của message
        *args: Arguments để format message
    
    Returns:
        str: Message đã được format
    """
    message = MESSAGES.get(key, "")
    if args:
        return message.format(*args)
    return message

def get_column_config(column_type):
    """
    Lấy cấu hình cột cho treeview
    
    Args:
        column_type: 'account' hoặc 'money'
    
    Returns:
        dict: Dictionary chứa cấu hình cột
    """
    if column_type == 'account':
        return ACCOUNT_COLUMNS
    elif column_type == 'money':
        return MONEY_COLUMNS
    return {}
