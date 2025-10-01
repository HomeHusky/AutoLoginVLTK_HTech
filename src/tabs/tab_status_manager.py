# ===============================
# TAB QUẢN LÝ TRẠNG THÁI TÀI KHOẢN
# ===============================

import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import threading
import datetime
import GlobalFunction as GF
import checkAcountMoneyAndInfo
import client
import fixErrorAccounts as FIX_ERROR_ACCOUNTS

class StatusManagerTab:
    def __init__(self, parent, data_manager, callbacks):
        """
        Khởi tạo tab Quản lý Trạng thái
        
        Args:
            parent: Widget cha (notebook)
            data_manager: Object quản lý dữ liệu
            callbacks: Dictionary chứa các callback functions
        """
        self.parent = parent
        self.data_manager = data_manager
        self.callbacks = callbacks
        
        # Biến quản lý thread
        self.monitor_thread = None
        self.is_running_monitor = False
        self.stop_monitor_event = threading.Event()
        
        # Biến test code
        self.is_testing_code = False
        
        # Tạo giao diện
        self.create_ui()
    
    def create_ui(self):
        """Tạo giao diện cho tab"""
        # Frame trạng thái
        status_frame = tk.Frame(self.parent)
        status_frame.pack(side="right", padx=10, pady=10)
        
        self.status_canvas = tk.Canvas(status_frame, width=40, height=40)
        self.status_canvas.pack()
        
        # Treeview thông tin tiền vạn
        tree_money_frame = ttk.LabelFrame(self.parent, text="Tiền vạn theo thời gian", padding=(10, 5))
        tree_money_frame.pack(padx=5, pady=10, fill="x")
        
        button_money_frame = ttk.Frame(self.parent, padding=(10, 5))
        button_money_frame.pack(padx=5, pady=10, fill="x")
        
        self.button_money_frame = button_money_frame
        
        # Tạo Treeview
        money_columns = ("stt", "ingame", "tong_tien", "thu_nhap", "thoi_gian", "TDP/C", "ban_do", "server")
        self.tree_money_accounts = ttk.Treeview(tree_money_frame, columns=money_columns, show="headings", height=10)
        
        self.tree_money_accounts.heading("stt", text="Stt")
        self.tree_money_accounts.heading("ingame", text="Tên nv")
        self.tree_money_accounts.heading("tong_tien", text="Tổng tiền")
        self.tree_money_accounts.heading("thu_nhap", text="Thu nhập")
        self.tree_money_accounts.heading("thoi_gian", text="Thời gian")
        self.tree_money_accounts.heading("TDP/C", text="TDP/C")
        self.tree_money_accounts.heading("ban_do", text="Bản đồ")
        self.tree_money_accounts.heading("server", text="Server")
        
        self.tree_money_accounts.column("stt", width=50)
        self.tree_money_accounts.column("ingame", width=100)
        self.tree_money_accounts.column("tong_tien", width=100)
        self.tree_money_accounts.column("thu_nhap", width=80)
        self.tree_money_accounts.column("thoi_gian", width=80)
        self.tree_money_accounts.column("TDP/C", width=80)
        self.tree_money_accounts.column("ban_do", width=80)
        self.tree_money_accounts.column("server", width=80)
        self.tree_money_accounts.pack(fill="both", expand=True)
        
        # Tạo frame trái để hiển thị tất cả tài khoản
        frame_left = ttk.LabelFrame(self.parent, text="Tài khoản", padding=(10, 5))
        frame_left.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        
        # Tạo frame phải để hiển thị các tài khoản đã chọn
        frame_right = ttk.LabelFrame(self.parent, text="Tài khoản gom vạn", padding=(10, 5))
        frame_right.pack(side="right", expand=True, fill="both", padx=10, pady=10)
        
        # Tạo frame giữa chứa nút chuyển đổi
        frame_middle = ttk.Frame(self.parent)
        frame_middle.pack(side="left", padx=10)
        
        # Tạo listbox hiển thị tất cả tài khoản
        self.listbox_left = tk.Listbox(frame_left, selectmode=tk.MULTIPLE, width=30, height=15)
        self.listbox_left.pack(expand=True, fill="both")
        
        # Tạo listbox hiển thị các tài khoản đã chọn
        self.listbox_right = tk.Listbox(frame_right, selectmode=tk.MULTIPLE, width=30, height=15)
        self.listbox_right.pack(expand=True, fill="both")
        
        # Tạo nút chuyển từ phải sang trái
        btn_to_left = ttk.Button(frame_middle, text="<", command=self.move_to_all)
        btn_to_left.pack(pady=5)
        
        # Tạo nút chuyển từ trái sang phải
        btn_to_right = ttk.Button(frame_middle, text=">", command=self.move_to_selected)
        btn_to_right.pack(pady=5)
        
        btn_save_gom_accounts = ttk.Button(frame_middle, text="Lưu", command=self.save_gom_account)
        btn_save_gom_accounts.pack(pady=5)
        
        # Tạo các nút chức năng
        self._create_buttons(button_money_frame)
    
    def _create_buttons(self, parent):
        """Tạo các nút chức năng"""
        # Thời gian monitor
        ttk.Label(parent, text="Thời gian(phút):").grid(row=0, column=0, padx=5, pady=5)
        self.entry_monitor_time = ttk.Entry(parent)
        self.entry_monitor_time.grid(row=0, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
        self.entry_monitor_time.insert(0, self.load_monitor_time())
        
        # Tên/Số máy gửi Mail
        ttk.Label(parent, text="Tên/Số máy gửi Mail:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_title_mail = ttk.Entry(parent)
        self.entry_title_mail.grid(row=1, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
        self.entry_title_mail.insert(0, self.load_title_mail())
        
        # Chỉ tiêu
        ttk.Label(parent, text="Chỉ tiêu (Kv/day):").grid(row=0, column=2, padx=5, pady=5)
        self.entry_kpi = ttk.Entry(parent)
        self.entry_kpi.grid(row=0, column=3, columnspan=1, padx=5, pady=5, sticky="ew")
        self.entry_kpi.insert(0, self.load_kpi())
        
        # Tổng server
        ttk.Label(parent, text="Tổng server:").grid(row=0, column=4, padx=5, pady=5)
        self.entry_total_servers = ttk.Entry(parent)
        self.entry_total_servers.grid(row=0, column=5, columnspan=1, padx=5, pady=5, sticky="ew")
        self.entry_total_servers.insert(0, self.load_total_servers())
        
        # Nút test code
        self.test_code_button = ttk.Button(parent, text="Test code", command=self.on_test_code_button_click)
        self.test_code_button.grid(row=1, column=2, padx=10, pady=5)
        
        # Nút cập nhật
        update_money_button = ttk.Button(parent, text="Cập nhật mới nhất", command=self.update_to_tab_money_manager)
        update_money_button.grid(row=1, column=3, padx=10, pady=5)
        
        # Nút theo dõi
        self.monitor_money_button = ttk.Button(parent, text="Theo dõi", command=self.monitor_money_manager)
        self.monitor_money_button.grid(row=1, column=4, padx=10, pady=5)
        
        # Nút send data
        send_data_button = ttk.Button(parent, text="Send data", command=self.send_data)
        send_data_button.grid(row=1, column=5, padx=10, pady=5)
    
    # ==================== DATA METHODS ====================
    
    def load_to_tab_money_manager(self):
        """Load dữ liệu lên tab"""
        data = checkAcountMoneyAndInfo.readAcountMoneyAndInfo()
        if not data:
            return False
        
        # Xóa dữ liệu hiện tại trong Treeview
        for i in self.tree_money_accounts.get_children():
            self.tree_money_accounts.delete(i)
        
        # Thêm dữ liệu vào Treeview
        stt = 1
        for key, item in data.items():
            if item:
                self.tree_money_accounts.insert("", "end", values=(
                    stt,
                    key,
                    item['tong_tien'],
                    item['thu_nhap'],
                    item['thoi_gian'],
                    item['TDP/C'],
                    item['ban_do'],
                    item['server']
                ))
                stt += 1
    
    def run_load_to_tab_money_manager(self):
        """Làm mới dữ liệu"""
        self.load_to_tab_money_manager()
        messagebox.showinfo("Success", "Làm mới thành công.")
    
    def update_to_tab_money_manager(self):
        """Cập nhật dữ liệu"""
        self.save_monitor_time()
        currentAutoName = self.callbacks.get('get_current_auto_name')()
        checkAcountMoneyAndInfo.updateAcountMoneyAndInfo(currentAutoName, self.on_update_success)
        self.load_to_tab_money_manager()
    
    def on_update_success(self):
        """Callback khi cập nhật thành công"""
        print("Cập nhật thành công.")
    
    def monitor_money_manager(self):
        """Theo dõi tài khoản"""
        if not self.is_running_monitor:
            confirm = messagebox.askyesno(
                "Thông báo",
                "Thao tác này sẽ chạy theo dõi tài khoản của các server mà dữ liệu đang có!"
            )
            if confirm:
                self.save_monitor_time()
                self.is_running_monitor = True
                currentAutoName = self.callbacks.get('get_current_auto_name')()
                checkAcountMoneyAndInfo.updateAcountMoneyAndInfo(currentAutoName, self.on_update_success)
                self.update_status_square(self.status_canvas, "theo dõi")
                self.stop_monitor_event.clear()
                self.monitor_money_button.config(text="Dừng")
                
                now = datetime.datetime.now()
                print(f"Đã chạy theo dõi tài khoản vào {now}!")
                self.monitor_thread = threading.Thread(target=checkAcountMoneyAndInfo.check_income_increase, 
                                                      args=(currentAutoName, self.call_from_monitor_thread, 
                                                           self.stop_monitor_event, self.stop_monitor_success))
                self.monitor_thread.daemon = True
                self.monitor_thread.start()
            else:
                return
        else:
            self.is_running_monitor = False
            self.stop_monitor_event.set()
            self.monitor_money_button.config(text="Theo dõi")
    
    def send_data(self):
        """Gửi dữ liệu"""
        client.send_data()
        now = datetime.datetime.now()
        print(f"Đã gửi dữ liệu lúc {now}!")
    
    def stop_monitor_success(self):
        """Callback khi dừng theo dõi thành công"""
        messagebox.showinfo("Success", "Dừng theo dõi thành công.")
        self.update_status_square(self.status_canvas, "không theo dõi")
    
    def call_from_monitor_thread(self):
        """Callback từ monitor thread"""
        self.parent.after(0, self.load_to_tab_money_manager)
    
    def update_status_square(self, canvas, status):
        """Cập nhật trạng thái hiển thị"""
        canvas.delete("all")
        color = "green" if status == "theo dõi" else "red"
        canvas.create_rectangle(5, 5, 35, 35, fill=color)
    
    # ==================== ACCOUNT SELECTION METHODS ====================
    
    def move_to_selected(self):
        """Chuyển tài khoản từ trái sang phải"""
        selected_accounts = self.listbox_left.curselection()
        for i in selected_accounts[::-1]:
            account = self.listbox_left.get(i)
            self.listbox_left.delete(i)
            self.listbox_right.insert(tk.END, account)
    
    def move_to_all(self):
        """Chuyển tài khoản từ phải sang trái"""
        selected_accounts = self.listbox_right.curselection()
        for i in selected_accounts[::-1]:
            account = self.listbox_right.get(i)
            self.listbox_right.delete(i)
            self.listbox_left.insert(tk.END, account)
    
    def save_gom_account(self):
        """Lưu tài khoản gom vạn"""
        selected_accounts = self.listbox_right.get(0, tk.END)
        selected_accounts = list(selected_accounts)
        gom_account_file = 'gom_accounts.json'
        
        # Đọc dữ liệu từ file accounts.json
        data = GF.read_json_file('accounts.json')
        
        # Cập nhật trường is_gom_tien cho từng tài khoản
        for account in data['accounts']:
            if account['ingame'] in selected_accounts:
                account['is_gom_tien'] = 1
            else:
                account['is_gom_tien'] = 0
        
        # Ghi lại toàn bộ dữ liệu vào file accounts.json
        with open(os.path.join(GF.join_directory_data(), 'accounts.json'), 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        
        with open(os.path.join(GF.join_directory_data(), gom_account_file), 'w', encoding='utf-8') as file:
            json.dump(selected_accounts, file, ensure_ascii=False, indent=4)
        
        print(f"Đã cập nhật trường 'is_gom_tien' cho các tài khoản trong accounts.json")
    
    def get_accounts_with_gom_tien(self):
        """Lấy danh sách tài khoản gom tiền"""
        data = GF.read_json_file('accounts.json')
        un_gom_tien_accounts = []
        gom_tien_accounts = []
        for account in data['accounts']:
            if account["ingame"] == "":
                continue
            if account["is_gom_tien"] == 1:
                gom_tien_accounts.append(account["ingame"])
            else:
                un_gom_tien_accounts.append(account["ingame"])
        return un_gom_tien_accounts, gom_tien_accounts
    
    def load_initial_deposit_account(self):
        """Load danh sách tài khoản ban đầu"""
        self.listbox_left.delete(0, tk.END)
        self.listbox_right.delete(0, tk.END)
        all_accounts, gomtien_accounts = self.get_accounts_with_gom_tien()
        for account in all_accounts:
            self.listbox_left.insert(tk.END, account)
        for account in gomtien_accounts:
            self.listbox_right.insert(tk.END, account)
    
    # ==================== CONFIG METHODS ====================
    
    def load_monitor_time(self, filepath='monitor_time.json'):
        """Load thời gian monitor"""
        try:
            with open(os.path.join(GF.join_directory_data(), filepath), 'r') as f:
                data = json.load(f)
                return data['monitor_time']
        except FileNotFoundError:
            return "5"
    
    def load_kpi(self, filepath='monitor_time.json'):
        """Load KPI"""
        try:
            with open(os.path.join(GF.join_directory_data(), filepath), 'r') as f:
                data = json.load(f)
                return data['kpi']
        except FileNotFoundError:
            return "1000"
    
    def load_total_servers(self, filepath='monitor_time.json'):
        """Load tổng số server"""
        try:
            with open(os.path.join(GF.join_directory_data(), filepath), 'r') as f:
                data = json.load(f)
                return data['total_servers']
        except FileNotFoundError:
            return "10"
    
    def load_title_mail(self, filepath='monitor_time.json'):
        """Load tiêu đề mail"""
        try:
            with open(os.path.join(GF.join_directory_data(), filepath), 'r') as f:
                data = json.load(f)
                return data['title_mail']
        except FileNotFoundError:
            return "Máy chủ AutoVLBS"
    
    def save_monitor_time(self, filepath='monitor_time.json'):
        """Lưu thời gian monitor"""
        data = {}
        data['monitor_time'] = self.entry_monitor_time.get().strip()
        data['kpi'] = self.entry_kpi.get().strip()
        data['total_servers'] = self.entry_total_servers.get().strip()
        data['title_mail'] = self.entry_title_mail.get().strip()
        with open(os.path.join(GF.join_directory_data(), filepath), 'w') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    
    # ==================== TEST CODE ====================
    
    def on_test_code_button_click(self):
        """Test code button click"""
        error_accounts_array = []
        error_accounts_array.append({"account": "PT2ÙTLÙHT11"})
        error_accounts_array.append({"account": "PT2ÙTNÙHT11"})
        
        if not self.is_testing_code:
            print("Bắt đầu test_code")
            FIX_ERROR_ACCOUNTS.start_fixing(error_accounts_array)
            self.test_code_button.config(text="Dừng")
            self.is_testing_code = True
        else:
            print("Dừng test code")
            FIX_ERROR_ACCOUNTS.stop_fixing()
            self.test_code_button.config(text="Test code")
            self.is_testing_code = False
    
    def get_entry_title_mail(self):
        """Lấy giá trị entry title mail"""
        return self.entry_title_mail.get().strip()
