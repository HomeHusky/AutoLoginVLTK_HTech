import win32gui
import win32process

def get_all_vltk_windows_win32():
    results = []

    def enum_handler(hwnd, _):
        title = win32gui.GetWindowText(hwnd)
        if "Vo Lam Truyen Ky" in title:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            results.append({
                "title": title,
                "handle": hwnd,
                "pid": pid,
                "visible": win32gui.IsWindowVisible(hwnd)
            })

    win32gui.EnumWindows(enum_handler, None)
    return results

def get_all_vpid_vo_lam_windows():
    """Lấy danh sách các cửa sổ 'Vo Lam Truyen Ky' đang hiển thị và trả về danh sách các PID của chúng."""
    windows = get_all_vltk_windows_win32()
    vltk_pids = []
    for w in windows:
        vltk_pids.append(w['pid'])
    return vltk_pids

if __name__ == "__main__":
    # windows = get_all_vltk_windows_win32()
    # for w in windows:
    #     state = "🟢 Hiển thị" if w['visible'] else "⚫ Đang ẩn"
    #     print(f"{state} | HWND: {w['handle']} | PID: {w['pid']} | Title: {w['title']}")
    vltk_pids = get_all_vpid_vo_lam_windows()
    if vltk_pids:
        print("Danh sách PID của các cửa sổ 'Vo Lam Truyen Ky' đang hiển thị:")
        for pid in vltk_pids:
            print(f"PID: {pid}")
    else:
        print("Không tìm thấy cửa sổ 'Vo Lam Truyen Ky' nào đang hiển thị.")