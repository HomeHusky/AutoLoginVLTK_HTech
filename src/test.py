import win32gui
import win32con
import re
import ctypes
import time
import platform
from pywinauto import Application
import pyautogui

pyautogui.FAILSAFE = False

# Hằng số cho ListView Messages
LVM_GETITEMCOUNT = 0x1004
LVM_GETITEMTEXT = 0x102D

def find_list_control(hwnd):
    list_control_hwnd = None

    def callback(hwnd_child, _):
        nonlocal list_control_hwnd
        class_name = win32gui.GetClassName(hwnd_child)
        # Kiểm tra nếu class name là SysListView32 hoặc tên class khác mà ứng dụng sử dụng
        if class_name == "SysListView32":  
            list_control_hwnd = hwnd_child

    win32gui.EnumChildWindows(hwnd, callback, None)
    return list_control_hwnd

def get_list_items(list_hwnd):
    items = []
    
    # Lấy số lượng mục trong ListView
    count = win32gui.SendMessage(list_hwnd, LVM_GETITEMCOUNT)
    if count == -1:
        print("Không phải là ListView hoặc không thể truy cập được.")
        return items

    for index in range(count):
        buffer_size = 256
        buffer = ctypes.create_unicode_buffer(buffer_size)

        # Cấu trúc LVITEM để lấy văn bản của mục
        class LVITEM(ctypes.Structure):
            _fields_ = [
                ("mask", ctypes.c_uint),
                ("iItem", ctypes.c_int),
                ("iSubItem", ctypes.c_int),
                ("state", ctypes.c_uint),
                ("stateMask", ctypes.c_uint),
                ("pszText", ctypes.c_wchar_p),
                ("cchTextMax", ctypes.c_int),
                ("iImage", ctypes.c_int),
                ("lParam", ctypes.c_long),
                ("iIndent", ctypes.c_int),
                ("iGroupId", ctypes.c_int),
                ("cColumns", ctypes.c_uint),
                ("puColumns", ctypes.POINTER(ctypes.c_uint)),
                ("piColFmt", ctypes.POINTER(ctypes.c_int)),
                ("iGroup", ctypes.c_int),
            ]

        lv_item = LVITEM()
        lv_item.mask = 0x0001  # LVIF_TEXT
        lv_item.iItem = index
        lv_item.iSubItem = 0
        lv_item.pszText = ctypes.cast(buffer, ctypes.c_wchar_p)
        lv_item.cchTextMax = buffer_size

        # Lấy địa chỉ của cấu trúc LVITEM và gửi thông điệp
        result = win32gui.SendMessage(list_hwnd, LVM_GETITEMTEXT, index, ctypes.cast(ctypes.pointer(lv_item), ctypes.c_void_p))
        item_text = buffer.value

        items.append(item_text)

    return items

def get_listbox_data_from_window(window_title):
    hwnd = win32gui.FindWindow(None, window_title)
    if not hwnd:
        print(f"Không tìm thấy cửa sổ có tiêu đề: {window_title}")
        return []

    # Tìm handle của ListBox hoặc ListView bên trong cửa sổ
    list_control_hwnd = find_list_control(hwnd)
    if not list_control_hwnd:
        print("Không tìm thấy điều khiển dạng List trong cửa sổ")
        return []
    print(list_control_hwnd)

    # Lấy dữ liệu từ List
    items = get_list_items(list_control_hwnd)
    return items

def is_window_visible(hwnd):
    """Kiểm tra xem cửa sổ có hiển thị hay không."""
    return win32gui.IsWindowVisible(hwnd)

def get_backend():
    """Xác định backend dựa trên kiến trúc hệ thống (32-bit hoặc 64-bit)."""
    architecture = platform.architecture()[0]
    print(f"Hệ thống đang chạy trên kiến trúc: {architecture}")
    return "win32" if architecture == "32bit" else "uia"

def get_visible_vo_lam_windows():
    """Lấy danh sách hwnd của tất cả các cửa sổ 'Vo Lam Truyen Ky' đang hiển thị."""
    hwnds = []

    def enum_windows_callback(hwnd, extra):
        if "Vo Lam Truyen Ky" in win32gui.GetWindowText(hwnd) and is_window_visible(hwnd):
            hwnds.append(hwnd)

    win32gui.EnumWindows(enum_windows_callback, None)
    return hwnds

def get_child_window_text(hwnd):
    """Lấy nội dung của các cửa sổ con (child controls) của cửa sổ popup."""
    texts = []

    def enum_child_windows_callback(child_hwnd, extra):
        text = win32gui.GetWindowText(child_hwnd)
        if text:  # Nếu text không rỗng
            texts.append(text)

    win32gui.EnumChildWindows(hwnd, enum_child_windows_callback, None)
    return texts

