import subprocess
import pyautogui
import time
import json
import ctypes
import autoClickVLBS
import updateIngame
import GlobalFunction as GF
import os

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

def load_sleepTime(file_path='accounts.json'):
    with open(os.path.join(GF.join_directory_data(), file_path), 'r') as file:
        data = json.load(file)
        return data['sleepTime']

def auto_open_autoVLBS(auto_tool_path, sleepTime):
    currentAutoName = None
    # try:
    global stop_login
    if stop_login:
        return  # Kiểm tra cờ dừng

    pyautogui.hotkey('win', 'r')
    time.sleep(global_time_sleep)
    pyautogui.write(auto_tool_path)
    time.sleep(global_time_sleep)
    pyautogui.press('enter')
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
    
    print(f"Đã mở AutoVLBS: {auto_tool_path}")
    # Tắt ứng dụng JXTrain
    GF.close_application("JXTrain")

    # except Exception as e:
    #     print(f"Lỗi khi bật auto!")
    return currentAutoName

def auto_login(account, sleepTime, currentAutoName, isAutoClickVLBS, isChangeServer):
    global stop_login
    if stop_login:
        return  # Kiểm tra cờ dừng

    # Mở game bằng pyautogui
    pyautogui.hotkey('win', 'r')
    time.sleep(global_time_sleep)
    pyautogui.write(account['game_path'])
    time.sleep(global_time_sleep)
    pyautogui.press('enter')

    # # Mở game bằng ctypes và os
    # path = account['game_path']
    # ctypes.windll.shell32.ShellExecuteW(None, "runas", path, None, None, 1)

    time.sleep(sleepTime[0]['wait_time_open'])

    isOpenExe = GF.checkWindowRunning('Vo Lam Truyen Ky')
    print('isOpenExe:', isOpenExe)

    if isOpenExe == 0:
        GF.close_application('Vo Lam Truyen Ky')
        pyautogui.press('enter')
        return 3
    else:
        print("Đã mở game.exe")

    if stop_login:
        return  # Kiểm tra cờ dừng

    pyautogui.press('enter')
    time.sleep(global_time_sleep)
    

    if stop_login:
        return  # Kiểm tra cờ dừng

    pyautogui.press('enter')
    time.sleep(global_time_sleep)

    if stop_login:
        return  # Kiểm tra cờ dừng

    if isChangeServer:
        pyautogui.press('down')

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

    InGameName = updateIngame.check_valid_ingame_value(account['username'], currentAutoName)
    if InGameName == False:
        print(f"Có lỗi khi đăng nhập 2: {account['username']}")
        GF.close_application('Vo Lam Truyen Ky')
        return 2

    autoClickVLBS.start_click(currentAutoName, isAutoClickVLBS)
    print(f"Đã đăng nhập vào tài khoản: {account['username']}")
    return 1
    
def runStartLogin(isAutoClickVLBS, callback, currentAutoName):
    global stop_login
    stop_login = False  # Reset cờ dừng khi bắt đầu
    auto_tool_path = load_auto_tool_path()
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
                        print(f"Login lần {i+1} và thử đổi server!")
                        login_success = auto_login(account, sleepTime, currentAutoName, isAutoClickVLBS, True)
                elif login_success == 3:
                    print(f"Login lần {i+1} vì trước đó không hiện gamme!")
                    login_success = auto_login(account, sleepTime, currentAutoName, isAutoClickVLBS, False)
                else:
                    print(f"Login lần {i+1}")
                    login_success = auto_login(account, sleepTime, currentAutoName, isAutoClickVLBS, False)
            if i == (tryLoginNumber-1):
                if login_success != 1:
                    add_server_fail_value('fail_servers.json', account['auto_update_path'])
                    print(f"Server failed for account {account['username']}")
    print("Hoàn thành login!")
    
    # Gọi callback sau khi hoàn thành
    callback()


def add_server_fail_value(file_path, new_value):
    try:
        # Kiểm tra nếu file không tồn tại hoặc file rỗng
        if not os.path.exists(os.path.join(join_directory_data(), file_path)) or os.stat(os.path.join(join_directory_data(), file_path)).st_size == 0:
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

if __name__ == "__main__":
    runStartLogin()