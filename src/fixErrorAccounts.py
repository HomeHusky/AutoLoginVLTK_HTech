import GlobalFunction as GF
import threading
from pywinauto import Application
import pyautogui
import time

stop_flag = False
global_time_sleep = GF.load_global_time_sleep()

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
    nameAutoVLBS = GF.getNameAutoVLBS()
    GF.checkBothAutoVlbsAndQuanLyRunning(nameAutoVLBS)
    list_control = Application(backend="uia").connect(title_re=nameAutoVLBS).window(title_re=nameAutoVLBS).child_window(control_type="List")
    if not list_control.exists():
        print("Không tìm thấy bảng!")
    else:
        # Tìm các mục trong danh sách và nhấp chuột phải vào mục đầu tiên
        items = list_control.children(control_type="ListItem")
        for item in items:
            countChild = 0
            for child in item.children():
                if countChild == 0:
                    if child.window_text() == account_name:
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
                        pyautogui.write('Htech317@', interval=0.1)
                        time.sleep(global_time_sleep)
                        pyautogui.press('enter')
                        time.sleep(global_time_sleep)
                        pyautogui.press('enter')
                        time.sleep(2)
                        # Sau khi sửa lỗi:
                        pyautogui.hotkey('ctrl', 'g')
                        time.sleep(global_time_sleep)
                        pyautogui.press('esc')
                        time.sleep(global_time_sleep)
                        time.sleep(2)
                        item.type_keys("{SPACE}") # Nhấp space để bật auto game
                        time.sleep(2)
                        item.type_keys("{SPACE}") # Nhấp space để bật auto game
                        item.click_input(double=True) # Nhấp đúp vào mục để ẩn game
                        print(f"✅ Đã sửa lỗi cho tài khoản: {account_name}")
                        return
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