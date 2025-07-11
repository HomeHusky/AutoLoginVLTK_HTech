import GlobalFunction as GF
import threading
from pywinauto import Application
import pyautogui
import time
import os
import json
from pywinauto.keyboard import send_keys

stop_flag = False
global_time_sleep = GF.load_global_time_sleep()

def scroll_to_list_item(list_control, index):
    list_items = list_control.children(control_type="ListItem")
    if index < 0 or index >= len(list_items):
        print("❌ Index không hợp lệ.")
        return

    target_item = list_items[index]

    # Dùng keyboard để cuộn đến item
    list_control.set_focus()
    list_control.type_keys("{HOME}")
    
    # Cuộn xuống đến đúng dòng
    for _ in range(index):
        send_keys("{DOWN}")
        time.sleep(0.05)

    # Khi đã hiển thị trên màn hình, click vào item
    target_item.click_input()

def get_account_by_ingame(ingame_name, file_path='accounts.json'):

    full_path = os.path.join(GF.join_directory_data(), file_path)
    with open(full_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for account in data.get('accounts', []):
            if account.get('ingame') == ingame_name:
                return account
    return None  # Không tìm thấy

def get_password_by_ingame(ingame_name, file_path='accounts.json'):

    full_path = os.path.join(GF.join_directory_data(), file_path)
    with open(full_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for account in data.get('accounts', []):
            if account.get('ingame') == ingame_name:
                return account.get('password')
    return None 

def fixErrorAccounts(error_accounts_array):
    """
    Sửa lỗi tài khoản bị lỗi game.
    :param error_accounts_array: Danh sách tài khoản bị lỗi.
    """
    print("🔧 Đang sửa lỗi tài khoản...")
    for account in error_accounts_array:
        account_name = account['account']
        # Thực hiện các bước sửa lỗi cho tài khoản
        print(f"🔧 Đang sửa lỗi cho tài khoản: {account_name}")
        # Giả sử có một hàm đăng nhập lại hoặc sửa lỗi cụ thể
        fix_account(account_name)

def fix_account(account_name):
    """
    Giả lập việc sửa lỗi cho tài khoản.
    :param account_name: Tên tài khoản cần sửa lỗi.
    """
    list_control = None

    for attempt in range(3):
        try:
            print(f"Thử kết nối lần {attempt + 1}...")
            # backend = GF.get_backend()
            nameAutoVLBS = GF.getNameAutoVLBS()
            GF.checkBothAutoVlbsAndQuanLyRunning(nameAutoVLBS)
            list_control = Application(backend="uia").connect(title_re=nameAutoVLBS).window(title_re=nameAutoVLBS).child_window(control_type="List")
            break  # Thoát vòng lặp nếu kết nối thành công
        except Exception as e:
            print(f"Lỗi kết nối đến ứng dụng lần {attempt + 1}: {e}")
            time.sleep(2)
    if not list_control.exists():
        print("Không tìm thấy bảng!")
        return
    # Tìm các mục trong danh sách và nhấp chuột phải vào mục đầu tiên
    items = list_control.children(control_type="ListItem")
    for i, item in enumerate(items):
        countChild = 0
        for child in item.children():
            if countChild == 0:
                if child.window_text() == account_name:
                    scroll_to_list_item(list_control, i)
                    print(f"Đã tìm thấy tài khoản: {account_name}")
                    print(f"Đang sửa lỗi cho tài khoản: {account_name}")
                    # Nhấp chuột phải vào mục này
                    item.click_input(double=True) # Nhấp đúp vào mục để mở game
                    # Giả lập việc sửa lỗi, ví dụ: đăng nhập lại
                    # Thực hiện các bước sửa lỗi cụ thể tại đây
                    # Ví dụ: gọi hàm đăng nhập lại hoặc thực hiện thao tác khác
                    pyautogui.hotkey('alt', 'x')
                    time.sleep(global_time_sleep)
                    pyautogui.press('enter')
                    time.sleep(global_time_sleep)
                    pyautogui.press('enter')
                    time.sleep(global_time_sleep)
                    pyautogui.press('enter')
                    time.sleep(global_time_sleep)
                    pyautogui.write(get_password_by_ingame(account_name), interval=0.1)
                    time.sleep(global_time_sleep)
                    pyautogui.press('enter')
                    time.sleep(global_time_sleep)
                    pyautogui.press('enter')
                    time.sleep(2)
                    pyautogui.hotkey('ctrl', 'g')
                    time.sleep(global_time_sleep)
                    pyautogui.press('esc')
                    time.sleep(2)
                    time.sleep(global_time_sleep)
                    item.type_keys("{SPACE}")
                    time.sleep(2)
                    item.click_input(double=True) # Nhấp đúp vào mục để ẩn game
                    time.sleep(global_time_sleep)
                    item.type_keys("{SPACE}")
                    print(f"✅ Đã sửa lỗi cho tài khoản: {account_name}")
                    return
            countChild += 1
    print(f"Không tìm thấy tài khoản: {account_name} trong danh sách.")

def relogin_lost_accounts(lost_accounts_array):
    """
    Đăng nhập lại các tài khoản bị mất kết nối.
    :param lost_accounts_array: Danh sách tài khoản bị mất kết nối.
    """
    print("🔄 Đang đăng nhập lại các tài khoản bị mất kết nối...")
    for account in lost_accounts_array:
        account_name = account['account']
        # Thực hiện các bước đăng nhập lại cho tài khoản
        print(f"🔄 Đang đăng nhập lại cho tài khoản: {account_name}")
        # Giả sử có một hàm đăng nhập lại
        relogin_account(account_name)

def relogin_account(account_name):
    """
    Giả lập việc đăng nhập lại cho tài khoản.
    :param account_name: Tên tài khoản cần đăng nhập lại.
    """

def start_fixing(error_accounts_array):
    global stop_flag
    stop_flag = False
    t = threading.Thread(target=fixErrorAccounts, args=(error_accounts_array,), daemon=True)
    t.start()
    print("🔁 Bắt đầu sửa...")

def stop_fixing():
    global stop_flag
    stop_flag = True
    print("⛔ Yêu cầu dừng sửa.")

if __name__ == "__main__":
    fix_account()