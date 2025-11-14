# ===============================
# TAB QUẢN LÝ TÀI KHOẢN
# ===============================

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import json
import os
import GlobalFunction as GF
import realTimeCheckBugAutoVLBS as REAL_TIME_CHECK

class AccountManagerTab:
    def __init__(self, parent, data_manager, callbacks):
        """
        Khởi tạo tab Quản lý Tài khoản
        
        Args:
            parent: Widget cha (notebook)
            data_manager: Object quản lý dữ liệu (chứa các hàm load/save data)
            callbacks: Dictionary chứa các callback functions
        """
        self.parent = parent
        self.data_manager = data_manager
        self.callbacks = callbacks
        
        # Biến toàn cục
        self.editting_account = None
        self.pass_accounts = []
        self.data = {}
        
        # Biến checkbox
        self.varCheckBox = tk.IntVar()
        self.varGomCheckBox = tk.IntVar()
        self.varXe2CheckBox = tk.IntVar()
        self.varMoGameLau = tk.IntVar()
        
        # Tạo giao diện
        self.create_ui()
    
    def create_ui(self):
        """Tạo giao diện cho tab"""
        # Frame thông tin nhập
        input_frame = ttk.LabelFrame(self.parent, text="Thông tin tài khoản", padding=(10, 5))
        input_frame.pack(padx=5, pady=10, fill="x")
        
        # Lưu reference để các hàm khác có thể truy cập
        self.input_frame = input_frame
        
        # Tạo các widget nhập liệu
        self._create_input_widgets(input_frame)
        
        # Tạo các nút chức năng
        self._create_buttons(input_frame)
        
        # Tạo Treeview hiển thị danh sách tài khoản
        self._create_treeview()
    
    def _create_input_widgets(self, parent):
        """Tạo các widget nhập liệu"""
        # Nhập Username, Password, Ingame
        ttk.Label(parent, text="Username, pass, ingame:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_username = ttk.Entry(parent)
        self.entry_username.grid(row=0, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
        
        self.entry_password = ttk.Entry(parent)
        self.entry_password.grid(row=0, column=2, columnspan=1, padx=5, pady=5, sticky="ew")
        
        self.entry_ingame = ttk.Entry(parent)
        self.entry_ingame.grid(row=0, column=3, columnspan=1, padx=5, pady=5, sticky="ew")
        
        # Frame server
        server_frame = ttk.Frame(parent)
        server_frame.grid(row=1, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
        server_frame.columnconfigure(0, weight=8)
        server_frame.columnconfigure(1, weight=2)
        
        # Nhập Server
        ttk.Label(parent, text="Server:").grid(row=1, column=0, padx=5, pady=5)
        
        # Load servers data
        servers_data = GF.read_config_file('servers.json')
        self.servers = servers_data['servers']
        server_names = list(self.servers.keys())
        
        self.selected_server = tk.StringVar(value="Chọn server")
        self.servers_dropdown = ttk.Combobox(server_frame, textvariable=self.selected_server, 
                                             values=server_names, state="readonly")
        self.servers_dropdown.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.servers_dropdown.bind("<<ComboboxSelected>>", self.on_server_select)
        
        # Reload server button
        reload_server_button = ttk.Button(server_frame, text="🗘", command=self.reload_server)
        reload_server_button.grid(row=0, column=1, sticky="ew")
        
        # Checkbox mở game lâu
        self.mo_game_lau_checkbox = tk.Checkbutton(parent, text="Server mở game lâu", 
                                                    variable=self.varMoGameLau, 
                                                    command=lambda: self.check_checkbox(self.varMoGameLau))
        self.mo_game_lau_checkbox.grid(row=1, column=2, columnspan=1)
        
        # Frame ẩn game và hiệu ứng
        hide_frame = ttk.Frame(parent)
        hide_frame.grid(row=1, column=3, columnspan=1, padx=5, pady=5, sticky="ew")
        hide_frame.columnconfigure(0, weight=5)
        hide_frame.columnconfigure(1, weight=5)
        
        hide_game_button = ttk.Button(hide_frame, text="Ẩn tất cả game", 
                                      command=lambda: GF.hideWindow("Vo Lam Truyen Ky"))
        hide_game_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        hide_effects_button = ttk.Button(hide_frame, text="Ẩn hiệu ứng", 
                                        command=lambda: GF.hide_effects_all())
        hide_effects_button.grid(row=0, column=1, sticky="ew")
        
        # Nhập Game Path
        ttk.Label(parent, text="Đường dẫn Game:").grid(row=2, column=0, padx=5, pady=5)
        self.entry_game_path = ttk.Entry(parent)
        self.entry_game_path.grid(row=2, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
        
        # Nhập AutoUpdate Path
        ttk.Label(parent, text="Đường dẫn AutoUpdate:").grid(row=3, column=0, padx=5, pady=5)
        self.entry_auto_update_path = ttk.Entry(parent)
        self.entry_auto_update_path.grid(row=3, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
        
        # Nút chọn đường dẫn game
        browse_button = ttk.Button(parent, text="Chọn đường dẫn", command=self.browse_game_path)
        browse_button.grid(row=2, column=2, padx=5, pady=5, sticky="ew")
        
        update_path_button = ttk.Button(parent, text="Cập nhật đường dẫn", command=self.update_path)
        update_path_button.grid(row=2, column=3, padx=5, pady=5, sticky="ew")
        
        # Checkbox gom tiền và KPI
        gom_frame = ttk.Frame(parent)
        gom_frame.grid(row=3, column=2, columnspan=1, padx=5, pady=5, sticky="ew")
        
        self.gom_checkbox = tk.Checkbutton(gom_frame, text="TK gom", variable=self.varGomCheckBox, 
                                          command=self.on_gom_checkbox_change)
        self.gom_checkbox.pack(side="left")
        
        # KPI cho tài khoản gom (chỉ hiện khi tick TK gom)
        ttk.Label(gom_frame, text="KPI:").pack(side="left", padx=(10, 2))
        self.entry_kpi_gom = ttk.Entry(gom_frame, width=8)
        self.entry_kpi_gom.pack(side="left")
        self.entry_kpi_gom.insert(0, "")  # Để trống = dùng default
        self.entry_kpi_gom.config(state="disabled")  # Disable mặc định
        
        # Frame số lần xuống
        small_frame = ttk.Frame(parent, width=10)
        small_frame.grid(row=3, column=3, columnspan=1, padx=0, pady=0)
        
        ttk.Label(small_frame, text="Chọn server").pack(side="left", padx=(0, 2))
        self.entry_solanxuong = ttk.Entry(small_frame, width=4)
        self.entry_solanxuong.pack(side="left", padx=(0, 2))
        
        self.entry_solanxuong2 = ttk.Entry(small_frame, width=4)
        self.entry_solanxuong2.pack(side="right", padx=(2, 0))
    
    def _create_buttons(self, parent):
        """Tạo các nút chức năng CRUD"""
        # Frame chứa các nút CRUD
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=4, column=0, columnspan=4, pady=10)
        
        # Các nút quản lý tài khoản
        add_button = ttk.Button(button_frame, text="➕ Thêm", 
                               command=self.add_account)
        add_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.edit_button = ttk.Button(button_frame, text="✏️ Sửa", command=self.edit_account)
        self.edit_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.update_button = ttk.Button(button_frame, text="💾 Cập nhật", 
                                       command=self.update_account)
        self.cancel_button = ttk.Button(button_frame, text="❌ Hủy", 
                                       command=lambda: (self.update_button.grid_forget(), 
                                                       self.cancel_button.grid_forget(), 
                                                       self.edit_button.grid(row=0, column=1, padx=5, pady=5)))
        
        delete_button = ttk.Button(button_frame, text="🗑️ Xoá", 
                                   command=self.delete_account)
        delete_button.grid(row=0, column=2, padx=5, pady=5)
        
        cancel_button2 = ttk.Button(button_frame, text="❌ Hủy", command=self.cancel_edit)
        cancel_button2.grid(row=0, column=3, padx=5, pady=5)
        cancel_button2.grid_remove()
        
        # Separator
        ttk.Separator(parent, orient='horizontal').grid(row=5, column=0, columnspan=4, sticky='ew', pady=10)
        
        # Frame Update App
        update_frame = ttk.LabelFrame(parent, text="🔄 Cập nhật ứng dụng", padding=(10, 5))
        update_frame.grid(row=6, column=0, columnspan=4, padx=10, pady=5, sticky="ew")
        
        update_app_button = ttk.Button(update_frame, text="Kiểm tra cập nhật", 
                                       command=self.callbacks.get('update_app'))
        update_app_button.pack(side="left", padx=5, pady=5)
        
        alway_update_app_button = ttk.Button(update_frame, text="Cập nhật ngay", 
                                            command=self.callbacks.get('alway_update_app'))
        alway_update_app_button.pack(side="left", padx=5, pady=5)
    
    def _create_treeview(self):
        """Tạo Treeview hiển thị danh sách tài khoản"""
        tree_frame = ttk.LabelFrame(self.parent, text="Danh sách tài khoản", padding=(10, 5))
        tree_frame.pack(padx=5, pady=10, fill="x")
        
        # Chỉ hiển thị các cột cần thiết (bỏ is_select và is_logged_in)
        columns = ("stt", "username", "ingame", "game_path", 
                  "is_gom_tien", "is_xe_2", "so_lan_xuong", "so_lan_xuong2")
        self.tree_accounts = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        
        # Thiết lập heading
        self.tree_accounts.heading("stt", text="STT")
        self.tree_accounts.heading("username", text="Username")
        self.tree_accounts.heading("ingame", text="Ingame")
        self.tree_accounts.heading("game_path", text="PathGame")
        self.tree_accounts.heading("is_gom_tien", text="Tk gom tiền")
        self.tree_accounts.heading("is_xe_2", text="Xe 2")
        self.tree_accounts.heading("so_lan_xuong", text="Số lần xuống cum server")
        self.tree_accounts.heading("so_lan_xuong2", text="Số lần xuống server")
        
        # Thiết lập column width
        self.tree_accounts.column("stt", width=40, anchor="center")
        self.tree_accounts.column("username", width=120)
        self.tree_accounts.column("ingame", width=120)
        self.tree_accounts.column("game_path", width=250)
        self.tree_accounts.column("is_gom_tien", width=80, anchor="center")
        self.tree_accounts.column("is_xe_2", width=50, anchor="center")
        self.tree_accounts.column("so_lan_xuong", width=80, anchor="center")
        self.tree_accounts.column("so_lan_xuong2", width=80, anchor="center")
        
        # Tạo thanh cuộn
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_accounts.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_accounts.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree_accounts.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_accounts.configure(xscrollcommand=h_scrollbar.set)
        
        self.tree_accounts.pack(fill="both", expand=True)
        
        # Bind events
        self.tree_accounts.bind("<Double-1>", self.on_item_select)
        self.tree_accounts.bind("<Button-1>", self.on_heading_click)
    
    # ==================== HELPER METHODS ====================
    
    def check_checkbox(self, var):
        """Kiểm tra trạng thái checkbox"""
        return var.get()
    
    def on_gom_checkbox_change(self):
        """Xử lý khi thay đổi checkbox TK gom"""
        if self.varGomCheckBox.get():
            # Enable KPI input khi tick TK gom
            self.entry_kpi_gom.config(state="normal")
        else:
            # Disable KPI input khi bỏ tick
            self.entry_kpi_gom.config(state="disabled")
            self.entry_kpi_gom.delete(0, tk.END)
    
    def check_exist_account(self, username, gamepath, data):
        """Kiểm tra tài khoản tồn tại"""
        for account in data['accounts']:
            if account.get('username') == username and account.get('game_path') == gamepath:
                return True
        return False
    
    # ==================== DATA METHODS ====================
    
    def load_to_gui(self):
        """Hiển thị dữ liệu từ file JSON lên giao diện"""
        self.data = self.data_manager.load_data()
        
        # Xóa dữ liệu hiện tại trong Treeview
        for i in self.tree_accounts.get_children():
            self.tree_accounts.delete(i)
        
        # Hiển thị danh sách tài khoản (bỏ cột Bỏ qua và Trạng thái)
        stt = 1
        for account in self.data['accounts']:
            is_gom_tien_display = "✓" if account['is_gom_tien'] else ""
            is_xe_2_display = "✓" if account['is_xe_2'] else ""
            
            try:
                so_lan_xuong_display = account['so_lan_xuong']
            except:
                so_lan_xuong_display = ""
            
            try:
                so_lan_xuong2_display = account['so_lan_xuong2']
            except:
                so_lan_xuong2_display = ""
            
            self.tree_accounts.insert("", "end", values=(
                stt,
                account['username'],
                account['ingame'],
                account['game_path'],
                is_gom_tien_display,
                is_xe_2_display,
                so_lan_xuong_display,
                so_lan_xuong2_display
            ))
            stt += 1
        
        # Render profit table và current online accounts (Tắt để không làm to giao diện)
        # try:
        #     entry_title_mail = self.callbacks.get('get_entry_title_mail')()
        #     currentAutoName = self.callbacks.get('get_current_auto_name')()
        #     REAL_TIME_CHECK.render_profit_table_ui(self.monitor_money_frame, entry_title_mail)
        #     REAL_TIME_CHECK.render_current_online_accounts(self.current_online_frame, currentAutoName)
        # except:
        #     pass
    
    def add_account(self):
        """Thêm tài khoản mới"""
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        ingame = self.entry_ingame.get().strip()
        game_path = self.entry_game_path.get().strip()
        # Xử lý cả trường hợp game.exe và Game.exe
        auto_update_path = game_path
        if game_path.lower().endswith('game.exe'):
            auto_update_path = game_path[:-8] + 'AutoUpdate.exe'
        solanxuong = self.entry_solanxuong.get().strip()
        solanxuong2 = self.entry_solanxuong2.get().strip()
        
        if not username or not password or not game_path:
            messagebox.showwarning("Warning", "Vui lòng nhập đủ thông tin!")
            return
        
        data = self.data_manager.load_data()
        
        if self.check_exist_account(username, game_path, data):
            messagebox.showwarning("Warning", "Tài khoản đã có trong dữ liệu!")
            return
        
        new_account = {
            'is_select': False,
            'username': username,
            'password': password,
            'ingame': ingame,
            'game_path': game_path,
            'auto_update_path': auto_update_path,
            'is_logged_in': False,
            'is_gom_tien': self.check_checkbox(self.varGomCheckBox),
            'kpi_gom': self.entry_kpi_gom.get().strip() if self.check_checkbox(self.varGomCheckBox) else "",
            'is_xe_2': self.check_checkbox(self.varXe2CheckBox),
            'so_lan_xuong': solanxuong if solanxuong else 1,
            'so_lan_xuong2': solanxuong2 if solanxuong2 else 0,
            'mo_game_lau': self.check_checkbox(self.varMoGameLau)
        }
        
        data['accounts'].append(new_account)
        self.data_manager.save_data(data)
        self.load_to_gui()
        
        self.entry_username.delete(0, tk.END)
        self.entry_ingame.delete(0, tk.END)
        
        self.update_button.grid_forget()
        self.cancel_button.grid_forget()
        self.edit_button.grid(row=0, column=1, padx=5, pady=10)
    
    def edit_account(self):
        """Hiển thị thông tin tài khoản đã chọn lên vùng trên cùng để chỉnh sửa"""
        selected_item = self.tree_accounts.selection()
        
        if selected_item:
            values = self.tree_accounts.item(selected_item)['values']
            # Columns hiện tại: stt(0), username(1), ingame(2), game_path(3), is_gom_tien(4), is_xe_2(5), so_lan_xuong(6), so_lan_xuong2(7)
            
            self.entry_username.delete(0, tk.END)
            self.entry_username.insert(0, values[1])  # username ở index 1
            
            self.entry_password.delete(0, tk.END)
            self.entry_game_path.delete(0, tk.END)
            self.entry_auto_update_path.delete(0, tk.END)
            self.entry_solanxuong.delete(0, tk.END)
            self.entry_solanxuong2.delete(0, tk.END)
            self.entry_ingame.delete(0, tk.END)
            
            # Tìm dữ liệu gốc
            data = self.data_manager.load_data()
            index = self.tree_accounts.index(selected_item[0])
            
            original_password = data['accounts'][index]['password']
            self.entry_password.insert(0, original_password)
            
            original_ingame = data['accounts'][index]['ingame']
            self.entry_ingame.insert(0, original_ingame)
            
            game_path = values[3]  # game_path ở index 3
            self.entry_game_path.insert(0, game_path)
            # Xử lý cả trường hợp game.exe và Game.exe
            auto_update_path = game_path
            if game_path.lower().endswith('game.exe'):
                auto_update_path = game_path[:-8] + 'AutoUpdate.exe'
            self.entry_auto_update_path.insert(0, auto_update_path)
            
            if data['accounts'][index]['is_gom_tien'] == 1:
                self.gom_checkbox.select()
                # Load KPI nếu có, nếu không thì hiển thị default
                kpi_gom = data['accounts'][index].get('kpi_gom', '')
                self.entry_kpi_gom.config(state="normal")
                self.entry_kpi_gom.delete(0, tk.END)
                if kpi_gom:
                    # Có KPI riêng
                    self.entry_kpi_gom.insert(0, kpi_gom)
                else:
                    # Chưa có KPI riêng, hiển thị default
                    from modules.config import DEFAULT_KPI_GOM
                    self.entry_kpi_gom.insert(0, DEFAULT_KPI_GOM)
            else:
                self.gom_checkbox.deselect()
                self.entry_kpi_gom.config(state="disabled")
                self.entry_kpi_gom.delete(0, tk.END)
            
            if data['accounts'][index]['is_xe_2'] == 1:
                self.mo_game_lau_checkbox.select()
            else:
                self.mo_game_lau_checkbox.deselect()
            
            try:
                if data['accounts'][index]['mo_game_lau'] == 1:
                    self.mo_game_lau_checkbox.select()
                else:
                    self.mo_game_lau_checkbox.deselect()
            except:
                self.mo_game_lau_checkbox.deselect()
            
            self.entry_solanxuong.insert(0, values[6])  # so_lan_xuong ở index 6
            self.entry_solanxuong2.insert(0, values[7])  # so_lan_xuong2 ở index 7
            
            # Lưu tài khoản đang chỉnh sửa (username ở index 1)
            self.editting_account = values[1]
            
            # Ẩn nút Edit và hiện nút Update cùng nút Cancel
            self.edit_button.grid_forget()
            self.update_button.grid(row=0, column=1, padx=5, pady=10)
            self.cancel_button.grid(row=0, column=2, padx=5, pady=10)
    
    def update_account(self):
        """Cập nhật tài khoản đã chỉnh sửa"""
        selected_item = self.tree_accounts.selection()
        
        if selected_item:
            # username ở index 1
            if self.tree_accounts.item(selected_item)['values'][1] != self.editting_account:
                messagebox.showwarning("Warning", "Vui lòng chọn tài khoản đang chỉnh sửa!")
                return
            
            index = self.tree_accounts.index(selected_item[0])
            data = self.data_manager.load_data()
            
            data['accounts'][index] = {
                'is_select': data['accounts'][index].get('is_select', False),
                'username': self.entry_username.get(),
                'password': self.entry_password.get(),
                'ingame': data['accounts'][index]['ingame'],
                'game_path': self.entry_game_path.get(),
                'auto_update_path': auto_update_path,  # Sử dụng biến đã xử lý ở trên
                'is_logged_in': data['accounts'][index].get('is_logged_in', False),
                'is_gom_tien': self.check_checkbox(self.varGomCheckBox),
                'kpi_gom': self.entry_kpi_gom.get().strip() if self.check_checkbox(self.varGomCheckBox) else "",
                'is_xe_2': self.check_checkbox(self.varXe2CheckBox),
                'so_lan_xuong': self.entry_solanxuong.get(),
                'so_lan_xuong2': self.entry_solanxuong2.get(),
                'mo_game_lau': self.check_checkbox(self.varMoGameLau)
            }
            
            self.data_manager.save_data(data)
            self.load_to_gui()
            
            self.entry_username.delete(0, tk.END)
            self.entry_password.delete(0, tk.END)
            self.entry_ingame.delete(0, tk.END)
            self.entry_game_path.delete(0, tk.END)
            self.entry_auto_update_path.delete(0, tk.END)
            self.entry_solanxuong.delete(0, tk.END)
            self.entry_solanxuong2.delete(0, tk.END)
            
            self.update_button.grid_forget()
            self.cancel_button.grid_forget()
            self.edit_button.grid(row=0, column=1, padx=5, pady=10)
    
    def delete_account(self):
        """Xoá tài khoản đã chọn"""
        selected_item = self.tree_accounts.selection()
        if selected_item:
            index = self.tree_accounts.index(selected_item)
            confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xoá tài khoản này?")
            if confirm:
                del self.data['accounts'][index]
                self.data_manager.save_data(self.data)
                self.load_to_gui()
        else:
            messagebox.showwarning("Warning", "Vui lòng chọn tài khoản để xóa!")
    
    def cancel_edit(self):
        """Hủy bỏ chỉnh sửa"""
        self.entry_username.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)
        self.entry_game_path.delete(0, tk.END)
        self.entry_auto_update_path.delete(0, tk.END)
        self.entry_solanxuong.delete(0, tk.END)
        self.entry_solanxuong2.delete(0, tk.END)
        self.entry_ingame.delete(0, tk.END)
        
        self.update_button.grid_forget()
        self.cancel_button.grid_forget()
        self.edit_button.grid(row=0, column=1, padx=5, pady=10)
    
    # ==================== EVENT HANDLERS ====================
    
    def on_item_select(self, event):
        """Xử lý sự kiện double click vào item"""
        selected_item = self.tree_accounts.selection()[0]
        values = self.tree_accounts.item(selected_item, 'values')
        stt = int(values[0]) - 1
        
        account = self.data['accounts'][stt]
        account['is_select'] = not account['is_select']
        
        is_select_display = "✓" if account['is_select'] else ""
        if account['is_select']:
            self.pass_accounts.append(account['username'])
        else:
            self.pass_accounts.remove(account['username'])
        
        print(self.pass_accounts)
        self.tree_accounts.item(selected_item, values=(
            values[0], is_select_display, values[2], values[3], values[4], values[5], values[6], values[7]
        ))
    
    def on_heading_click(self, event):
        """Xử lý sự kiện click vào heading"""
        try:
            region = self.tree_accounts.identify_region(event.x, event.y)
            column = self.tree_accounts.identify_column(event.x)
            heading_name = self.tree_accounts.heading(column)["text"]
            
            if region == "heading" and column == "#2":
                for item_id in self.tree_accounts.get_children():
                    values = self.tree_accounts.item(item_id, 'values')
                    stt = int(values[0]) - 1
                    account = self.data['accounts'][stt]
                    account['is_select'] = not account['is_select']
                    
                    is_select_display = "✓" if account['is_select'] else ""
                    if account['is_select']:
                        self.pass_accounts.append(account['username'])
                    else:
                        self.pass_accounts.remove(account['username'])
                    
                    self.tree_accounts.item(item_id, values=(
                        values[0], is_select_display, values[2], values[3], values[4], values[5], values[6], values[7]
                    ))
                print(self.pass_accounts)
            
            elif region == "heading" and column == "#5":
                if heading_name == 'Servers':
                    self.tree_accounts.heading(column, text='PathGame')
                    self.update_server_to_pathgame()
                else:
                    self.tree_accounts.heading(column, text='Servers')
                    self.update_pathgame_to_server()
        except Exception as e:
            print("Lỗi double click: ", str(e))
    
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
    
    # ==================== SERVER METHODS ====================
    
    def browse_game_path(self):
        """Chọn file đường dẫn game"""
        file_path = filedialog.askopenfilename(
            title="Chọn đường dẫn Game",
            initialfile="game.exe",
            filetypes=(("Executable Files", "*.exe"), ("All Files", "*.*"))
        )
        if file_path:
            self.entry_game_path.delete(0, tk.END)
            self.entry_game_path.insert(0, file_path)
            self.entry_auto_update_path.delete(0, tk.END)
            # Xử lý cả trường hợp game.exe và Game.exe
            auto_update_path = file_path
            if file_path.lower().endswith('game.exe'):
                auto_update_path = file_path[:-8] + 'AutoUpdate.exe'
            self.entry_auto_update_path.insert(0, auto_update_path)
    
    def reload_server(self):
        """Reload danh sách server"""
        with open(os.path.join(GF.join_directory_data(), "accounts.json"), "r", encoding="utf-8") as f:
            accounts_data = json.load(f)
        
        with open(os.path.join(GF.join_directory_config(), 'servers.json'), "r", encoding="utf-8") as f:
            servers_data = json.load(f)
        
        new_servers = {}
        seen_paths = set()
        
        for acc in accounts_data.get("accounts", []):
            path = acc.get("game_path")
            if not path or not path.lower().endswith("game.exe"):
                continue
            
            if path not in seen_paths:
                folder_name = os.path.basename(os.path.dirname(path))
                new_servers[folder_name] = path
                seen_paths.add(path)
        
        servers_data["servers"] = new_servers
        
        with open(os.path.join(GF.join_directory_config(), 'servers.json'), "w", encoding="utf-8") as f:
            json.dump(servers_data, f, indent=4, ensure_ascii=False)
        
        server_names = list(new_servers.keys())
        self.servers_dropdown["values"] = server_names
        self.servers = new_servers
        
        print("✅ Đã cập nhật servers.json thành công!")
    
    def on_server_select(self, event):
        """Xử lý khi chọn server"""
        server = self.selected_server.get()
        path = self.servers[server]
        game_path = path
        self.entry_game_path.insert(0, game_path)
        self.entry_auto_update_path.delete(0, tk.END)
        # Xử lý cả trường hợp game.exe và Game.exe
        auto_update_path = game_path
        if game_path.lower().endswith('game.exe'):
            auto_update_path = game_path[:-8] + 'AutoUpdate.exe'
        self.entry_auto_update_path.insert(0, auto_update_path)
        print(f"Server đã chọn: {server}")
        print(f"Đường dẫn: {path}")
    
    def update_path(self):
        """Cập nhật path của server"""
        server = self.selected_server.get()
        new_path = self.entry_game_path.get()
        
        if server and new_path:
            self.servers[server] = new_path
            servers_data = GF.read_config_file('servers.json')
            servers_data["servers"] = self.servers
            
            with open(os.path.join(GF.join_directory_config(), 'servers.json'), 'w') as file:
                json.dump(servers_data, file, ensure_ascii=True, indent=4)
            print(f"Path của server '{server}' đã được cập nhật thành:\n{new_path}")
        else:
            print("Vui lòng chọn server và nhập đường dẫn mới.")
    
    def update_pathgame_to_server(self):
        """Cập nhật hiển thị từ path game sang tên server"""
        for child in self.tree_accounts.get_children():
            item = self.tree_accounts.item(child)
            game_path = item["values"][4]
            server_name = "Lỗi"
            for server, path in self.servers.items():
                if game_path == path:
                    server_name = server
                    break
            self.tree_accounts.set(child, "game_path", server_name)
    
    def update_server_to_pathgame(self):
        """Cập nhật hiển thị từ tên server sang path game"""
        for child in self.tree_accounts.get_children():
            item = self.tree_accounts.item(child)
            name = item["values"][4]
            path_name = "Lỗi"
            for server, path in self.servers.items():
                if name == server:
                    path_name = path
                    break
            self.tree_accounts.set(child, "game_path", path_name)
    
    def update_status_to_logged_in(self, username):
        """Cập nhật trạng thái đã login"""
        for item in self.tree_accounts.get_children():
            account_username = self.tree_accounts.item(item, "values")[2]
            if account_username == username:
                self.tree_accounts.set(item, "is_logged_in", "Login(1)")
                break
    
    def get_pass_accounts(self):
        """Lấy danh sách pass accounts"""
        return self.pass_accounts
    
    def clear_pass_accounts(self):
        """Xóa danh sách pass accounts"""
        self.pass_accounts.clear()
