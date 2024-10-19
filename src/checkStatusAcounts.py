from pywinauto import Application
import json
import time 
import GlobalFunction as GF
import autoClickVLBS
import startLogin
import pyautogui
import re
import os

global_time_sleep = GF.load_global_time_sleep()

def getCheckData(currentAutoName):
    useAutoVLBS = None
    GF.checkBothAutoVlbsAndQuanLyRunning(currentAutoName)
    try:
        if GF.checkQuanlynhanvat():
            # Kết nối đến ứng dụng có tiêu đề "vocongtruyenky"
            app = Application(backend="uia").connect(title_re='^Quan ly nhan vat.*')

            # Lấy cửa sổ chính của ứng dụng
            dlg = app.window(title_re='^Quan ly nhan vat.*')
        elif GF.checkWindowRunning(currentAutoName) == 1:
            useAutoVLBS = True
            # Kết nối đến ứng dụng có tiêu đề "vocongtruyenky"
            app = Application(backend="uia").connect(title_re=currentAutoName)

            # Lấy cửa sổ chính của ứng dụng
            dlg = app.window(title_re=currentAutoName)
        elif GF.checkWindowRunning(currentAutoName) == 2:
            GF.show_application(currentAutoName)
            useAutoVLBS = True
            # Kết nối đến ứng dụng có tiêu đề "vocongtruyenky"
            app = Application(backend="uia").connect(title_re=currentAutoName)

            # Lấy cửa sổ chính của ứng dụng
            dlg = app.window(title_re=currentAutoName)

        # Tìm danh sách điều khiển
        list_control = dlg.child_window(control_type="List")

        if not list_control.exists():
            print("Không tìm thấy bảng!")
            return None
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
            print("Error:", e)
    return json_data

def checkStatusAcounts(auto_tool_path, currentAutoName, sleepTime):
    updated_data = None
    if not currentAutoName:

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
