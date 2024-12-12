import json
from pywinauto import Application
import time 
import GlobalFunction as GF
import os

global_time_sleep = GF.load_global_time_sleep()

def getIngame(autoName):
    try:
        useAutoVlbs = False
        inGame = None
        app = None
        dlg = None
        list_control = None
        # Thử kết nối với từng ứng dụng trong mảng
        GF.checkBothAutoVlbsAndQuanLyRunning(autoName)
        backend = GF.get_backend()
        if GF.checkWindowRunning(autoName) == 1:
            useAutoVlbs = True
            try:
                # Kết nối đến ứng dụng có tiêu đề "vocongtruyenky"
                app = Application(backend=backend).connect(title_re=autoName)

                # Lấy cửa sổ chính của ứng dụng
                dlg = app.window(title_re=autoName)

            except Exception as e:
                print("next----------> 1")

        else:
            for attempt in range(3):
                try:
                    print(f"Thử kết nối lần {attempt + 1}...")
                    list_control = Application(backend=backend).connect(title_re='^Quan ly nhan vat.*')
                    print("Kết nối thành công!")
                    break  # Nếu kết nối thành công, thoát vòng lặp
                except Exception as e:
                    print(f"Lỗi khi kết nối (lần {attempt + 1}): {e}")
                    time.sleep(1)  # Đợi 1 giây trước khi thử lại
            # Kết nối đến ứng dụng có tiêu đề "vocongtruyenky"

            # Lấy cửa sổ chính của ứng dụng
            dlg = list_control.window(title_re='^Quan ly nhan vat.*')
        
        try:
            # Tìm danh sách điều khiển
            list_control = dlg.child_window(control_type="List")
            inGame = None
            if not list_control.exists():
                print("Không tìm thấy bảng!")
            else:
                items = list_control.children(control_type="ListItem")
                print("IngameList: " + items[0].window_text())

                if useAutoVlbs:
                    print("Truong hop 1")
                    inGame = items[0].window_text()  # Lấy văn bản của mục
                else:
                    print("Truong hop 2")
                    count = 0
                    for child in items[0].children():
                        if count == 1: 
                            inGame = child.window_text()
                        count += 1
            time.sleep(global_time_sleep)
            return inGame
        except Exception as e:
            print("Chưa hiển thị autoVLBS")
    except Exception as e:
        print(f"Lỗi dòng 62 file updateIngame.py: ", e)
        
def update_ingame(username, ingame_value, json_data):
    # Duyệt qua danh sách tài khoản trong dữ liệu JSON
    try:
        for account in json_data['accounts']:
            # Kiểm tra xem username có khớp không
            if account['username'] == username:
                # Cập nhật giá trị ingame
                if ingame_value != None:
                    account['ingame'] = ingame_value
                break  # Dừng lại sau khi đã cập nhật
    except Exception as e:
        for account in json_data['accounts']:
            # Kiểm tra xem username có khớp không
            if account['username'] == username:
                # Cập nhật giá trị ingame
                account['ingame'] = ""
                break  # Dừng lại sau khi đã cập nhật
    return json_data

def run_update_ingame(username_to_update, ingame_value_to_update):
    print("ingame_value_to_update:", ingame_value_to_update)
    data = None
    # Đọc file JSON với encoding 'utf-8'
    data = GF.read_json_file('accounts.json')

    updated_data = update_ingame(username_to_update, ingame_value_to_update, data)
    # Ghi lại dữ liệu đã cập nhật vào file JSON
    with open(os.path.join(GF.join_directory_data(), 'accounts.json'), 'w', encoding='utf-8') as file:
        # Đảm bảo không chuyển đổi các ký tự Unicode sang ASCII
        json.dump(updated_data, file, ensure_ascii=False, indent=4)

    print("Cập nhật INGAME thành công!")
    return ingame_value_to_update

def getIngameValueByUserName(username, data):
    for account in data['accounts']:
        if account.get('username') == username:
            ingame = account.get('ingame')
            return ingame

def checkExistIngame(ingame, data):
    for account in data['accounts']:
        if account.get('ingame') == ingame:
            return True

def check_valid_ingame_value(username_to_update, autoName):
    ingame_value_to_update = getIngame(autoName)
    data = None
    # Đọc file JSON với encoding 'utf-8'
    with open(os.path.join(GF.join_directory_data(), 'accounts.json'), 'r', encoding='utf-8') as file:
        data = json.load(file)

    ingame_in_jsonfile_with_username = getIngameValueByUserName(username_to_update, data)

    print(f"VLBS: {ingame_value_to_update}, JSON: {ingame_in_jsonfile_with_username}")
    if ingame_value_to_update == "" or ingame_value_to_update == "Vo Lam Truyen Ky":
        return False
    else:
        if not checkExistIngame(ingame_value_to_update, data):
            run_update_ingame(username_to_update, ingame_value_to_update)
    return True