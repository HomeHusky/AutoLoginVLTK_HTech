import subprocess
import pyautogui
import time
import json
import ctypes

from pywinauto import keyboard
import autoClickVLBS
import updateIngame
import GlobalFunction as GF
import os
from pywinauto.keyboard import send_keys
from pywinauto import Desktop
import win32api

pyautogui.FAILSAFE = False

global_time_sleep = GF.load_global_time_sleep()

# Biến cờ để dừng quá trình login
stop_login = False

def disable_mouse():
    ctypes.windll.user32.BlockInput(True)  # Vô hiệu hóa chuột và bàn phím

def enable_mouse():
    ctypes.windll.user32.BlockInput(False)  # Kích hoạt lại chuột và bàn phím

def load_accounts(file_path='accounts.json'):
    with open(os.path.join(GF.join_directory_data(), file_path), 'r') as file:
        data = json.load(file)
        return data['accounts']

def load_auto_tool_path(file_path='accounts.json'):
    with open(os.path.join(GF.join_directory_data(), file_path), 'r') as file:
        data = json.load(file)
        return data['auto_tool_path']

def load_sleepTime(file_path='global_time.json'):
    with open(os.path.join(GF.join_directory_config(), file_path), 'r') as file:
        data = json.load(file)
        return data['sleepTime']

def auto_open_autoVLBS(auto_tool_path, sleepTime):
    try:
        currentAutoName = None
        # try:
        global stop_login
        if stop_login:
            return  # Kiểm tra cờ dừng

        # pyautogui.hotkey('win', 'r')
        # time.sleep(global_time_sleep)
        # pyautogui.write(auto_tool_path)
        # time.sleep(global_time_sleep)
        # pyautogui.press('enter')
        
        working_dir = os.path.dirname(auto_tool_path)

        subprocess.Popen(auto_tool_path, cwd=working_dir)
        time.sleep(sleepTime[0]['wait_time_open_trainjx'])
        if stop_login:
            return  # Kiểm tra cờ dừng
        pyautogui.press('enter')
        time.sleep(sleepTime[0]['wait_time_load_autovlbs'])

        if stop_login:
            return  # Kiểm tra cờ dừng

        auto_names = GF.load_autoNames()
        currentAutoName = GF.checkAutoVlbsBackGroundRunning()
                # currentAutoName = name
        
        # 1. Tìm cửa sổ theo tên
        window = Desktop(backend="win32")[currentAutoName]

        # 2. Lấy kích thước cửa sổ hiện tại
        rect = window.rectangle()
        win_width = rect.width()
        win_height = rect.height()

        # 3. Lấy độ phân giải màn hình
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)

        # 4. Tính vị trí mới: Góc phải trên
        new_left = screen_width - win_width
        new_top = 0

        # 5. Di chuyển cửa sổ
        window.move_window(new_left, new_top, win_width, win_height, repaint=True)
        
        print(f"Đã mở AutoVLBS: {auto_tool_path}")
        # Tắt ứng dụng JXTrain
        GF.close_application("JXTrain")

        # except Exception as e:
        #     print(f"Lỗi khi bật auto!")
        return currentAutoName
    except Exception as e:
        print(f"Lỗi khi mở AutoVLBS: {e}")
        return None