# Ban muon thoat khoi Vo Lam Truyen Ky?
# def close_visible_vltk_app():
#     """
#     Đóng các cửa sổ Võ Lâm Truyền Kỳ đang hiển thị, giữ nguyên các cửa sổ ẩn.
#     """
#     try:
#         def enum_window_callback(hwnd, window_list):
#             """Hàm callback để liệt kê các cửa sổ đang chạy."""
#             title = win32gui.GetWindowText(hwnd)
#             if re.search(r'Vo Lam Truyen Ky', title, re.IGNORECASE):
#                 window_list.append((hwnd, title))
        
#         # Danh sách các cửa sổ khớp với "Vo Lam Truyen Ky"
#         windows = []
#         win32gui.EnumWindows(enum_window_callback, windows)
        
#         for hwnd, title in windows:
#             # Kiểm tra nếu cửa sổ đang hiển thị (visible)
#             if win32gui.IsWindowVisible(hwnd):
#                 print(f"Đóng cửa sổ: {title}")
#                 win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

#                 # time.sleep(2)

#                 # pyautogui.press('enter')
    
#     except Exception as e:
#         print(f"Lỗi: {e}")

def close_visible_vltk_app():
    """Đóng cửa sổ 'Vo Lam Truyen Ky' đang hiển thị và xử lý popup xác nhận."""
    # Bước 1: Lấy danh sách hwnd của cửa sổ chính 'Vo Lam Truyen Ky' đang hiển thị
    initial_hwnds = get_visible_vo_lam_windows()
    if not initial_hwnds:
        print("Không tìm thấy cửa sổ hiển thị nào có tiêu đề 'Vo Lam Truyen Ky'.")
        return
    
    print(f"Danh sách hwnd của cửa sổ chính trước khi đóng: {initial_hwnds}")

    # Bước 2: Đóng tất cả các cửa sổ chính 'Vo Lam Truyen Ky'
    for hwnd in initial_hwnds:
        print(f"Đang đóng cửa sổ chính với hwnd: {hwnd}")
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        print("Parents: ", get_child_window_text(hwnd))
    
    # Đợi để cửa sổ chính đóng và popup xuất hiện
    time.sleep(2)  # Chờ 2 giây để popup xuất hiện

    # Bước 3: Lấy lại danh sách hwnd của tất cả các cửa sổ 'Vo Lam Truyen Ky' hiện tại
    current_hwnds = get_visible_vo_lam_windows()
    print(f"Danh sách hwnd của tất cả các cửa sổ sau khi đóng: {current_hwnds}")

    # Bước 4: Lọc các hwnd của popup (cửa sổ mới, không có trong danh sách ban đầu)
    popup_hwnds = [hwnd for hwnd in current_hwnds if hwnd not in initial_hwnds]
    if not popup_hwnds:
        print("Không tìm thấy popup xác nhận nào.")
        return
    
    print(f"Danh sách hwnd của popup mới xuất hiện: {popup_hwnds}")

    # Bước 5: Xử lý popup xác nhận, tự động nhấn Yes nếu tìm thấy
    for popup_hwnd in popup_hwnds:
        try:
            backend = get_backend()
            print(f"Đang kết nối với hwnd: {popup_hwnd} bằng backend: {backend}")
            app = Application(backend="uia").connect(handle=popup_hwnd)
            popup = app.window(handle=popup_hwnd)
            
            # Kiểm tra nếu message là 'Ban muon thoat khoi Vo Lam Truyen Ky?'
            texts = get_child_window_text(popup_hwnd)
            print("Texts: ", texts==['&Yes', '&No', 'Ban muon thoat  khoi Vo Lam Truyen Ky?'])

            if texts==['&Yes', '&No', 'Ban muon thoat  khoi Vo Lam Truyen Ky?']:
                print(f"Tìm thấy popup xác nhận. Chọn 'Yes' cho hwnd: {popup_hwnd}")
                yes_button = popup.child_window(title="Yes", control_type="Button")
                yes_button.click()
            else:
                print(f"Nội dung của popup không khớp.")
        except Exception as e:
            print(f"Không thể xử lý popup với hwnd {popup_hwnd}: {e}")

def run_press_space_VLBS(ingameByUsername, name, isAutoClickVLBS):
    try:
        list_control = Application(backend="uia").connect(title_re=name).window(title_re=name).child_window(control_type="List")
        if not list_control.exists():
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

# Ví dụ sử dụng
# window_title = "vocongtruyenky.net"
window_title = "congthanhchienxua.net"
ingame = THTPÙTESTÙAUTO
# items = get_listbox_data_from_window(window_title)
# print("Các mục trong List:", items)
if __name__ == "__main__":
    run_press_space_VLBS(ingame, window_title, True)
