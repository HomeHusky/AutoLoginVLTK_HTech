from pywinauto import Application
import json
import time 
import GlobalFunction as GF
import autoClickVLBS
import startLogin
import pyautogui
import re
import os

pyautogui.FAILSAFE = False

global_time_sleep = GF.load_global_time_sleep()

def get_dlg(currentAutoName, backend):
    print("currentAutoName: ", currentAutoName)
    print("backend: ", backend)
    list_control = None
    if GF.checkQuanlynhanvat():
        # Kết nối đến ứng dụng có tiêu đề "vocongtruyenky"
        for attempt in range(3):
            try:
                print(f"Thử kết nối lần {attempt + 1}...")
                
                app = Application(backend="uia").connect(title_re='^Quan ly nhan vat.*')
                print("Kết nối thành công!")
                break  # Nếu kết nối thành công, thoát vòng lặp
            except Exception as e:
                print(f"Lỗi khi kết nối (lần {attempt + 1}): {e}")
                time.sleep(1)  # Đợi 1 giây trước khi thử lại
        # Lấy cửa sổ chính của ứng dụng
        dlg = app.window(title_re='^Quan ly nhan vat.*')
        list_control = dlg.child_window(control_type="List")  # mặc định nếu chỉ có 1  
    elif GF.checkWindowRunning(currentAutoName) == 1:
        useAutoVLBS = True
        # Kết nối đến ứng dụng có tiêu đề "vocongtruyenky"
        app = Application(backend="uia").connect(title_re=currentAutoName)

        # Lấy cửa sổ chính của ứng dụng
        dlg = app.window(title_re=currentAutoName)
        # Lấy tất cả control loại List trong cửa sổ
        list_controls = dlg.descendants(control_type="List")

        # Kiểm tra số lượng và lấy theo điều kiện
        if len(list_controls) == 3:
            print("Có 3 List control, lấy cái đầu tiên.")
            list_control = list_controls[2]  # lấy cái đầu tiên
        else:
            list_control = dlg.child_window(control_type="List")  # mặc định nếu chỉ có 1  
    elif GF.checkWindowRunning(currentAutoName) == 2:
        GF.show_application(currentAutoName)
        useAutoVLBS = True
        # Kết nối đến ứng dụng có tiêu đề "vocongtruyenky"
        app = Application(backend="uia").connect(title_re=currentAutoName)

        # Lấy cửa sổ chính của ứng dụng
        dlg = app.window(title_re=currentAutoName)
        # Lấy tất cả control loại List trong cửa sổ
        list_controls = dlg.descendants(control_type="List")

        # Kiểm tra số lượng và lấy theo điều kiện
        if len(list_controls) == 3:
            print("Có 3 List control, lấy cái đầu tiên.")
            list_control = list_controls[2]  # lấy cái đầu tiên
        else:
            list_control = dlg.child_window(control_type="List")  # mặc định nếu chỉ có 1  

    return list_control