def auto_login(account, sleepTime, currentAutoName, isAutoClickVLBS, isChangeServer):
    global stop_login
    if stop_login:
        return  # Kiểm tra cờ dừng

    # Mở game bằng pyautogui
    # pyautogui.hotkey('win', 'r')
    # time.sleep(global_time_sleep)
    # pyautogui.write(account['game_path'])
    # time.sleep(global_time_sleep)
    # pyautogui.press('enter')

    working_dir = os.path.dirname(account['game_path'])
    
    for attempt in range(3):
        base_length = len(GF.get_all_vpid_vo_lam_windows())
        print(f"Base length of VLTK windows: {base_length}")

        subprocess.Popen(account['game_path'], cwd=working_dir)
        time.sleep(sleepTime[0]['wait_time_open'])
        new_length = len(GF.get_all_vpid_vo_lam_windows())
        print(f"Attempt {attempt + 1}: New length of VLTK windows: {new_length}")
        if new_length > base_length:
            print(f"Đã mở game: {account['game_path']}")
            break
        else:
            print("Lỗi khi mở game:", account['game_path'])
            print(f"Thử lại lần {attempt + 2} để mở game: {account['game_path']}")



    # # Mở game bằng ctypes và os
    # path = account['game_path']
    # ctypes.windll.shell32.ShellExecuteW(None, "runas", path, None, None, 1)

    # time.sleep(sleepTime[0]['wait_time_open'])
    try:
        mo_game_lau = account['mo_game_lau']
        if mo_game_lau:
            print(f"Chờ thêm {sleepTime[0]['wait_time_open2']}s vì server này mở game lâu")
            time.sleep(sleepTime[0]['wait_time_open2'])
    except Exception as e:
        time.sleep(sleepTime[0]['wait_time_open'])


    isOpenExe = GF.checkWindowRunning('Vo Lam Truyen Ky')
    print('isOpenExe:', isOpenExe)
    time.sleep(global_time_sleep)

    if isOpenExe == 0:
        # GF.close_application('Vo Lam Truyen Ky')
        GF.close_visible_vltk_app()
        pyautogui.press('enter')
        time.sleep(global_time_sleep)
        return 3
    else:
        # GF.activate_window('Vo Lam Truyen Ky')
        print("Đã mở game.exe")
        time.sleep(global_time_sleep)

    if stop_login:
        return  # Kiểm tra cờ dừng

    pyautogui.click()
    # pyautogui.press('enter')
    print("Đã nhấn bắt đầu")
    time.sleep(global_time_sleep)
    

    if stop_login:
        return  # Kiểm tra cờ dừng

    pyautogui.press('enter')
    print("Đã nhấn đồng ý ở lần enter 2")
    time.sleep(global_time_sleep)
    

    if stop_login:
        return  # Kiểm tra cờ dừng

    # if isChangeServer:
    #     pyautogui.press('down')

    send_keys("{UP}")
    send_keys("{UP}")
    send_keys("{UP}")
    send_keys("{UP}")

    try:
        solanxuong = int(account['so_lan_xuong'])
        for i in range(solanxuong):
            send_keys("{DOWN}")
    except Exception as e:
        send_keys("{DOWN}")

    send_keys("{RIGHT}")

    try:
        solanxuong2 = int(account['so_lan_xuong2'])
        for i in range(solanxuong2):
            send_keys("{DOWN}")
    except Exception as e:
        print("Acc khong co xuong lan 2")

    pyautogui.press('enter')
    print("Đang đợi server!")

    time.sleep(sleepTime[0]['wait_time_server'])

    pyautogui.write(account['username'])
    pyautogui.press('tab')
    pyautogui.write(account['password'])
    pyautogui.press('enter')

    print("Đã nhập tài khoản mật khẩu!")

    time.sleep(2)
    pyautogui.press('enter')

    time.sleep(sleepTime[0]['wait_time_load'])

    if sleepTime[0]['hide_effects'] == 1:
        pyautogui.hotkey("alt", "f")
        time.sleep(global_time_sleep)
        pyautogui.hotkey("alt", "s")

    InGameName = updateIngame.check_valid_ingame_value(account['username'], currentAutoName)
    if InGameName == False:
        print(f"Có lỗi khi đăng nhập 2: {account['username']}")
        # GF.close_application('Vo Lam Truyen Ky')
        GF.close_visible_vltk_app()
        # pyautogui.press('enter')
        return 2

    if not autoClickVLBS.start_click(account['username'], currentAutoName, isAutoClickVLBS):
        print(f"Account tự tắt sau khi chạy auto")
        return 4
    print(f"Đã đăng nhập vào tài khoản: {account['username']}")
    return 1
    
def reset_all_accounts_login_status():
    """Reset trạng thái is_logged_in của tất cả accounts về False"""
    try:
        filepath = os.path.join(GF.join_directory_data(), 'accounts.json')
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Reset tất cả is_logged_in về False
        for account in data['accounts']:
            account['is_logged_in'] = False
        
        # Lưu lại file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"✅ Đã reset trạng thái login của {len(data['accounts'])} accounts về False")
    except Exception as e:
        print(f"❌ Lỗi reset trạng thái login: {e}")

