import os
import json
import win32api
import win32con
import win32gui
import pyautogui

def load_global_time_sleep(file_path='accounts.json'):
    with open(os.path.join(join_directory_data(), file_path), 'r') as file:
        data = json.load(file)
        return data["sleepTime"][0]["global_time_sleep"]

def load_autoNames(file_path='accounts.json'):
    with open(os.path.join(join_directory_data(), file_path), 'r') as file:
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

def copy_auto_update_path_to_auto_update_path():
    accounts_file = 'accounts.json'
    output_file = 'autoUpdate_path.json'
    # Kiểm tra xem file accounts.json có tồn tại không
    if not os.path.exists(os.path.join(join_directory_data(), accounts_file)):
        print(f"File {accounts_file} không tồn tại.")
        return
    
    # Đọc dữ liệu từ accounts.json
    data = read_json_file(accounts_file)
    
    # Chuẩn bị mảng chỉ chứa auto_update_path từ accounts.json
    auto_update_paths = [account.get("auto_update_path") for account in data.get("accounts", [])]
    
    # Kiểm tra nếu file autoUpdate_path.json đã tồn tại
    if os.path.exists(os.path.join(join_directory_data(), output_file)):
        print(f"File {output_file} đã tồn tại, sẽ ghi đè nội dung.")
    
    # Ghi mảng auto_update_paths vào autoUpdate_path.json
    with open(os.path.join(join_directory_data(), output_file), 'w', encoding='utf-8') as f:
        json.dump({"auto_update_paths": auto_update_paths}, f, ensure_ascii=False, indent=4)
    
    print(f"Sao chép đường dẫn auto_update_path thành công vào {output_file}.")

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