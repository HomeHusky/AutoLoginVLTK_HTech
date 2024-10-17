import win32gui
import ctypes

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

# Ví dụ sử dụng
window_title = "vocongtruyenky.net"
items = get_listbox_data_from_window(window_title)
print("Các mục trong List:", items)
