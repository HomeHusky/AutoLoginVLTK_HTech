"""
Helper script để di chuyển console window xuống góc dưới trái
"""
import ctypes
import time

def move_console_to_bottom_left():
    """Di chuyển console window xuống góc dưới trái màn hình"""
    try:
        # Import win32 modules
        try:
            import win32gui
            import win32con
            import win32api
        except ImportError:
            print("⚠️ Không có pywin32, bỏ qua di chuyển console")
            return False
        
        # Đợi một chút để console hiện ra
        time.sleep(0.5)
        
        # Lấy handle của console window
        console_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        
        if console_hwnd == 0:
            print("⚠️ Không tìm thấy console window")
            return False
        
        # Lấy kích thước màn hình
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)
        
        # Kích thước console (nhỏ gọn)
        console_width = 500
        console_height = 250
        
        # Vị trí góc dưới trái
        x = 0
        y = screen_height - console_height - 40  # -40 để tránh taskbar
        
        # Set title cho console trước
        try:
            ctypes.windll.kernel32.SetConsoleTitleW("Auto Login Console")
        except:
            pass
        
        # Di chuyển và resize console
        win32gui.SetWindowPos(
            console_hwnd,
            win32con.HWND_BOTTOM,  # Đặt ở dưới cùng (không che app)
            x, y,
            console_width, console_height,
            win32con.SWP_SHOWWINDOW
        )
        
        # Đợi một chút
        time.sleep(0.2)
        
        # Minimize console để không chiếm chỗ
        win32gui.ShowWindow(console_hwnd, win32con.SW_MINIMIZE)
        
        print("✅ Console đã được di chuyển xuống góc dưới trái và minimize")
        print(f"📍 Vị trí: ({x}, {y})")
        print(f"📐 Kích thước: {console_width}x{console_height}")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi di chuyển console: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    move_console_to_bottom_left()