def getCheckData(currentAutoName):
    backend = None
    backend = GF.get_backend()
    useAutoVLBS = None
    list_control = None
    GF.checkBothAutoVlbsAndQuanLyRunning(currentAutoName)
    print("18_checkStatusAcounts.py: ", currentAutoName)
    try:
        # Tìm danh sách điều khiển
        if GF.checkQuanlynhanvat():
            # Kết nối đến ứng dụng có tiêu đề "vocongtruyenky"
            list_control = None
            for attempt in range(3):
                try:
                    print(f"Thử kết nối lần {attempt + 1}...")
                    
                    app = Application(backend="uia").connect(title_re='^Quan ly nhan vat.*')
                    print("Kết nối thành công!")
                    break  # Nếu kết nối thành công, thoát vòng lặp
                except Exception as e:
                    print(f"Lỗi khi kết nối (lần {attempt + 1}): {e}")
                    time.sleep(1)  # Đợi 1 giây trước khi thử lại
            # Lấy cửa sổ chính của ứng dụng
            dlg = app.window(title_re='^Quan ly nhan vat.*')
            list_control = dlg.child_window(control_type="List")
        elif GF.checkWindowRunning(currentAutoName) == 1:
            useAutoVLBS = True
            # Kết nối đến ứng dụng có tiêu đề "vocongtruyenky"
            app = Application(backend="uia").connect(title_re=currentAutoName)

            # Lấy cửa sổ chính của ứng dụng
            dlg = app.window(title_re=currentAutoName)
            list_controls = dlg.descendants(control_type="List")

            # Kiểm tra số lượng và lấy theo điều kiện
            if len(list_controls) == 3:
                print("Có 3 List control, lấy cái đầu tiên.")
                list_control = list_controls[2]  # lấy cái đầu tiên
            else:
                list_control = dlg.child_window(control_type="List")  # mặc định nếu chỉ có 1  
        elif GF.checkWindowRunning(currentAutoName) == 2:
            GF.show_application(currentAutoName)
            useAutoVLBS = True
            # Kết nối đến ứng dụng có tiêu đề "vocongtruyenky"
            app = Application(backend="uia").connect(title_re=currentAutoName)

            # Lấy cửa sổ chính của ứng dụng
            dlg = app.window(title_re=currentAutoName)
            list_controls = dlg.descendants(control_type="List")

            # Kiểm tra số lượng và lấy theo điều kiện
            if len(list_controls) == 3:
                print("Có 3 List control, lấy cái đầu tiên.")
                list_control = list_controls[2]  # lấy cái đầu tiên
            else:
                list_control = dlg.child_window(control_type="List")  # mặc định nếu chỉ có 1  
        # list_control = get_dlg(currentAutoName, backend)
        if not list_control:
            try: 
                print("Retry with backend uia!")
                backend = "uia"
                list_control = None
                if GF.checkQuanlynhanvat():
                    # Kết nối đến ứng dụng có tiêu đề "vocongtruyenky"
                    for attempt in range(3):
                        try:
                            print(f"Thử kết nối lần {attempt + 1}...")
                            
                            app = Application(backend="uia").connect(title_re='^Quan ly nhan vat.*')
                            print("Kết nối thành công!")
                            break  # Nếu kết nối thành công, thoát vòng lặp
                        except Exception as e:
                            print(f"Lỗi khi kết nối (lần {attempt + 1}): {e}")
                            time.sleep(1)  # Đợi 1 giây trước khi thử lại
                    # Lấy cửa sổ chính của ứng dụng
                    dlg = app.window(title_re='^Quan ly nhan vat.*')
                    list_control = dlg.child_window(control_type="List")
                elif GF.checkWindowRunning(currentAutoName) == 1:
                    useAutoVLBS = True
                    # Kết nối đến ứng dụng có tiêu đề "vocongtruyenky"
                    app = Application(backend="uia").connect(title_re=currentAutoName)

                    # Lấy cửa sổ chính của ứng dụng
                    dlg = app.window(title_re=currentAutoName)
                    list_controls = dlg.descendants(control_type="List")

                    # Kiểm tra số lượng và lấy theo điều kiện
                    if len(list_controls) == 3:
                        print("Có 3 List control, lấy cái đầu tiên.")
                        list_control = list_controls[2]  # lấy cái đầu tiên
                    else:
                        list_control = dlg.child_window(control_type="List")  # mặc định nếu chỉ có 1  
                elif GF.checkWindowRunning(currentAutoName) == 2:
                    GF.show_application(currentAutoName)
                    useAutoVLBS = True
                    # Kết nối đến ứng dụng có tiêu đề "vocongtruyenky"
                    app = Application(backend="uia").connect(title_re=currentAutoName)

                    # Lấy cửa sổ chính của ứng dụng
                    dlg = app.window(title_re=currentAutoName)
                    list_controls = dlg.descendants(control_type="List")

                    # Kiểm tra số lượng và lấy theo điều kiện
                    if len(list_controls) == 3:
                        print("Có 3 List control, lấy cái đầu tiên.")
                        list_control = list_controls[2]  # lấy cái đầu tiên
                    else:
                        list_control = dlg.child_window(control_type="List")  # mặc định nếu chỉ có 1  
            except Exception as e:
                print("Error as line 64:", e)
        if not list_control:
            print("Không tìm thấy bảng!")
            return []
        else:
            items = list_control.children(control_type="ListItem")
            data = []
            if useAutoVLBS:
                print("Truong hop 1")
                for item in items:
                    if useAutoVLBS:
                        item_text = item.window_text()  # Lấy văn bản của mục
                        data.append(item_text)
            else:
                print("Truong hop 2")
                for item in items:
                    count = 0
                    for child in item.children():
                        if count == 1: 
                            data.append(child.window_text())
                        count += 1
        time.sleep(global_time_sleep)

        return data
    except Exception as e:
        print("Lỗi update Status: " + str(e))
        return None

def update_login_status(json_data, checkData):
    for account in json_data['accounts']:
        try:
            print("Account:", account)
            if account['ingame'] in checkData:
                account['is_logged_in'] = True
            else:
                account['is_logged_in'] = False
        except Exception as e:
            print("Error line 91 checkStatusAccounts.py:", e)
    return json_data

def set_all_is_select_accounts_to_false(file_path="accounts.json"):
    # Đọc file json
    with open(os.path.join(GF.join_directory_data(), file_path), "r", encoding="utf-8") as f:
        data = json.load(f)

    # Chỉnh tất cả is_select thành False
    for acc in data.get("accounts", []):
        acc["is_select"] = False

    # Ghi lại file json
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return data
    
def checkStatusAcounts(auto_tool_path, currentAutoName, sleepTime):
    updated_data = None
    if not currentAutoName:
        set_all_is_select_accounts_to_false()
        currentAutoName = startLogin.auto_open_autoVLBS(auto_tool_path, sleepTime)
        print("currentAutoName:", currentAutoName)
        return False
            
    data = None

    # Đọc file JSON với encoding 'utf-8'
    data = GF.read_json_file('accounts.json')

    checkData = getCheckData(currentAutoName)
    print("CHECKDATA: ", checkData)

    # Cập nhật trạng thái đăng nhập dựa trên checkData
    updated_data = update_login_status(data, checkData)
    # Ghi lại dữ liệu đã cập nhật vào file JSON với encoding 'utf-8'
    with open(os.path.join(GF.join_directory_data(), 'accounts.json'), 'w', encoding='utf-8') as file:
        # Đảm bảo ensure_ascii=False để giữ nguyên ký tự Unicode
        json.dump(updated_data, file, ensure_ascii=False, indent=4)

    print("Cập nhật TRẠNG THÁI thành công!")

    return updated_data

if __name__ == "__main__":
    getCheckData("vocongtruyenky.net")
