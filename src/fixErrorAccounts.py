import GlobalFunction as GF
import threading
from pywinauto import Application
import pyautogui
import time
import os
import json
from pywinauto.keyboard import send_keys
import startLogin as START_LOGIN
import checkStatusAcounts as CHECK_STATUS
import psutil
import win32gui, win32process, ctypes

# WinAPI để kiểm tra app có bị treo không
IsHungAppWindow = ctypes.windll.user32.IsHungAppWindow

def enum_windows_callback(hwnd, result):
    """
    Callback để lấy tất cả hwnd có chứa tiêu đề 'Vo Lam Truyen Ky'
    """
    title = win32gui.GetWindowText(hwnd)
    if "Vo Lam Truyen Ky" in title:
        result.append(hwnd)

def kill_hung_vo_lam():
    """
    Kiểm tra tất cả cửa sổ 'Vo Lam Truyen Ky', 
    nếu cửa sổ nào treo (Hung) thì kill process của nó.
    Trả về danh sách PID đã bị kill.
    """
    hwnd_list = []
    win32gui.EnumWindows(enum_windows_callback, hwnd_list)

    killed_pids = []
    for hwnd in hwnd_list:
        try:
            if IsHungAppWindow(hwnd):  # Kiểm tra treo
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                p = psutil.Process(pid)
                print(f"[!] Treo: {win32gui.GetWindowText(hwnd)} (PID {pid}) -> Đang tắt...")
                p.terminate()  # Tắt tiến trình
                killed_pids.append(pid)
        except Exception as e:
            print(f"Lỗi khi xử lý hwnd {hwnd}: {e}")

    return killed_pids

def run_kill_hung_vo_lam():
    result = kill_hung_vo_lam()
    if result:
        print("Đã tắt các PID:", result)
    else:
        print("Không có cửa sổ nào bị treo.")

stop_flag = False
global_time_sleep = GF.load_global_time_sleep()

