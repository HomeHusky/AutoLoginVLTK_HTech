from pywinauto import Application
from pywinauto.keyboard import send_keys
import json
import time
import re
import GlobalFunction as GF

global_time_sleep = GF.load_global_time_sleep()

def start_click(name, isAutoClickVLBS):
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

    run_down_enter(isAutoClickVLBS)

def run_right_click(name):
    try:
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
        print(f"Lỗi dòng 40 file autoClickVLBS.py: ", e)

def run_down_enter(isAutoClickVLBS):
    try:
        list_control = Application(backend="uia").connect(title_re='^Quan ly nhan vat.*').window(title_re='^Quan ly nhan vat.*').child_window(control_type="List")
        if not list_control.exists():
            print("Không tìm thấy bảng!")
        else:
            items = list_control.children(control_type="ListItem")
            if isAutoClickVLBS:
                items[0].right_click_input()
                time.sleep(global_time_sleep)
                send_keys("{DOWN}")
                time.sleep(global_time_sleep)
                send_keys("{ENTER}") 
                time.sleep(global_time_sleep)
            items[0].double_click_input()
            time.sleep(global_time_sleep)
    except Exception as e:
        print(f"Lỗi dòng 59 file autoClickVLBS.py: ", e)

if __name__ == "__main__":
    start_click('vocongtruyenky', 0)
