# ===============================
# TAB DASHBOARD/MONITOR
# ===============================
"""
Tab Dashboard - Hiển thị trạng thái tài khoản và điều khiển login
Chỉ tập trung vào monitoring và control, không có CRUD
"""

import tkinter as tk
from tkinter import messagebox, ttk
import realTimeCheckBugAutoVLBS as REAL_TIME_CHECK


class DashboardTab:
    def __init__(self, parent, data_manager, callbacks):
        """
        Khởi tạo tab Dashboard
        
        Args:
            parent: Widget cha (notebook)
            data_manager: Object quản lý dữ liệu
            callbacks: Dictionary chứa các callback functions
        """
        self.parent = parent
        self.data_manager = data_manager
        self.callbacks = callbacks
        
        # Biến checkbox
        self.varCheckBox = tk.IntVar()
        
        # Lưu reference đến root window để resize
        self.root = parent.winfo_toplevel()
        
        # Tạo giao diện
        self.create_ui()
    
    def create_ui(self):
        """Tạo giao diện Dashboard"""
        # Frame thống kê với card design - ĐẶT TRÊN CÙNG
        self.create_stats_cards()
        
        # Frame điều khiển chính
        control_frame = ttk.LabelFrame(self.parent, text="🎮 Điều khiển", padding=(15, 10))
        control_frame.pack(padx=10, pady=10, fill="x")
        
        # Row 1: Checkbox Auto click AutoVLBS + Time input + Theo dõi
        row1_frame = ttk.Frame(control_frame)
        row1_frame.pack(fill="x", pady=5)
        
        checkbox = tk.Checkbutton(row1_frame, text="Tự động click AutoVLBS", 
                                 variable=self.varCheckBox,
                                 font=('Segoe UI', 10))
        checkbox.pack(side="left", padx=5)
        
        ttk.Label(row1_frame, text="Thời gian (phút):").pack(side="left", padx=5)
        self.entry_time_check_loop_VLBS = ttk.Entry(row1_frame, width=8)
        self.entry_time_check_loop_VLBS.pack(side="left", padx=5)
        
        self.start_check_fix_VLBS_button = ttk.Button(row1_frame, text="Theo dõi", 
                                                      command=self.on_start_check_fix_VLBS_button_click)
        self.start_check_fix_VLBS_button.pack(side="left", padx=5)
        
        # Row 2: Các nút điều khiển chính
        row2_frame = ttk.Frame(control_frame)
        row2_frame.pack(fill="x", pady=5)
        
        self.start_login_button = ttk.Button(row2_frame, text="▶ Bắt đầu", 
                                            style="Success.TButton",
                                            command=lambda: self.callbacks.get('start_login')(self.varCheckBox.get()))
        self.start_login_button.pack(side="left", padx=5)
        
        self.stop_login_button = ttk.Button(row2_frame, text="⏸ Dừng", 
                                           style="Danger.TButton",
                                           command=self.callbacks.get('stop_login'))
        self.stop_login_button.pack(side="left", padx=5)
        
        self.test_button = ttk.Button(row2_frame, text="🧪 Test", 
                                      style="Warning.TButton",
                                      command=self.callbacks.get('test_accounts'))
        self.test_button.pack(side="left", padx=5)
        
        self.run_auto_update_button = ttk.Button(row2_frame, text="🔄 AutoUpdate", 
                                                 command=self.callbacks.get('run_all_auto_update'))
        self.run_auto_update_button.pack(side="left", padx=5)
        
        # Nút toggle bảng trạng thái
        self.toggle_button = ttk.Button(row2_frame, text="▼ Mở rộng", 
                                       command=self.toggle_account_table)
        self.toggle_button.pack(side="left", padx=5)
        
        # Treeview hiển thị trạng thái tài khoản (ẩn mặc định)
        self.tree_frame = ttk.LabelFrame(self.parent, text="📊 Trạng thái Tài khoản", padding=(15, 10))
        # Không pack ngay, sẽ pack khi nhấn nút
        self.is_table_visible = False
        
        # Chỉ hiển thị các cột cần thiết
        columns = ("stt", "is_select", "ingame", "is_logged_in")
        self.tree_accounts = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=5)
        
        # Thiết lập heading
        self.tree_accounts.heading("stt", text="STT")
        self.tree_accounts.heading("is_select", text="Bỏ qua")
        self.tree_accounts.heading("ingame", text="Tên nhân vật")
        self.tree_accounts.heading("is_logged_in", text="Trạng thái")
        
        # Thiết lập column width
        self.tree_accounts.column("stt", width=60, anchor="center")
        self.tree_accounts.column("is_select", width=80, anchor="center")
        self.tree_accounts.column("ingame", width=200)
        self.tree_accounts.column("is_logged_in", width=120, anchor="center")
        
        # Tạo thanh cuộn
        v_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree_accounts.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_accounts.configure(yscrollcommand=v_scrollbar.set)
        
        self.tree_accounts.pack(fill="both", expand=True)
        
        # Bind events
        self.tree_accounts.bind("<Double-1>", self.on_item_select)
        self.tree_accounts.bind("<Button-1>", self.on_heading_click)
    
    def create_stats_cards(self):
        """Tạo cards thống kê"""
        # Frame thống kê với card design
        stats_container = ttk.LabelFrame(self.parent, text="📈 Thống kê", padding=(15, 10))
        stats_container.pack(padx=10, pady=10, fill="x")
        
        # Card container
        cards_frame = ttk.Frame(stats_container)
        cards_frame.pack(fill="x")
        
        # Card 1: Tổng
        card1 = ttk.Frame(cards_frame, relief="solid", borderwidth=1)
        card1.pack(side="left", padx=5, pady=5, fill="both", expand=True)
        
        ttk.Label(card1, text="📊 TỔNG", 
                 font=('Segoe UI', 9),
                 foreground="#64748b").pack(pady=(5, 0))
        self.label_total = ttk.Label(card1, text="0", 
                                     font=('Segoe UI', 20, 'bold'),
                                     foreground="#1e293b")
        self.label_total.pack(pady=(0, 5))
        
        # Card 2: Online
        card2 = ttk.Frame(cards_frame, relief="solid", borderwidth=1)
        card2.pack(side="left", padx=5, pady=5, fill="both", expand=True)
        
        ttk.Label(card2, text="🟢 ONLINE", 
                 font=('Segoe UI', 9),
                 foreground="#10b981").pack(pady=(5, 0))
        self.label_online = ttk.Label(card2, text="0", 
                                     font=('Segoe UI', 20, 'bold'),
                                     foreground="#10b981")
        self.label_online.pack(pady=(0, 5))
        
        # Card 3: Offline
        card3 = ttk.Frame(cards_frame, relief="solid", borderwidth=1)
        card3.pack(side="left", padx=5, pady=5, fill="both", expand=True)
        
        ttk.Label(card3, text="⚫ OFFLINE", 
                 font=('Segoe UI', 9),
                 foreground="#ef4444").pack(pady=(5, 0))
        self.label_offline = ttk.Label(card3, text="0", 
                                      font=('Segoe UI', 20, 'bold'),
                                      foreground="#ef4444")
        self.label_offline.pack(pady=(0, 5))
        
        # Card 4: Tỷ lệ
        card4 = ttk.Frame(cards_frame, relief="solid", borderwidth=1)
        card4.pack(side="left", padx=5, pady=5, fill="both", expand=True)
        
        ttk.Label(card4, text="📊 TỶ LỆ", 
                 font=('Segoe UI', 9),
                 foreground="#3b82f6").pack(pady=(5, 0))
        self.label_ratio = ttk.Label(card4, text="0%", 
                                     font=('Segoe UI', 20, 'bold'),
                                     foreground="#3b82f6")
        self.label_ratio.pack(pady=(0, 5))
    
    def toggle_account_table(self):
        """Toggle hiển thị/ẩn bảng trạng thái tài khoản + Auto resize window"""
        if self.is_table_visible:
            # Ẩn bảng - Thu nhỏ window
            self.tree_frame.pack_forget()
            self.toggle_button.config(text="▼ Mở rộng")
            self.is_table_visible = False
            # Auto resize - Vừa khít với nội dung
            self.root.update_idletasks()
            width = max(650, self.parent.winfo_reqwidth() + 20)
            height = max(450, self.parent.winfo_reqheight() + 80)
            self.root.geometry(f"{width}x{height}+0+0")
            print(f"🔽 Đã thu gọn bảng trạng thái - {width}x{height}")
        else:
            # Hiện bảng - To window ra
            self.tree_frame.pack(padx=10, pady=10, fill="both", expand=True)
            self.toggle_button.config(text="▲ Thu gọn")
            self.is_table_visible = True
            # Auto resize - Vừa khít với nội dung
            self.root.update_idletasks()
            width = max(650, self.parent.winfo_reqwidth() + 20)
            height = max(750, self.parent.winfo_reqheight() + 80)
            self.root.geometry(f"{width}x{height}+0+0")
            print(f"🔼 Đã mở rộng bảng trạng thái - {width}x{height}")
    
    # ==================== DATA METHODS ====================
    
    def load_to_gui(self):
        """Hiển thị dữ liệu từ file JSON lên giao diện"""
        data = self.data_manager.load_data()
        
        # Xóa dữ liệu hiện tại trong Treeview
        for i in self.tree_accounts.get_children():
            self.tree_accounts.delete(i)
        
        # Đếm số lượng
        total = len(data['accounts'])
        online = 0
        offline = 0
        
        # Hiển thị danh sách tài khoản
        stt = 1
        for account in data['accounts']:
            is_logged_in = account.get('is_logged_in', False)
            is_logged_in_display = "🟢 Online" if is_logged_in else "⚫ Offline"
            is_select_display = "✓" if account.get('is_select', False) else ""
            
            # Đếm online/offline
            if is_logged_in:
                online += 1
            else:
                offline += 1
            
            # Thêm màu cho row
            tags = ('online',) if is_logged_in else ('offline',)
            
            self.tree_accounts.insert("", "end", values=(
                stt,
                is_select_display,
                account['ingame'] if account['ingame'] else account['username'],
                is_logged_in_display
            ), tags=tags)
            stt += 1
        
        # Cấu hình màu cho tags
        self.tree_accounts.tag_configure('online', foreground='#10b981')
        self.tree_accounts.tag_configure('offline', foreground='#64748b')
        
        # Tính tỷ lệ online
        ratio = (online / total * 100) if total > 0 else 0
        
        # Cập nhật thống kê với số lớn
        self.label_total.config(text=f"{total}")
        self.label_online.config(text=f"{online}")
        self.label_offline.config(text=f"{offline}")
        self.label_ratio.config(text=f"{ratio:.1f}%")
    
    def update_status_to_logged_in(self, username):
        """Cập nhật trạng thái đã login"""
        # Reload lại toàn bộ để cập nhật
        self.load_to_gui()
    
    # ==================== EVENT HANDLERS ====================
    
    def on_item_select(self, event):
        """Xử lý sự kiện double click vào item - Toggle bỏ qua"""
        selected_item = self.tree_accounts.selection()
        if not selected_item:
            return
        
        selected_item = selected_item[0]
        values = self.tree_accounts.item(selected_item, 'values')
        stt = int(values[0]) - 1
        
        # Load data và toggle is_select
        data = self.data_manager.load_data()
        account = data['accounts'][stt]
        account['is_select'] = not account['is_select']
        
        # Save data
        self.data_manager.save_data(data)
        
        # Reload GUI
        self.load_to_gui()
    
    def on_heading_click(self, event):
        """Xử lý sự kiện click vào heading - Toggle tất cả"""
        try:
            region = self.tree_accounts.identify_region(event.x, event.y)
            column = self.tree_accounts.identify_column(event.x)
            
            if region == "heading" and column == "#2":  # Cột "Bỏ qua"
                data = self.data_manager.load_data()
                
                # Toggle tất cả
                current_state = data['accounts'][0].get('is_select', False) if data['accounts'] else False
                new_state = not current_state
                
                for account in data['accounts']:
                    account['is_select'] = new_state
                
                # Save và reload
                self.data_manager.save_data(data)
                self.load_to_gui()
        except Exception as e:
            print(f"Lỗi click heading: {e}")
    
    def on_start_check_fix_VLBS_button_click(self):
        """Xử lý sự kiện click nút theo dõi"""
        is_checking = self.callbacks.get('is_checking_fix_vlbs')
        
        if not is_checking():
            print("Bắt đầu kiểm tra fix lỗi VLBS")
            entry_title_mail = self.callbacks.get('get_entry_title_mail')()
            time_check = int(self.entry_time_check_loop_VLBS.get().strip()) if self.entry_time_check_loop_VLBS.get().strip().isdigit() else 60
            REAL_TIME_CHECK.start_checking(time_check, entry_title_mail)
            self.start_check_fix_VLBS_button.config(text="Dừng kiểm tra")
            self.callbacks.get('set_checking_fix_vlbs')(True)
        else:
            print("Dừng kiểm tra fix lỗi VLBS")
            REAL_TIME_CHECK.stop_checking()
            self.start_check_fix_VLBS_button.config(text="Theo dõi")
            self.callbacks.get('set_checking_fix_vlbs')(False)
    
    def get_pass_accounts(self):
        """Lấy danh sách pass accounts"""
        data = self.data_manager.load_data()
        pass_accounts = []
        for account in data['accounts']:
            if account.get('is_select', False):
                pass_accounts.append(account['username'])
        return pass_accounts
    
    def clear_pass_accounts(self):
        """Xóa danh sách pass accounts - Không cần thiết vì load từ data"""
        pass