def load_accounts(file_path='accounts.json'):
    with open(os.path.join(GF.join_directory_data(), file_path), 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data['accounts']

def load_auto_tool_path(file_path='accounts.json'):
    with open(os.path.join(GF.join_directory_data(), file_path), 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data['auto_tool_path']

def load_sleepTime(file_path='global_time.json'):
    with open(os.path.join(GF.join_directory_config(), file_path), 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data['sleepTime']
    
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

def get_length_online_accounts(file_path='accounts.json'):
    """
    Lấy danh sách các tài khoản đang online từ file JSON.
    :param file_path: Đường dẫn đến file JSON chứa thông tin tài khoản.
    :return: Danh sách các tài khoản đang online.
    """
    full_path = os.path.join(GF.join_directory_data(), file_path)
    with open(full_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        online_accounts = [account for account in data.get('accounts', []) if account.get('is_logged_in')]
    return len(online_accounts)

def get_length_all_accounts(file_path='accounts.json'):
    """
    Lấy tổng số lượng tài khoản từ file JSON.
    :param file_path: Đường dẫn đến file JSON chứa thông tin tài khoản.
    :return: Tổng số lượng tài khoản.
    """
    full_path = os.path.join(GF.join_directory_data(), file_path)
    with open(full_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return len(data.get('accounts', []))

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
        time.sleep(global_time_sleep)
    print("🔧 Hoàn thành sửa lỗi tài khoản.")

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
            app = Application(backend="uia").connect(title_re=nameAutoVLBS)
            dlg = app.window(title_re=nameAutoVLBS)

            # Lấy tất cả control loại List trong cửa sổ
            list_controls = dlg.descendants(control_type="List")

            # Kiểm tra số lượng và lấy theo điều kiện
            if len(list_controls) == 3:
                print("Có 3 List control, lấy cái đầu tiên.")
                list_control = list_controls[2]  # lấy cái đầu tiên
            else:
                list_control = dlg.child_window(control_type="List")  # mặc định nếu chỉ có 1   
            break  # Thoát vòng lặp nếu kết nối thành công
        except Exception as e:
            print(f"Lỗi kết nối đến ứng dụng lần {attempt + 1}: {e}")
            time.sleep(2)

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
                    # pyautogui.hotkey('alt', 'x')
                    # time.sleep(global_time_sleep)
                    # pyautogui.press('enter')
                    # time.sleep(global_time_sleep)
                    # pyautogui.press('enter')
                    # time.sleep(global_time_sleep)
                    # pyautogui.press('enter')
                    # time.sleep(global_time_sleep)
                    # pyautogui.write(get_password_by_ingame(account_name), interval=0.1)
                    # time.sleep(global_time_sleep)
                    # pyautogui.press('enter')
                    # time.sleep(global_time_sleep)
                    # pyautogui.press('enter')
                    time.sleep(2)
                    pyautogui.hotkey('ctrl', 'g')
                    time.sleep(global_time_sleep)
                    pyautogui.press('esc')
                    time.sleep(2)
                    time.sleep(global_time_sleep)
                    # item.type_keys("{SPACE}")
                    # time.sleep(2)
                    item.click_input(double=True) # Nhấp đúp vào mục để ẩn game
                    time.sleep(global_time_sleep)
                    # item.type_keys("{SPACE}")
                    print(f"✅ Đã sửa lỗi cho tài khoản: {account_name}")
                    return
            countChild += 1
    print(f"❌ Không tìm thấy tài khoản: {account_name} trong danh sách.")

def relogin_lost_accounts():
    """
    Đăng nhập lại các tài khoản bị mất kết nối.
    :param lost_accounts_array: Danh sách tài khoản bị mất kết nối.
    """
    print("🔄 Đang kiểm tra và đăng nhập lại các tài khoản bị mất kết nối...")
    relogin_account()

def relogin_account():
    """
    Giả lập việc đăng nhập lại cho tài khoản.
    :param account_name: Tên tài khoản cần đăng nhập lại.
    """
    try:
        auto_tool_path = START_LOGIN.load_auto_tool_path()
        sleepTime = START_LOGIN.load_sleepTime()
        global currentAutoName
        currentAutoName = GF.getNameAutoVLBS()
        CHECK_STATUS.checkStatusAcounts(auto_tool_path, currentAutoName, sleepTime)
        online_accounts = get_length_online_accounts()
        all_accounts = get_length_all_accounts()
        if online_accounts < all_accounts:
            print(f"Đang mới có {online_accounts} acc đang online so với {all_accounts}.")
            run_reLogin(currentAutoName, True)
            CHECK_STATUS.checkStatusAcounts(auto_tool_path, currentAutoName, sleepTime)
            print("Hoàn thành login!")
        else:
            print(f"Tất cả {all_accounts} tài khoản đều đang online.")
        # Giả lập việc đăng nhập lại, ví dụ: mở game và nhập thông tin đăng nhập

    except Exception as e:
        print(f"❌ Lỗi khi đăng nhập lại: {e}")

def run_reLogin(currentAutoName, isAutoClickVLBS):
    """
    Chạy quá trình đăng nhập lại cho các tài khoản bị mất kết nối.
    """
    GF.minimizeWindow("Auto Login Htech")
    global stop_login
    stop_login = False  # Reset cờ dừng khi bắt đầu
    sleepTime = load_sleepTime()
    accounts = load_accounts()
    for account in accounts:
        tryLoginNumber = sleepTime[0]['try_number']
        login_success = 0
        isChangedServer = False
        if stop_login:
            break  # Dừng quá trình nếu cờ được đặt
        for i in range(tryLoginNumber):
            if login_success == 1:
                continue
            if account['is_logged_in'] != True:
                if login_success == 2:
                    if not isChangedServer:
                        isChangedServer = True
                        print(f"Login lần {i+1} và thử lại!")
                elif login_success == 3:
                    print(f"Login lần {i+1} vì trước đó không hiện gamme!")
                elif login_success == 4:
                    print(f"Login lần {i+1} vì trước đó game tự tắt sau khi chạy auto!")
                    login_success = START_LOGIN.auto_login(account, sleepTime, currentAutoName, isAutoClickVLBS, False)
                else:
                    print(f"Login lần {i+1}")
                    login_success = START_LOGIN.auto_login(account, sleepTime, currentAutoName, isAutoClickVLBS, False)
            if i == (tryLoginNumber-1):
                if login_success != 1:
                    # add_server_fail_value('fail_servers.json', account['auto_update_path'])
                    print(f"Server failed for account {account['username']}")
def getLowBoodAccounts():
    """
    Tìm các tài khoản bị mất kết nối vì thấp máu.
    Trả về danh sách các account bị lỗi.
    """
    print("🔍 Đang kiểm tra các tài khoản bị mất kết nối vì thấp máu...")
    list_control = None
    error_accounts = []  # Mảng lưu các tài khoản lỗi

    for attempt in range(3):
        try:
            print(f"Thử kết nối lần {attempt + 1}...")
            # backend = GF.get_backend()
            nameAutoVLBS = GF.getNameAutoVLBS()
            GF.checkBothAutoVlbsAndQuanLyRunning(nameAutoVLBS)
            app = Application(backend="uia").connect(title_re=nameAutoVLBS)
            dlg = app.window(title_re=nameAutoVLBS)

            # Lấy tất cả control loại List trong cửa sổ
            list_controls = dlg.descendants(control_type="List")

            # Kiểm tra số lượng và lấy theo điều kiện
            if len(list_controls) == 3:
                print("Có 3 List control, lấy cái đầu tiên.")
                list_control = list_controls[2]  # lấy cái đầu tiên
            else:
                list_control = dlg.child_window(control_type="List")  # mặc định nếu chỉ có 1   
            break  # Thoát vòng lặp nếu kết nối thành công
        except Exception as e:
            print(f"Lỗi kết nối đến ứng dụng lần {attempt + 1}: {e}")
            time.sleep(2)

    if not list_control:
        print("❌ Không tìm thấy list control.")
        return error_accounts

    # Tìm các mục trong danh sách
    items = list_control.children(control_type="ListItem")
    for i, item in enumerate(items):
        countChild = 0
        account_name = ""
        blood_account = ""
        for child in item.children():
            if countChild == 0:
                account_name = child.window_text()
            elif countChild == 1:
                blood_account = child.window_text()
                if blood_account == "":
                    continue # Bỏ qua nếu máu không hiển thị
                if blood_account != "Boss":
                    try:
                        if int(blood_account) < 900:
                            print(f"⚠️  Tài khoản {account_name} có máu thấp: {blood_account}")
                            error_accounts.append({
                                "account": account_name,
                                "blood": blood_account
                            })
                    except ValueError:
                        print(f"❓ Không parse được máu của {account_name}: {blood_account}")
            countChild += 1

    print("🔧 Hoàn thành kiểm tra. Tổng số acc lỗi:", len(error_accounts))
    return error_accounts
    
def fixLowBloodAccountsWithRepair(prev_errors=None):
    """
    Kiểm tra acc thấp máu.
    - Nếu prev_errors = None → chỉ trả về danh sách lỗi.
    - Nếu prev_errors có giá trị → sẽ sửa lỗi nếu acc vừa bị lỗi và có trong prev_errors.
    """
    print("🔍 Đang kiểm tra các tài khoản bị mất kết nối vì thấp máu...")
    list_control = None
    error_accounts = []  # lưu acc bị lỗi trong lần kiểm tra này

    for attempt in range(3):
        try:
            print(f"Thử kết nối lần {attempt + 1}...")
            nameAutoVLBS = GF.getNameAutoVLBS()
            GF.checkBothAutoVlbsAndQuanLyRunning(nameAutoVLBS)
            app = Application(backend="uia").connect(title_re=nameAutoVLBS)
            dlg = app.window(title_re=nameAutoVLBS)

            # Lấy list control
            list_controls = dlg.descendants(control_type="List")
            if len(list_controls) == 3:
                list_control = list_controls[2]
            else:
                list_control = dlg.child_window(control_type="List")
            break
        except Exception as e:
            print(f"Lỗi kết nối lần {attempt + 1}: {e}")
            time.sleep(2)

    if not list_control:
        print("❌ Không tìm thấy list control.")
        return error_accounts

    # Quét danh sách acc
    items = list_control.children(control_type="ListItem")
    for i, item in enumerate(items):
        account_name, blood_account = "", ""
        for idx, child in enumerate(item.children()):
            if idx == 0:
                account_name = child.window_text()
            elif idx == 1:
                blood_account = child.window_text()

        if blood_account == "" or blood_account == "Boss":
            continue

        try:
            if int(blood_account) < 900:
                print(f"⚠️  Tài khoản {account_name} có máu thấp: {blood_account}")
                error_accounts.append({"account": account_name, "blood": blood_account})

                # Nếu có prev_errors và acc này nằm trong prev_errors → tiến hành sửa
                if prev_errors and any(err["account"] == account_name for err in prev_errors):
                    print(f"🔨 Sửa lỗi cho acc {account_name} (máu {blood_account})")
                    scroll_to_list_item(list_control, i)
                    item.click_input(double=True)  # mở game
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
                    time.sleep(4)
                    time.sleep(global_time_sleep)
                    pyautogui.press('enter')
                    time.sleep(3)
                    pyautogui.hotkey('ctrl', 'g')
                    time.sleep(global_time_sleep)
                    pyautogui.press('esc')
                    time.sleep(2)
                    time.sleep(global_time_sleep)
                    item.click_input(double=True)  # ẩn game
                    time.sleep(global_time_sleep)
                    print(f"✅ Đã sửa lỗi cho acc: {account_name}")
        except ValueError:
            print(f"❓ Không parse được máu của {account_name}: {blood_account}")

    print("🔧 Hoàn thành kiểm tra.")
    return error_accounts


def fixLowBloodAccounts():
    """
    Xử lý các tài khoản bị mất kết nối vì thấp máu.
    """
    print("🔧 Đang xử lý các tài khoản bị mất kết nối vì thấp máu...")
    list_control = None

    for attempt in range(3):
        try:
            print(f"Thử kết nối lần {attempt + 1}...")
            # backend = GF.get_backend()
            nameAutoVLBS = GF.getNameAutoVLBS()
            GF.checkBothAutoVlbsAndQuanLyRunning(nameAutoVLBS)
            app = Application(backend="uia").connect(title_re=nameAutoVLBS)
            dlg = app.window(title_re=nameAutoVLBS)

            # Lấy tất cả control loại List trong cửa sổ
            list_controls = dlg.descendants(control_type="List")

            # Kiểm tra số lượng và lấy theo điều kiện
            if len(list_controls) == 3:
                print("Có 3 List control, lấy cái đầu tiên.")
                list_control = list_controls[2]  # lấy cái đầu tiên
            else:
                list_control = dlg.child_window(control_type="List")  # mặc định nếu chỉ có 1   
            break  # Thoát vòng lặp nếu kết nối thành công
        except Exception as e:
            print(f"Lỗi kết nối đến ứng dụng lần {attempt + 1}: {e}")
            time.sleep(2)

    # Tìm các mục trong danh sách và nhấp chuột phải vào mục đầu tiên
    items = list_control.children(control_type="ListItem")
    for i, item in enumerate(items):
        countChild = 0
        for child in item.children():
            if countChild == 0:
                account_name = child.window_text()
            if countChild == 1:
                blood_account = child.window_text()
                print(f"Máu của tài khoản {account_name} là: {blood_account}")
                if blood_account == "":
                    continue  # Bỏ qua nếu máu không được hiển thị
                if blood_account != "Boss" and int(blood_account) < 900:
                    scroll_to_list_item(list_control, i)
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
                    time.sleep(4)
                    time.sleep(global_time_sleep)
                    pyautogui.press('enter')
                    time.sleep(3)
                    pyautogui.hotkey('ctrl', 'g')
                    time.sleep(global_time_sleep)
                    pyautogui.press('esc')
                    time.sleep(2)
                    time.sleep(global_time_sleep)
                    # item.type_keys("{SPACE}")
                    # time.sleep(2)
                    item.click_input(double=True) # Nhấp đúp vào mục để ẩn game
                    time.sleep(global_time_sleep)
                    # item.type_keys("{SPACE}")
                    print(f"✅ Đã sửa lỗi thấp máu cho tài khoản: {account_name}")
            countChild += 1
    print("🔧 Hoàn thành xử lý các tài khoản bị mất kết nối vì thấp máu.")

def fix_account_stuck_on_map_Sa_Mac():
    """
    Lấy tên bản đồ hiện tại của tài khoản đang hoạt động.
    :return: Tên bản đồ hiện tại.
    """
    try:
        list_control = None
        for attempt in range(3):
            try:
                print(f"Thử kết nối lần {attempt + 1}...")
                list_control = Application(backend="uia").connect(title_re='^Quan ly nhan vat.*').window(title_re='^Quan ly nhan vat.*').child_window(control_type="List")
                print("Kết nối thành công!")
                break  # Nếu kết nối thành công, thoát vòng lặp
            except Exception as e:
                print(f"Lỗi khi kết nối (lần {attempt + 1}): {e}")
                nameAutoVLBS = GF.getNameAutoVLBS()
                if not GF.checkBothAutoVlbsAndQuanLyRunning(nameAutoVLBS):
                    app = Application(backend="uia").connect(title_re=nameAutoVLBS)
                    dlg = app.window(title_re=nameAutoVLBS)

                    # Lấy tất cả control loại List trong cửa sổ
                    list_controls = dlg.descendants(control_type="List")

                    # Kiểm tra số lượng và lấy theo điều kiện
                    if len(list_controls) == 3:
                        print("Có 3 List control, lấy cái đầu tiên.")
                        list_control = list_controls[2]  # lấy cái đầu tiên
                    else:
                        list_control = dlg.child_window(control_type="List")  # mặc định nếu chỉ có 1
                    if not list_control:
                        print("Không tìm thấy bảng!")
                    else:
                        try:
                            list_control.set_focus()
                            list_control.type_keys("{HOME}")
                            time.sleep(0.5)  # Đợi scroll hoàn thành
                        except Exception as e:
                            print(f"Lỗi khi scroll: {str(e)}")
                        # Tìm các mục trong danh sách và nhấp chuột phải vào mục đầu tiên
                        items = list_control.children(control_type="ListItem")
                        if items:
                            items[0].right_click_input()
                        else:
                            print("Không có mục nào trong danh sách!")
                    time.sleep(1)
        # Khởi tạo và sử dụng biến trạng thái kẹt Sa Mạc giữa các lần gọi
        global _prev_stuck_sa_mac_accounts
        try:
            _prev_stuck_sa_mac_accounts
        except NameError:
            _prev_stuck_sa_mac_accounts = set()

        current_stuck_accounts = set()

        items = list_control.children(control_type="ListItem")
        for i, item in enumerate(items):
            account_name = ""
            account_map = ""
            countChild = 0
            for child in item.children():
                if countChild == 1:
                    account_name = child.window_text()
                if countChild == 8:
                    account_map = child.window_text()
                    if account_map.lower().startswith("sa m¹c ®Þa biÓu".lower()):
                        # Đánh dấu là đang kẹt ở Sa Mạc trong lần kiểm tra hiện tại
                        current_stuck_accounts.add(account_name)
                        if account_name in _prev_stuck_sa_mac_accounts:
                            print(f"Account {account_name} vẫn kẹt Sa Mạc ở lần kiểm tra liên tiếp => tiến hành fix")
                            print(f"Account {account_name} đang ở bản đồ Sa mạc Địa Biểu!")
                            scroll_to_list_item(list_control, i)
                            # Nhấp chuột phải vào mục này
                            item.click_input(double=True) # Nhấp đúp vào mục để mở game
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
                            time.sleep(4)
                            time.sleep(global_time_sleep)
                            pyautogui.press('enter')
                            time.sleep(3)
                            pyautogui.hotkey('ctrl', 'g')
                            time.sleep(global_time_sleep)
                            pyautogui.press('esc')
                            time.sleep(2)
                            time.sleep(global_time_sleep)
                            # item.right_click_input()
                            # item.type_keys("{DOWN}")  # 1
                            # item.type_keys("{DOWN}")  # 2
                            # item.type_keys("{DOWN}")  # 3
                            # item.type_keys("{DOWN}")  # 4
                            # item.type_keys("{DOWN}")  # 5
                            # item.type_keys("{DOWN}")  # 6
                            # item.type_keys("{DOWN}")  # 7
                            # pyautogui.press('enter')
                            # time.sleep(2)
                            item.click_input(double=True) # Nhấp đúp vào mục để ẩn game
                            time.sleep(global_time_sleep)
                            # item.right_click_input()
                            # item.type_keys("{DOWN}")  # 1
                            # pyautogui.press('enter')
                            print(f"✅ Đã sửa lỗi kẹt map Sa Mạc cho tài khoản: {account_name}")
                        else:
                            print(f"Phát hiện lần đầu kẹt Sa Mạc: {account_name} -> sẽ kiểm tra lại ở lần kế tiếp trước khi fix")
                countChild += 1

        # Cập nhật trạng thái cho lần kiểm tra tiếp theo
        _prev_stuck_sa_mac_accounts = current_stuck_accounts

        # messagebox.showinfo("Dữ liệu:", gom_accounts_info_data)
    except Exception as e:
        print(f"Lỗi khi kiểm tra tài khoản: {e}")

# # test hàm fixErrorAccounts
# def start_fixing(error_accounts_array):
#     global stop_flag
#     stop_flag = False
#     t = threading.Thread(target=fixErrorAccounts, args=(error_accounts_array,), daemon=True)
#     t.start()
#     print("🔁 Bắt đầu sửa...")

# # test hàm fixLowBloodAccounts
# def start_fixing(error_accounts_array):
#     global stop_flag
#     stop_flag = False
#     t = threading.Thread(target=fixLowBloodAccounts, args=(), daemon=True)
#     t.start()
#     print("🔁 Bắt đầu sửa...")

# # test hàm lấy tên bản đồ hiện tại
# def start_fixing(error_accounts_array):
#     global stop_flag
#     stop_flag = False
#     t = threading.Thread(target=fix_account_stuck_on_map_Sa_Mac, args=(), daemon=True)
#     t.start()
#     print("🔁 Bắt đầu lấy bản đồ...")

# # test hàm relogin_lost_accounts
# def start_fixing(error_accounts_array):
#     global stop_flag
#     stop_flag = False
#     t = threading.Thread(target=relogin_lost_accounts, args=(), daemon=True)
#     t.start()
#     print("🔁 Bắt đầu kiểm tra và relogin!")

# test hàm connect mongodb
def load_title_mail(filepath='monitor_time.json'):
    try:
        with open(os.path.join(GF.join_directory_data(), filepath), 'r', encoding='utf-8') as f:
            data = json.load(f)
            return float(data['title_mail'])
    except FileNotFoundError:
        # Nếu file không tồn tại, trả về giá trị mặc định
        print(f"File {filepath} không tồn tại. Sử dụng giá trị mặc định 1.")
        return 1.0

def load_accounts_data(file_path='accounts.json'):
    with open(os.path.join(GF.join_directory_data(), file_path), 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data
    
def connect_mongodb():
    try:
        import pymongo
        import json
        import os
        from datetime import datetime
        from pymongo.mongo_client import MongoClient
        from pymongo.server_api import ServerApi

        # === 1. Kết nối MongoDB Atlas ===
        mongo_uri = "mongodb+srv://htechvolam:Htech317@htechvolam.oefc26z.mongodb.net/?retryWrites=true&w=majority&appName=HtechVolam"
        # Create a new client and connect to the server
        client = MongoClient(mongo_uri)
        client.admin.command('ping')
        print("✅ Kết nối MongoDB thành công!")
        db = client["HtechVolam"]
        collection = db["tai_khoan_may"]

        # === 3. Load dữ liệu từ file ===
        ten_may = int(load_title_mail())
        new_data = load_accounts_data()
        new_accounts = new_data.get("accounts", [])

        # === 4. Tìm document theo tên máy và group ===
        existing_doc = collection.find_one({"ten_may": ten_may})

        if existing_doc:
            print(f"🔁 Đã có dữ liệu máy {ten_may}. Đang cập nhật...")

            # Lấy danh sách username hiện có
            existing_usernames = {acc["username"] for acc in existing_doc.get("accounts", [])}

            # Lọc ra những account mới chưa có
            new_unique_accounts = [acc for acc in new_accounts if acc["username"] not in existing_usernames]

            if new_unique_accounts:
                # Cập nhật thêm account mới vào mảng accounts
                collection.update_one(
                    {"_id": existing_doc["_id"]},
                    {"$push": {"accounts": {"$each": new_unique_accounts}}}
                )
                print(f"✅ Đã thêm {len(new_unique_accounts)} account mới vào máy {ten_may}.")
            else:
                print("✅ Không có account mới để thêm.")

        else:
            # Chưa có thì thêm mới toàn bộ
            new_data["ten_may"] = ten_may
            new_data["ngay"] = datetime.now()
            collection.insert_one(new_data)
            print(f"✅ Đã thêm mới máy {ten_may}.")

    except Exception as e:
        print(f"❌ Lỗi kết nối MongoDB: {e}")

# # test hàm connect mongodb
# def start_fixing(error_accounts_array):
#     global stop_flag
#     stop_flag = False
#     t = threading.Thread(target=connect_mongodb, args=(), daemon=True)
#     t.start()
#     print("🔁 Bắt đầu sửa...")

def start_fixing(error_accounts_array):
    global stop_flag
    stop_flag = False
    t = threading.Thread(target=run_kill_hung_vo_lam, args=(), daemon=True)
    t.start()
    print("🔁 Bắt đầu sửa...")

def stop_fixing():
    global stop_flag
    stop_flag = True
    print("⛔ Yêu cầu dừng sửa.")

if __name__ == "__main__":
    connect_mongodb()