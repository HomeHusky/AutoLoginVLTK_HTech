import os
import json
import win32api
import win32con
import re
import win32gui
import win32process
import pyautogui
from pywinauto import Application
import platform
import time

pyautogui.FAILSAFE = False

def load_global_time_sleep(file_path='global_time.json'):
    with open(os.path.join(join_directory_config(), file_path), 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data["sleepTime"][0]["global_time_sleep"]

def load_autoNames(file_path='accounts.json'):
    with open(os.path.join(join_directory_data(), file_path), 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data['autoNames']

def checkQuanlynhanvat():
    try:
        # Hàm callback để kiểm tra từng cửa sổ
        def callback(hwnd, extra):
            # Lấy tiêu đề của cửa sổ
            title = win32gui.GetWindowText(hwnd)
            # Kiểm tra nếu tiêu đề bắt đầu bằng "Quan ly nhan vat"
            if title.startswith("Quan ly nhan vat"):
                extra.append(hwnd)

        # Danh sách để lưu các cửa sổ khớp
        hwnds = []
        # Duyệt qua tất cả các cửa sổ
        win32gui.EnumWindows(callback, hwnds)
        
        # Kiểm tra nếu có cửa sổ nào khớp
        if hwnds:
            print(hwnds)
            return True
        else:
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def checkBothAutoVlbsAndQuanLyRunning(name):
    if checkQuanlynhanvat() and checkWindowRunning(name) == 1:
        close_application("Quan ly nhan vat")
        return True

    return False

def checkWindowRunning(window_name):
    try:
        hwnd = win32gui.FindWindow(None, window_name)
        if hwnd:
            if win32gui.IsWindowVisible(hwnd):
                print(f"{window_name} đang mở và không chạy ẩn.")
                return 1 # cửa sổ
            else:
                print(f"{window_name} đang chạy nền.")
                return 2 # chạy nền
        else:
            print(f"Không tìm thấy cửa sổ {window_name}.")
            return 0
    except Exception as e:
        print(f"Lỗi tìm cửa sổ {window_name}: {e}")
        return 0

def checkAutoVlbsBackGroundRunning():
    auto_names = load_autoNames()
    # try:
    def enum_window_callback(hwnd, result):
        # Lấy tiêu đề cửa sổ
        window_text = win32gui.GetWindowText(hwnd)
        if window_text:
            result.append((hwnd, window_text))

    # Lấy tất cả các cửa sổ hiện tại
    windows = []
    win32gui.EnumWindows(enum_window_callback, windows)

    for name in auto_names:
        # Duyệt qua tất cả các cửa sổ và kiểm tra tiêu đề bắt đầu với 'name'
        for hwnd, window_text in windows:
            if window_text.lower().startswith(name.lower()):
                if window_text.startswith('AutoVLBS 1.3'):
                    close_application(window_text)
                    continue
                # Nếu tìm thấy cửa sổ, khôi phục và đưa nó lên trước
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                print(f"Cửa sổ {window_text} (bắt đầu với {win32gui.GetWindowText(hwnd)}) đã được đưa lên trước.")
                # try:
                # move_window_to_top_right(name)
                # except Exception as e:
                #     print("Không có quyền")
                return win32gui.GetWindowText(hwnd)
        else:
            print(f"Không tìm thấy cửa sổ nào bắt đầu với '{name}'.")
    # except Exception as e:
    #     print("Lỗi dòng 104 hàm checkAutoVlbsBackGroundRunning GlobalFunction.py")
    #     return None
    
    return None

def getNameAutoVLBS():
    if checkQuanlynhanvat():
        close_application("Quan ly nhan vat")

    correct_name = checkAutoVlbsBackGroundRunning()
    return correct_name

def move_window_to_top_right(app_name):
    def enum_windows_callback(hwnd, windows):
        title = win32gui.GetWindowText(hwnd)
        if app_name in title:
            windows.append(hwnd)
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    if windows:
        window = windows[0]
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        x, y, width, height = win32gui.GetWindowRect(window)
        
        # Move the window to the top right corner without resizing
        win32gui.SetWindowPos(window, win32con.HWND_TOP, screen_width - width, 0, width, height, win32con.SWP_NOSIZE)
        return True
    return False

def close_application(app_name):
    def enum_windows_callback(hwnd, windows):
        title = win32gui.GetWindowText(hwnd)
        if title.startswith(app_name):
            windows.append(hwnd)
    
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    
    for hwnd in windows:
        try:
            if win32gui.IsIconic(hwnd):  # Nếu cửa sổ bị thu nhỏ
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # Khôi phục cửa sổ
            
            win32gui.SetForegroundWindow(hwnd)  # Đặt cửa sổ lên foreground
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)  # Gửi thông báo đóng cửa sổ

            if win32gui.GetWindowText(hwnd) == 'AutoVLBS 1.3' or "Vo Lam Truyen Ky":
                # Chờ một chút để popup hiển thị
                pyautogui.sleep(1)  # Điều chỉnh thời gian chờ nếu cần thiết

                # Xác nhận popup bằng cách nhấn Enter
                pyautogui.press('enter')

            print(f"Đã đóng cửa sổ: {win32gui.GetWindowText(hwnd)}")
            return True
        except Exception as e:
            print(f"Không thể đóng cửa sổ: {win32gui.GetWindowText(hwnd)} - Lỗi: {e}")
    
    return False

def is_window_visible(hwnd):
    """Kiểm tra xem cửa sổ có hiển thị hay không."""
    return win32gui.IsWindowVisible(hwnd)

def get_backend():
    """Xác định backend dựa trên kiến trúc hệ thống (32-bit hoặc 64-bit)."""
    architecture = platform.architecture()[0]
    print(f"Hệ thống đang chạy trên kiến trúc: {architecture}")
    return "win32" if architecture == "32bit" else "uia"

def get_visible_vo_lam_windows():
    """Lấy danh sách hwnd của tất cả các cửa sổ 'Vo Lam Truyen Ky' đang hiển thị."""
    hwnds = []

    def enum_windows_callback(hwnd, extra):
        if "Vo Lam Truyen Ky" in win32gui.GetWindowText(hwnd) and is_window_visible(hwnd):
            hwnds.append(hwnd)

    win32gui.EnumWindows(enum_windows_callback, None)
    return hwnds

def get_all_vltk_windows_win32():
    results = []

    def enum_handler(hwnd, _):
        title = win32gui.GetWindowText(hwnd)
        if "Vo Lam Truyen Ky" in title:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            results.append({
                "title": title,
                "handle": hwnd,
                "pid": pid,
                "visible": win32gui.IsWindowVisible(hwnd)
            })

    win32gui.EnumWindows(enum_handler, None)
    return results

def get_all_vpid_vo_lam_windows():
    """Lấy danh sách các cửa sổ 'Vo Lam Truyen Ky' đang hiển thị và trả về danh sách các PID của chúng."""
    windows = get_all_vltk_windows_win32()
    vltk_pids = []
    for w in windows:
        vltk_pids.append(w['pid'])
    return vltk_pids

def get_child_window_text(hwnd):
    """Lấy nội dung của các cửa sổ con (child controls) của cửa sổ popup."""
    texts = []

    def enum_child_windows_callback(child_hwnd, extra):
        text = win32gui.GetWindowText(child_hwnd)
        if text:  # Nếu text không rỗng
            texts.append(text)

    win32gui.EnumChildWindows(hwnd, enum_child_windows_callback, None)
    return texts

def close_visible_vltk_app():
    """Đóng cửa sổ 'Vo Lam Truyen Ky' đang hiển thị và xử lý popup xác nhận."""
    # Bước 1: Lấy danh sách hwnd của cửa sổ chính 'Vo Lam Truyen Ky' đang hiển thị
    initial_hwnds = get_visible_vo_lam_windows()
    if not initial_hwnds:
        print("Không tìm thấy cửa sổ hiển thị nào có tiêu đề 'Vo Lam Truyen Ky'.")
        return
    
    print(f"Danh sách hwnd của cửa sổ chính trước khi đóng: {initial_hwnds}")

    # Bước 2: Đóng tất cả các cửa sổ chính 'Vo Lam Truyen Ky'
    for hwnd in initial_hwnds:
        print(f"Đang đóng cửa sổ chính với hwnd: {hwnd}")
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        print("Parents: ", get_child_window_text(hwnd))
    
    # Đợi để cửa sổ chính đóng và popup xuất hiện
    time.sleep(2)  # Chờ 2 giây để popup xuất hiện

    # Bước 3: Lấy lại danh sách hwnd của tất cả các cửa sổ 'Vo Lam Truyen Ky' hiện tại
    current_hwnds = get_visible_vo_lam_windows()
    print(f"Danh sách hwnd của tất cả các cửa sổ sau khi đóng: {current_hwnds}")

    # Bước 4: Lọc các hwnd của popup (cửa sổ mới, không có trong danh sách ban đầu)
    popup_hwnds = [hwnd for hwnd in current_hwnds if hwnd not in initial_hwnds]
    if not popup_hwnds:
        print("Không tìm thấy popup xác nhận nào.")
        return
    
    print(f"Danh sách hwnd của popup mới xuất hiện: {popup_hwnds}")

    # Bước 5: Xử lý popup xác nhận, tự động nhấn Yes nếu tìm thấy
    for popup_hwnd in popup_hwnds:
        try:
            backend = get_backend()
            print(f"Đang kết nối với hwnd: {popup_hwnd} bằng backend: {backend}")
            app = Application(backend="uia").connect(handle=popup_hwnd)
            popup = app.window(handle=popup_hwnd)
            
            # Kiểm tra nếu message là 'Ban muon thoat khoi Vo Lam Truyen Ky?'
            texts = get_child_window_text(popup_hwnd)
            print("Texts: ", texts==['&Yes', '&No', 'Ban muon thoat  khoi Vo Lam Truyen Ky?'])

            if texts==['&Yes', '&No', 'Ban muon thoat  khoi Vo Lam Truyen Ky?']:
                print(f"Tìm thấy popup xác nhận. Chọn 'Yes' cho hwnd: {popup_hwnd}")
                yes_button = popup.child_window(title="Yes", control_type="Button")
                yes_button.click()
            else:
                print(f"Nội dung của popup không khớp.")
        except Exception as e:
            print(f"Không thể xử lý popup với hwnd {popup_hwnd}: {e}")

def show_application(window_name):
    try:
        hwnd = win32gui.FindWindow(None, window_name)
        if hwnd:
            if win32gui.IsIconic(hwnd):  # Nếu cửa sổ bị thu nhỏ
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # Khôi phục cửa sổ
                print(f"Đã hiện cửa sổ: {win32gui.GetWindowText(hwnd)}")
        else:
            return
    except Exception as e:
        print(f"Lỗi hiện cửa sổ {window_name}: {e}")
        return 0

def activate_window(window_title):
    # Tìm handle của cửa sổ dựa trên tên chính xác
    hwnd = win32gui.FindWindow(None, window_title)
    
    if hwnd:
        # Đặt cửa sổ lên phía trước (active)
        win32gui.SetForegroundWindow(hwnd)
        print(f"Cửa sổ '{window_title}' đã được kích hoạt.")
    else:
        print(f"Không tìm thấy cửa sổ với tiêu đề: {window_title}")

def copy_auto_update_path_to_auto_update_path(json_path_accounts = 'accounts.json', json_path_fail = 'autoUpdate_path.json'):

    with open(os.path.join(join_directory_data(), json_path_fail), 'w', encoding='utf-8') as f:
        f.write('')  # Ghi file trống để xóa dữ liệu

    with open(os.path.join(join_directory_data(), json_path_accounts), 'r', encoding='utf-8') as accounts_file:
        data = json.load(accounts_file)
    
    # Kiểm tra xem file fail_server.json có tồn tại không
    if not os.path.exists(json_path_fail):
        # Tạo file nếu chưa tồn tại
        fail_data = {"auto_update_paths": []}
        with open(os.path.join(join_directory_data(), json_path_fail), 'w', encoding='utf-8') as fail_file:
            json.dump(fail_data, fail_file, ensure_ascii=False, indent=4)
    
    # Đọc file fail_server.json
    with open(os.path.join(join_directory_data(), json_path_fail), 'r', encoding='utf-8') as fail_file:
        fail_data = json.load(fail_file)
    
    # Lấy danh sách server_fail hiện tại
    server_fail_list = fail_data.get("auto_update_paths", [])
    server_online = []
    
    # Duyệt qua từng account và thêm auto_update_path nếu chưa có
    for account in data["accounts"]:
        auto_update_path = account.get("auto_update_path")
        isOnline = account.get("is_logged_in")
        if isOnline == False:
            if auto_update_path not in server_online:
                if auto_update_path and auto_update_path not in server_fail_list:
                    server_fail_list.append(auto_update_path)
        else:
            server_online.append(auto_update_path)
    # Cập nhật lại fail_server.json
    fail_data["auto_update_paths"] = server_fail_list
    with open(os.path.join(join_directory_data(), json_path_fail), 'w', encoding='utf-8') as fail_file:
        json.dump(fail_data, fail_file, ensure_ascii=False, indent=4)
    
    print(f"Sao chép đường dẫn auto_update_path thành công vào {json_path_fail}.")

def copy_auto_update_path_to_fix_web_ctcx_path(json_path_accounts = 'accounts.json', json_path_fail = 'fix_web_ctcx.json'):

    with open(os.path.join(join_directory_data(), json_path_fail), 'w', encoding='utf-8') as f:
        f.write('')  # Ghi file trống để xóa dữ liệu

    with open(os.path.join(join_directory_data(), json_path_accounts), 'r', encoding='utf-8') as accounts_file:
        data = json.load(accounts_file)
    
    # Kiểm tra xem file json_path_fail có tồn tại không
    if not os.path.exists(json_path_fail):
        # Tạo file nếu chưa tồn tại
        fail_data = {"fix_web_ctcx_paths": []}
        with open(os.path.join(join_directory_data(), json_path_fail), 'w', encoding='utf-8') as fail_file:
            json.dump(fail_data, fail_file, ensure_ascii=False, indent=4)
    
    # Đọc file fail_server.json
    with open(os.path.join(join_directory_data(), json_path_fail), 'r', encoding='utf-8') as fail_file:
        fail_data = json.load(fail_file)
    
    # Lấy danh sách server_fail hiện tại
    server_fail_list = fail_data.get("fix_web_ctcx_paths", [])
    server_online = []
    
    # Duyệt qua từng account và thêm auto_update_path nếu chưa có
    for account in data["accounts"]:
        auto_update_path = account.get("auto_update_path")
        isOnline = account.get("is_logged_in")
        if isOnline == False:
            if auto_update_path not in server_online:
                if auto_update_path and auto_update_path not in server_fail_list:
                    server_fail_list.append(auto_update_path)
        else:
            server_online.append(auto_update_path)
    # Cập nhật lại fail_server.json
    fail_data["fix_web_ctcx_paths"] = server_fail_list
    with open(os.path.join(join_directory_data(), json_path_fail), 'w', encoding='utf-8') as fail_file:
        json.dump(fail_data, fail_file, ensure_ascii=False, indent=4)
    
    print(f"Sao chép đường dẫn auto_update_path thành công vào {json_path_fail}.")

def replace_AutoUpdate_to_fix_web_ctcx(file_path='fix_web_ctcx.json'):
    # Đọc nội dung file JSON
    with open(os.path.join(join_directory_data(), file_path), 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Thay đổi "AutoUpdate.exe" thành "fix_web_ctcx"
    data["fix_web_ctcx_paths"] = [path.replace("AutoUpdate.exe", "fix_web_ctcx.bat") for path in data["fix_web_ctcx_paths"]]

    # Ghi lại nội dung đã thay đổi vào file
    with open(os.path.join(join_directory_data(), file_path), 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def check_and_create_json_file(file_path):
    """
    Kiểm tra xem tệp JSON có tồn tại và không rỗng. 
    Nếu không tồn tại hoặc rỗng, tạo một tệp mới với nội dung là {}.
    
    :param file_path: Đường dẫn tới tệp JSON
    """
    if os.path.exists(os.path.join(join_directory_data(), file_path)):
        if os.path.getsize(os.path.join(join_directory_data(), file_path)) == 0:
            print("Tệp rỗng. Tạo tệp mới với nội dung {}.")
            with open(os.path.join(join_directory_data(), file_path), 'w', encoding='utf-8') as file:
                json.dump({}, file)
    else:
        print("Tệp chưa được tạo. Tạo tệp mới với nội dung {}.")
        with open(os.path.join(join_directory_data(), file_path), 'w', encoding='utf-8') as file:
            json.dump({}, file)
            
def read_json_file(file_path):
    data = None
    try:
        with open(os.path.join(join_directory_data(), file_path), 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except UnicodeDecodeError:
        with open(os.path.join(join_directory_data(), file_path), 'r', encoding='latin-1') as f:
            data = json.load(f)
    
    return data

def join_directory_data():
    data_directory = os.path.join(os.path.dirname(__file__), '..\data')
    return data_directory

def read_config_file(file_path):
    data = None
    try:
        with open(os.path.join(join_directory_config(), file_path), 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except UnicodeDecodeError:
        with open(os.path.join(join_directory_config(), file_path), 'r', encoding='latin-1') as f:
            data = json.load(f)
    
    return data

def join_directory_config():
    data_directory = os.path.join(os.path.dirname(__file__), '..\config')
    return data_directory

def hideWindow(partial_title):
    """
    Hides a window based on a partial title match.
    
    Args:
        partial_title (str): The partial title of the window to hide.
    """
    def enum_window_callback(hwnd, titles):
        window_text = win32gui.GetWindowText(hwnd)
        if partial_title.lower() in window_text.lower():
            titles.append(hwnd)
    
    try:
        # Find all windows that match the partial title
        matching_windows = []
        win32gui.EnumWindows(enum_window_callback, matching_windows)
        
        if matching_windows:
            for hwnd in matching_windows:
                win32gui.ShowWindow(hwnd, 0)  # 0 = SW_HIDE (hide the window)
                print(f"Window '{win32gui.GetWindowText(hwnd)}' has been hidden.")
        else:
            print(f"Error: No window with title containing '{partial_title}' found.")
    except Exception as e:
        print(f"Error: Could not hide the window with title containing '{partial_title}'. Reason: {e}")

def minimizeWindow(partial_title):
    """
    Minimizes a window based on a partial title match.
    
    Args:
        partial_title (str): A part of the title of the window to minimize.
    """
    def enum_window_callback(hwnd, titles):
        window_text = win32gui.GetWindowText(hwnd)
        if partial_title.lower() in window_text.lower():
            titles.append(hwnd)
    
    try:
        # Find all windows that match the partial title
        matching_windows = []
        win32gui.EnumWindows(enum_window_callback, matching_windows)
        
        if matching_windows:
            for hwnd in matching_windows:
                win32gui.ShowWindow(hwnd, 6)  # 6 = SW_MINIMIZE (minimize the window)
                print(f"Window '{win32gui.GetWindowText(hwnd)}' has been minimized.")
        else:
            print(f"Error: No window with title containing '{partial_title}' found.")
    except Exception as e:
        print(f"Error: Could not minimize the window with title containing '{partial_title}'. Reason: {e}")

# Hàm gửi tổ hợp phím tới một cửa sổ
def send_alt_key(hwnd, key):
    """Gửi tổ hợp Alt + key tới cửa sổ hwnd"""
    try:
        win32gui.PostMessage(hwnd, win32con.WM_SYSKEYDOWN, key, 0x20000000)
        time.sleep(0.1)
        win32gui.PostMessage(hwnd, win32con.WM_SYSKEYUP, key, 0x20000000)
    except Exception as e:
        print(f"❌ Lỗi gửi phím Alt+{chr(key)} tới hwnd={hwnd}: {e}")

def hide_effects_all():
    def enum_handler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "Vo Lam Truyen Ky" in title or "Vo Lam" in title:  # Tên cửa sổ game
                try:
                    print(f"👉 Đang gửi phím tới cửa sổ: {title} (hwnd={hwnd})")
                    # Alt+F
                    send_alt_key(hwnd, ord('F'))
                    time.sleep(0.5)
                    # Alt+S
                    send_alt_key(hwnd, ord('S'))
                    time.sleep(0.5)
                    print(f"✅ Đã gửi Alt+F và Alt+S tới: {title}")
                except Exception as e:
                    print(f"❌ Lỗi khi xử lý cửa sổ {title}: {e}")

    try:
        win32gui.EnumWindows(enum_handler, None)
        print("🎯 Hoàn tất quá trình ẩn hiệu ứng cho tất cả acc.")
    except Exception as e:
        print(f"❌ Lỗi khi duyệt cửa sổ: {e}")
# Gọi hàm
# accounts_file = 'accounts.json'
# output_file = 'autoUpdate_path.json'
# copy_game_path_to_auto_update_path(accounts_file, output_file)
# print(load_global_time_sleep())
name = 'vocongtruyenky.net'
# if __name__ == "__main__":
#     show_application('vocongtruyenky.net')
    # print(checkBothAutoVlbsAndQuanLyRunning(name))
    # print(checkAutoVlbsBackGroundRunning())
    # checkWindowRunning('Vo Lam Truyen Ky')
    # print(checkQuanlynhanvat())