def runStartLogin(isAutoClickVLBS, callback, currentAutoName, pass_accounts, callback_login):
    GF.minimizeWindow("Auto Login Htech")
    global stop_login
    stop_login = False  # Reset cờ dừng khi bắt đầu
    auto_tool_path = load_auto_tool_path()
    sleepTime = load_sleepTime()
    
    # Chỉ reset trạng thái is_logged_in khi máy vừa khởi động
    from modules.system_manager import system_manager
    if system_manager.is_system_just_booted():
        print("🔄 Máy vừa khởi động, reset trạng thái login của tất cả accounts...")
        reset_all_accounts_login_status()
    else:
        print("ℹ️ Máy đã chạy lâu, giữ nguyên trạng thái login hiện tại")
    
    # Load accounts
    accounts = load_accounts()
    
    # Kiểm tra xem có account nào đã login chưa
    any_account_logged_in = any(account.get('is_logged_in', False) for account in accounts)
    
    # Chỉ mở game fix khi chưa có account nào login
    has_fix_game_server = sleepTime[0].get('has_fix_game_server', 0)
    fix_game_path = sleepTime[0].get('fix_game_path', '')
    
    # if has_fix_game_server and fix_game_path and not any_account_logged_in:
    if has_fix_game_server and fix_game_path:
        print(f"🎮 Phát hiện server fix game, đang mở: {fix_game_path}")
        try:
            # Mở game fix
            subprocess.Popen(fix_game_path)
            print("✅ Đã mở game fix thành công!")
            print("⏳ Chờ 15 giây để game fix khởi động...")
            time.sleep(15)
            
            # Press F5 using pywinauto
            send_keys('{F5}')
            print("Đã nhấn F5 bằng pywinauto")

            # Ẩn cửa sổ game fix
            try:
                # Lấy tên file từ đường dẫn (không có .exe)
                game_name = os.path.basename(fix_game_path).replace('.exe', '')
                print(f"🔍 Đang tìm cửa sổ game: {game_name}")
                
                # Tìm và ẩn cửa sổ
                desktop = Desktop(backend="uia")
                windows = desktop.windows()
                
                for window in windows:
                    try:
                        window_title = window.window_text()
                        # Kiểm tra nếu tên game có trong title
                        if game_name.lower() in window_title.lower():
                            window.minimize()
                            print(f"✅ Đã ẩn cửa sổ game fix: {window_title}")
                            break
                    except:
                        continue
            except Exception as e:
                print(f"⚠️ Không thể ẩn cửa sổ game fix: {e}")
                
        except Exception as e:
            print(f"❌ Lỗi khi mở game fix: {e}")
    elif has_fix_game_server and fix_game_path and any_account_logged_in:
        print(f"ℹ️ Đã có account login, bỏ qua mở game fix")
    
    for account in accounts:
        if account['username'] in pass_accounts:
            continue
        tryLoginNumber = sleepTime[0]['try_number']
        login_success = 0
        isChangedServer = False
        if stop_login:
            break  # Dừng quá trình nếu cờ được đặt
        for i in range(tryLoginNumber):
            # Kiểm tra cờ dừng trong vòng lặp
            if stop_login:
                print("⏸ Đã nhận lệnh dừng, thoát vòng lặp login")
                break
            
            if login_success == 1:
                continue
            if account['is_logged_in'] != True:
                if login_success == 2:
                    if not isChangedServer:
                        isChangedServer = True
                        print(f"Login lần {i+1} và thử lại!")
                        callback_login(account['username'])
                        login_success = auto_login(account, sleepTime, currentAutoName, isAutoClickVLBS, True)
                elif login_success == 3:
                    print(f"Login lần {i+1} vì trước đó không hiện gamme!")
                    callback_login(account['username'])
                    login_success = auto_login(account, sleepTime, currentAutoName, isAutoClickVLBS, False)
                elif login_success == 4:
                    print(f"Login lần {i+1} vì trước đó game tự tắt sau khi chạy auto!")
                    callback_login(account['username'])
                    login_success = auto_login(account, sleepTime, currentAutoName, isAutoClickVLBS, False)
                else:
                    callback_login(account['username'])
                    print(f"Login lần {i+1}")
                    login_success = auto_login(account, sleepTime, currentAutoName, isAutoClickVLBS, False)
            if i == (tryLoginNumber-1):
                if login_success != 1:
                    # add_server_fail_value('fail_servers.json', account['auto_update_path'])
                    print(f"Server failed for account {account['username']}")
        
        # Kiểm tra cờ dừng sau mỗi account
        if stop_login:
            print("⏸ Đã nhận lệnh dừng, thoát khỏi quá trình login")
            break
    print("Hoàn thành login!")
    
    # Gọi callback sau khi hoàn thành
    callback()


def add_server_fail_value(file_path, new_value):
    try:
        # Kiểm tra nếu file không tồn tại hoặc file rỗng
        if not os.path.exists(os.path.join(GF.join_directory_data(), file_path)) or os.stat(os.path.join(GF.join_directory_data(), file_path)).st_size == 0:
            # Tạo file mới với cấu trúc mặc định
            with open(os.path.join(GF.join_directory_data(), file_path), 'w', encoding='utf-8') as file:
                json.dump({"server_fail": []}, file, ensure_ascii=False, indent=4)
            print("File JSON chưa tồn tại hoặc rỗng. Đã tạo file mới với cấu trúc mặc định.")

        # Bước 1: Đọc file JSON
        data = GF.read_json_file(file_path)

        # Bước 2: Thêm giá trị mới vào mảng server_fail
        if "server_fail" in data:
            data["server_fail"].append(new_value)
        else:
            data["server_fail"] = [new_value]  # Tạo mới mảng nếu không tồn tại

        # Bước 3: Ghi lại nội dung đã cập nhật vào file JSON
        with open(os.path.join(GF.join_directory_data(), file_path), 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        print("Đã thêm giá trị vào mảng server_fail thành công!")
        print(data['server_fail'])

    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")

def stop():
    global stop_login
    stop_login = True  # Đặt cờ dừng thành True

# if __name__ == "__main__":
#     runStartLogin()
