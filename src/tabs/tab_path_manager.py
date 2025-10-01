# ===============================
# TAB QUẢN LÝ ĐƯỜNG DẪN
# ===============================

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import json
import os
import GlobalFunction as GF
import winshell
from win32com.client import Dispatch

class PathManagerTab:
    def __init__(self, parent, data_manager):
        """
        Khởi tạo tab Quản lý Đường dẫn
        
        Args:
            parent: Widget cha (notebook)
            data_manager: Object quản lý dữ liệu
        """
        self.parent = parent
        self.data_manager = data_manager
        
        # Biến checkbox
        self.varHideEffects = tk.IntVar()
        self.varStartUp = tk.IntVar()
        
        # Tạo giao diện
        self.create_ui()
    
    def create_ui(self):
        """Tạo giao diện cho tab"""
        # Frame thông tin đường dẫn
        auto_frame = ttk.LabelFrame(self.parent, text="Cài đặt Tự động", padding=(10, 5))
        auto_frame.pack(padx=5, pady=10, fill="x")
        
        self.auto_frame = auto_frame
        
        # Nhập đường dẫn tool auto
        ttk.Label(auto_frame, text="Đường dẫn Tool auto:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_auto_path = ttk.Entry(auto_frame)
        self.entry_auto_path.grid(row=0, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
        
        # Nút chọn đường dẫn auto
        browse_auto_button = ttk.Button(auto_frame, text="Browse", command=self.browse_auto_path)
        browse_auto_button.grid(row=0, column=5, padx=5, pady=5)
        
        # Tên auto
        ttk.Label(auto_frame, text="Tên auto:").grid(row=1, column=0, padx=5, pady=5)
        
        # Thời gian load game
        ttk.Label(auto_frame, text="Thời gian load game (s):").grid(row=4, column=0, padx=5, pady=5)
        self.entry_wait_game_open = ttk.Entry(auto_frame)
        self.entry_wait_game_open.grid(row=4, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
        
        # Thời gian load game nếu game mở lâu
        ttk.Label(auto_frame, text="Thời gian load game nếu game mở lâu (s):").grid(row=5, column=0, padx=5, pady=5)
        self.entry_wait_game_open2 = ttk.Entry(auto_frame)
        self.entry_wait_game_open2.grid(row=5, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
        
        # Thời gian load nhân vật
        ttk.Label(auto_frame, text="Thời gian load nhân vật (s):").grid(row=6, column=0, padx=5, pady=5)
        self.entry_wait_character_open = ttk.Entry(auto_frame)
        self.entry_wait_character_open.grid(row=6, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
        
        # Thời gian load server
        ttk.Label(auto_frame, text="Thời gian load server (s):").grid(row=7, column=0, padx=5, pady=5)
        self.entry_wait_server_open = ttk.Entry(auto_frame)
        self.entry_wait_server_open.grid(row=7, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
        
        # Thời gian load TrainJX
        ttk.Label(auto_frame, text="Thời gian load TrainJX (s):").grid(row=8, column=0, padx=5, pady=5)
        self.entry_wait_time_trainjx_open = ttk.Entry(auto_frame)
        self.entry_wait_time_trainjx_open.grid(row=8, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
        
        # Thời gian load AutoVLBS
        ttk.Label(auto_frame, text="Thời gian load AutoVLBS (s):").grid(row=9, column=0, padx=5, pady=5)
        self.entry_wait_time_autovlbs_open = ttk.Entry(auto_frame)
        self.entry_wait_time_autovlbs_open.grid(row=9, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
        
        # Số lần thử lại
        ttk.Label(auto_frame, text="Số lần thử lại:").grid(row=10, column=0, padx=5, pady=5)
        self.entry_try_number = ttk.Entry(auto_frame)
        self.entry_try_number.grid(row=10, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
        
        # Chờ cục bộ
        ttk.Label(auto_frame, text="Chờ cục bộ (0.5 hoặc 1 nếu máy nhanh):").grid(row=11, column=0, padx=5, pady=5)
        self.entry_global_time_sleep = ttk.Entry(auto_frame)
        self.entry_global_time_sleep.grid(row=11, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
        
        # Ẩn hiệu ứng
        ttk.Label(auto_frame, text="Ẩn hiệu ứng:").grid(row=12, column=0, padx=5, pady=5)
        self.varHideEffects.set(0)
        entry_hide_effects = ttk.Checkbutton(auto_frame, variable=self.varHideEffects)
        entry_hide_effects.grid(row=12, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
        
        # Khởi động cùng Window
        ttk.Label(auto_frame, text="Khởi động cùng Window:").grid(row=13, column=0, padx=5, pady=5)
        self.varStartUp.set(0)
        entry_start_up = ttk.Checkbutton(auto_frame, variable=self.varStartUp)
        entry_start_up.grid(row=13, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
        
        # Lưu dữ liệu đường dẫn auto
        save_button = ttk.Button(auto_frame, text="Lưu Cài đặt", command=self.save_auto_data)
        save_button.grid(row=13, column=5, padx=5, pady=5)
    
    def load_auto_data(self):
        """Load dữ liệu auto"""
        data = self.data_manager.load_data()
        global_time_data = self.data_manager.load_global_time()
        
        self.entry_auto_path.delete(0, tk.END)
        self.entry_auto_path.insert(0, data.get('auto_tool_path', ''))
        
        # Hiển thị tên auto
        for i, auto in enumerate(data.get('autoNames', [])):
            entry_game_name = ttk.Entry(self.auto_frame, width=40)
            entry_game_name.grid(row=i+1, column=1, padx=5, pady=5)
            entry_game_name.insert(0, auto)
        
        # Hiển thị thời gian sleepTime
        sleep_times = global_time_data.get('sleepTime', [])
        if sleep_times:
            self.entry_wait_game_open.delete(0, tk.END)
            self.entry_wait_game_open2.delete(0, tk.END)
            self.entry_wait_character_open.delete(0, tk.END)
            self.entry_wait_server_open.delete(0, tk.END)
            self.entry_wait_time_trainjx_open.delete(0, tk.END)
            self.entry_wait_time_autovlbs_open.delete(0, tk.END)
            self.entry_try_number.delete(0, tk.END)
            self.entry_global_time_sleep.delete(0, tk.END)
            self.varHideEffects.set(0)
            self.varStartUp.set(0)
            
            self.entry_wait_game_open.insert(0, sleep_times[0]['wait_time_open'])
            self.entry_wait_game_open2.insert(0, sleep_times[0]['wait_time_open2'])
            self.entry_wait_character_open.insert(0, sleep_times[0]['wait_time_load'])
            self.entry_wait_server_open.insert(0, sleep_times[0]['wait_time_server'])
            self.entry_wait_time_trainjx_open.insert(0, sleep_times[0]['wait_time_open_trainjx'])
            self.entry_wait_time_autovlbs_open.insert(0, sleep_times[0]['wait_time_load_autovlbs'])
            self.entry_try_number.insert(0, sleep_times[0]['try_number'])
            self.entry_global_time_sleep.insert(0, sleep_times[0]['global_time_sleep'])
            self.varHideEffects.set(sleep_times[0]['hide_effects'])
            self.varStartUp.set(sleep_times[0]['start_up'])
    
    def save_auto_data(self):
        """Lưu dữ liệu auto"""
        data = self.data_manager.load_data()
        global_time_data = self.data_manager.load_global_time()
        
        # Lưu đường dẫn tool auto
        data['auto_tool_path'] = self.entry_auto_path.get().strip()
        
        # Lưu tên game auto
        autoNames = []
        for i in range(len(data['autoNames'])):
            entry_game_name = self.auto_frame.grid_slaves(row=i+1, column=1)[0]
            autoNames.append(entry_game_name.get())
        data['autoNames'] = autoNames
        
        # Lưu thời gian auto
        wait_time_open = self.entry_wait_game_open.get().strip()
        wait_time_open2 = self.entry_wait_game_open2.get().strip()
        wait_time_load = self.entry_wait_character_open.get().strip()
        wait_time_server = self.entry_wait_server_open.get().strip()
        wait_time_open_trainjx = self.entry_wait_time_trainjx_open.get().strip()
        wait_time_load_autovlbs = self.entry_wait_time_autovlbs_open.get().strip()
        try_number = self.entry_try_number.get().strip()
        edit_global_time_sleep = self.entry_global_time_sleep.get().strip()
        hide_effects = self.varHideEffects.get()
        start_up = self.varStartUp.get()
        
        global_time_data['sleepTime'] = [{
            'wait_time_open': int(wait_time_open) if wait_time_open.isdigit() else 12,
            'wait_time_open2': int(wait_time_open2) if wait_time_open2.isdigit() else 45,
            'wait_time_load': int(wait_time_load) if wait_time_load.isdigit() else 2,
            'wait_time_server': int(wait_time_server) if wait_time_server.isdigit() else 8,
            'wait_time_open_trainjx': int(wait_time_open_trainjx) if wait_time_open_trainjx.isdigit() else 2,
            'wait_time_load_autovlbs': int(wait_time_load_autovlbs) if wait_time_load_autovlbs.isdigit() else 3,
            'try_number': int(try_number) if try_number.isdigit() else 3,
            'global_time_sleep': int(edit_global_time_sleep) if edit_global_time_sleep.isdigit() else 2,
            'hide_effects': int(hide_effects),
            'start_up': int(start_up)
        }]
        
        # Lưu dữ liệu vào file JSON
        self.data_manager.save_data(data)
        self.data_manager.save_global_time_data(global_time_data)
        
        # Reload auto data to global variable
        # auto_tool_path = START_LOGIN.load_auto_tool_path()
        # sleepTime = START_LOGIN.load_sleepTime()
        
        if int(start_up) == 1:
            self.set_startup(True)
        else:
            self.set_startup(False)
        
        messagebox.showinfo("Success", "Đã lưu thành công dữ liệu Auto Tool!")
    
    def browse_auto_path(self):
        """Chọn file đường dẫn auto"""
        file_path = filedialog.askopenfilename(
            title="Chọn đường dẫn AutoVLBS 1.9",
            filetypes=(("Executable Files", "*.exe"), ("All Files", "*.*"))
        )
        if file_path:
            self.entry_auto_path.delete(0, tk.END)
            self.entry_auto_path.insert(0, file_path)
            new_auto_tool_path = self.entry_auto_path.get().strip()
            
            if not new_auto_tool_path:
                messagebox.showwarning("Warning", "Vui lòng nhập đường dẫn tool auto!")
                return
    
    def set_startup(self, enable: bool):
        """Tạo hoặc xóa shortcut trong Startup để chạy quick_run.bat khi mở máy."""
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        PARENT_DIR = os.path.dirname(CURRENT_DIR)
        PARENT_DIR = os.path.dirname(PARENT_DIR)
        QUICK_RUN_PATH = os.path.join(PARENT_DIR, "quick_run.vbs")
        
        startup_folder = winshell.startup()
        shortcut_path = os.path.join(startup_folder, "QuickRun.lnk")
        
        if enable:
            if not os.path.exists(shortcut_path):
                target = QUICK_RUN_PATH
                working_dir = os.path.dirname(target)
                
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = target
                shortcut.WorkingDirectory = working_dir
                shortcut.save()
                print(f"✅ Đã tạo shortcut: {shortcut_path}")
            else:
                print("ℹ️ Shortcut đã tồn tại.")
        else:
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                print("❌ Đã xóa shortcut, ứng dụng sẽ không tự chạy nữa.")
            else:
                print("ℹ️ Không có shortcut để xóa.")
