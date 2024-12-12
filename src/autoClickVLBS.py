from pywinauto import Application
from pywinauto.keyboard import send_keys
import json
import time
import re
import GlobalFunction as GF
import os
import updateIngame

global_time_sleep = GF.load_global_time_sleep()

def start_click(username, name, isAutoClickVLBS):
    try:
        print("isAutoClickVLBS in autoClickVLBS.py:", isAutoClickVLBS)
        print("name AutoVLBS:", name)
        # auto_name = ['vocongtruyenky', 'anotherapp', 'yetanotherapp']
        GF.checkBothAutoVlbsAndQuanLyRunning(name)
        if name == None:
            name = GF.getNameAutoVLBS()

        if GF.checkQuanlynhanvat():
            pass
        elif GF.checkWindowRunning(name) == 1:
            run_right_click(name)
            time.sleep(global_time_sleep)
        elif GF.checkWindowRunning(name) == 2:
            GF.show_application(name)
            time.sleep(global_time_sleep)

        ingameByUsername = getIngameValueByUserName(username)
        if not run_down_enter(ingameByUsername, name, isAutoClickVLBS):
            return False
        return True
    except Exception as e:
        print(f"Lỗi dòng 30 file autoClickVLBS.py: ", e)

def getIngameValueByUserName(username):
    data = None
    # Đọc file JSON với encoding 'utf-8'
    with open(os.path.join(GF.join_directory_data(), 'accounts.json'), 'r', encoding='utf-8') as file:
        data = json.load(file)

    for account in data['accounts']:
        if account.get('username') == username:
            ingame = account.get('ingame')
            return ingame

def run_right_click(name):
    try:
        backend = GF.get_backend()
        list_control = Application(backend="uia").connect(title_re=name).window(title_re=name).child_window(control_type="List")
        if not list_control.exists():
            print("Không tìm thấy bảng!")
        else:
            # Tìm các mục trong danh sách và nhấp chuột phải vào mục đầu tiên
            items = list_control.children(control_type="ListItem")
            if items:
                items[0].right_click_input()
            else:
                print("Không có mục nào trong danh sách!")
    except Exception as e:
        print(f"Lỗi dòng 45 file autoClickVLBS.py: ", e)

def run_down_enter(ingameByUsername, currentAutoName, isAutoClickVLBS):
    list_control = None
    try:
        for attempt in range(3):
            try:
                print(f"Thử kết nối lần {attempt + 1}...")
                backend = GF.get_backend()
                list_control = Application(backend="uia").connect(title_re='^Quan ly nhan vat.*').window(title_re='^Quan ly nhan vat.*').child_window(control_type="List")
                print("Kết nối thành công!")
                break  # Nếu kết nối thành công, thoát vòng lặp
            except Exception as e:
                print(f"Lỗi khi kết nối (lần {attempt + 1}): {e}")
                time.sleep(1)  # Đợi 1 giây trước khi thử lại
        if not list_control.exists():
            print("Không tìm thấy bảng!")
        else:
            items = list_control.children(control_type="ListItem")
            if not check_after_click_auto(ingameByUsername, currentAutoName):
                return False
            items[0].double_click_input()
            if isAutoClickVLBS:
                items[0].right_click_input()
                time.sleep(global_time_sleep)
                send_keys("{DOWN}")
                time.sleep(global_time_sleep)
                send_keys("{ENTER}")
                time.sleep(5)
                if not check_after_click_auto(ingameByUsername, currentAutoName):
                    return False
            time.sleep(global_time_sleep)
        return True
    except Exception as e:
        print(f"Lỗi dòng 64 file autoClickVLBS.py: ", e)

def check_after_click_auto(ingameByUsername, currentAutoName):
    ingame = updateIngame.getIngame(currentAutoName)
    if ingame != ingameByUsername:
        return False
    return True

if __name__ == "__main__":
    start_click('vocongtruyenky', 0)
