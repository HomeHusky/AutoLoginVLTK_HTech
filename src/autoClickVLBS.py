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

        ingameByUsername = getIngameValueByUserName(username)

        if GF.checkQuanlynhanvat():
            if not run_down_enter(ingameByUsername, name, isAutoClickVLBS):
                return False
            return True
        elif GF.checkWindowRunning(name) == 1:
            # run_right_click(name)
            if not run_press_space_VLBS(ingameByUsername, name, isAutoClickVLBS):
                return False
            return True
        elif GF.checkWindowRunning(name) == 2:
            GF.show_application(name)

            time.sleep(global_time_sleep)
            if not run_press_space_VLBS(ingameByUsername, name, isAutoClickVLBS):
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
        list_control = None
        # backend = GF.get_backend()
        app = Application(backend="uia").connect(title_re=name)
        dlg = app.window(title_re=name)

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
            # Tìm các mục trong danh sách và nhấp chuột phải vào mục đầu tiên
            items = list_control.children(control_type="ListItem")
            if items:
                items[0].right_click_input()
            else:
                print("Không có mục nào trong danh sách!")
    except Exception as e:
        print(f"Lỗi dòng 45 file autoClickVLBS.py: ", e)

def run_press_space_VLBS(ingameByUsername, name, isAutoClickVLBS):
    try:
        list_control = None
        app = Application(backend="uia").connect(title_re=name)
        dlg = app.window(title_re=name)

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
            # Scroll lên đầu danh sách
            try:
                # Cách 1: Dùng phím Home
                list_control.set_focus()
                list_control.type_keys("{HOME}")
                
                # Hoặc cách 2: Dùng scroll pattern (nếu ứng dụng hỗ trợ)
                # list_control.iface_scroll.SetScrollPercent(horizontalPercent=None, verticalPercent=0)
                
                time.sleep(0.5)  # Đợi scroll hoàn thành
            except Exception as e:
                print(f"Lỗi khi scroll: {str(e)}")

            # Tìm các mục trong danh sách và thao tác
            items = list_control.children(control_type="ListItem")
            if items:
                first_item = items[0]
                first_item_text = first_item.window_text()
                if isAutoClickVLBS:
                    if first_item_text != ingameByUsername:
                        return False
                    # Nhấn chuột trái vào mục đầu tiên
                    first_item.click_input(button='left')
                    # Nhấn phím space
                    first_item.type_keys("{SPACE}")
                    if not check_after_click_auto(ingameByUsername, name):
                        return False
                first_item.double_click_input()
                time.sleep(global_time_sleep)
            else:
                print("Không có mục nào trong danh sách!")
            return True
    except Exception as e:
        print(f"Lỗi dòng 64 file autoClickVLBS.py: ", e)

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
        if not list_control:
            print("Không tìm thấy bảng!")
        else:
            items = list_control.children(control_type="ListItem")
            # if not check_after_click_auto(ingameByUsername, currentAutoName):
            #     return False
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
    """
    Kiểm tra tối đa 3 lần xem ingame có khớp với ingameByUsername hay không.
    Nếu không khớp sau 3 lần, trả về False.
    
    Args:
        ingameByUsername (str): Tên ingame cần so sánh.
        currentAutoName (str): Tên của auto hiện tại.
    
    Returns:
        bool: True nếu khớp, False nếu không khớp sau 3 lần.
    """
    MAX_ATTEMPTS = 3  # Số lần kiểm tra tối đa
    for attempt in range(1, MAX_ATTEMPTS + 1):
        ingame = updateIngame.getIngame(currentAutoName)
        if ingame == ingameByUsername:
            return True
        
        print(f"Lần thử {attempt}: ingame = {ingame}, yêu cầu = {ingameByUsername}")
        
        # Chờ 1 giây giữa các lần thử (có thể điều chỉnh tùy theo yêu cầu)
        time.sleep(1)
    
    return False


if __name__ == "__main__":
    start_click('vocongtruyenky', 0)
