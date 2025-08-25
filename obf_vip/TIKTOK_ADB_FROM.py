import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import subprocess
from curl_cffi import requests
import time
import os
import cv2
import numpy as np
from PIL import Image, ImageTk
import re
import json

class TikTokAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HVH TikTok Automation Pro")
        self.root.geometry("1000x700")  # Tăng chiều cao để chứa thêm phần tọa độ
        self.root.configure(bg='#f0f0f0')
        
        # Load saved data
        self.data_file = "tiktok_data.json"
        self.load_data()
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors
        self.bg_color = '#f0f0f0'
        self.frame_color = '#ffffff'
        self.text_color = '#333333'
        self.success_color = '#2ecc71'  # Green
        self.error_color = '#e74c3c'    # Red
        self.warning_color = '#f39c12'  # Orange
        self.info_color = '#3498db'     # Blue
        
        # Configure styles
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.text_color, font=('Helvetica', 9))
        self.style.configure('TLabelFrame', background=self.frame_color, foreground=self.text_color, 
                           bordercolor='#dddddd', lightcolor=self.frame_color, darkcolor=self.frame_color,
                           font=('Helvetica', 9, 'bold'))
        self.style.configure('TButton', background=self.info_color, foreground='white', font=('Helvetica', 9),
                           padding=3, borderwidth=1)
        self.style.map('TButton', 
                      background=[('active', '#2980b9'), ('disabled', '#bdc3c7')],
                      foreground=[('disabled', '#7f8c8d')])
        self.style.configure('Treeview', background='white', foreground=self.text_color, fieldbackground='white',
                           rowheight=20, font=('Helvetica', 9))
        self.style.configure('Treeview.Heading', background='#ecf0f1', foreground=self.text_color,
                           font=('Helvetica', 9, 'bold'))
        self.style.configure('TCombobox', fieldbackground='white', background='white', foreground=self.text_color)
        self.style.configure('TEntry', fieldbackground='white', foreground=self.text_color, insertbackground=self.text_color)
        
        # Variables
        self.threads = []
        self.thread_data = []
        self.devices = []
        self.accounts = []
        self.follow_buttons = []
        self.follow_button_dir = ""
        self.template_threshold = 0.8
        
        # Create main frames with improved layout
        self.create_control_frame()
        self.create_stats_frame()
        
        # Create a paned window for better resizing
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create thread frame in paned window
        self.create_thread_frame()
        
        # Create log frame in paned window
        self.create_log_frame()
        
        # Add frames to paned window
        self.paned_window.add(self.thread_frame, weight=2)
        self.paned_window.add(self.log_frame, weight=1)
        
        # Add follow button frame at the bottom
        self.create_follow_button_frame()
        
        # Add coordinate frame
        self.create_coordinate_frame()
        
        # Initial device scan
        self.scan_devices()
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    def load_follow_buttons(self, dir_path=None, initial_load=False):
        """Load follow button images from a directory"""
        if dir_path is None and not initial_load:
            # Open dialog to choose directory
            dir_path = filedialog.askdirectory(title="Chọn thư mục chứa ảnh nút Follow")
            if not dir_path:
                return
            
            # Save the directory path
            self.follow_button_dir = dir_path
            self.follow_path_label.config(text=dir_path)
            self.save_data()
        
        # If initial load, use saved path
        if initial_load:
            dir_path = self.follow_button_dir
        
        # Clear existing images
        for widget in self.image_frame.winfo_children():
            widget.destroy()
        
        # Reset the list
        self.follow_buttons = []
        
        # Check if directory exists
        if not os.path.isdir(dir_path):
            self.image_status_label.config(text="Thư mục không tồn tại!")
            return
        
        # Get all image files
        image_extensions = ['.png', '.jpg', '.jpeg']
        image_files = [f for f in os.listdir(dir_path) 
                      if os.path.splitext(f)[1].lower() in image_extensions]
        
        if not image_files:
            self.image_status_label.config(text="Không tìm thấy ảnh nào!")
            return
        
        # Load each image and display in the frame
        self.image_status_label.config(text=f"Đang tải {len(image_files)} ảnh...")
        self.root.update()
        
        # Process each image
        for img_file in image_files:
            img_path = os.path.join(dir_path, img_file)
            try:
                # Load image and create thumbnail
                img = Image.open(img_path)
                img.thumbnail((60, 60), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # Create a label for the image
                label = tk.Label(self.image_frame, image=photo, borderwidth=1, relief="solid")
                label.image = photo  # keep a reference
                label.pack(side=tk.LEFT, padx=5, pady=2)
                
                # Add to the list
                self.follow_buttons.append(img_path)
            except Exception as e:
                self.log("ERROR", f"❌ Lỗi khi tải ảnh {img_file}: {str(e)}")
        
        self.image_status_label.config(text=f"Đã tải {len(self.follow_buttons)} ảnh")
        self.templates_label.config(text=str(len(self.follow_buttons)))
        self.update_stats()
    def create_coordinate_frame(self):
        """Create frame for coordinate settings"""
        coord_frame = ttk.LabelFrame(self.root, text="🎯 Tọa độ Click", padding=5)
        coord_frame.pack(fill=tk.X, padx=10, pady=(0, 10), ipadx=5, ipady=5)
        
        # Input fields
        input_frame = ttk.Frame(coord_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="X:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.coord_x_entry = ttk.Entry(input_frame, width=8)
        self.coord_x_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(input_frame, text="Y:").grid(row=0, column=2, padx=5, sticky=tk.W)
        self.coord_y_entry = ttk.Entry(input_frame, width=8)
        self.coord_y_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(input_frame, text="Delay click (s):").grid(row=0, column=4, padx=5, sticky=tk.W)
        self.click_delay_entry = ttk.Entry(input_frame, width=8)
        self.click_delay_entry.insert(0, "3")
        self.click_delay_entry.grid(row=0, column=5, padx=5)
        
        ttk.Label(input_frame, text="Kích hoạt:").grid(row=0, column=6, padx=5, sticky=tk.W)
        self.coord_enabled = tk.BooleanVar(value=False)
        coord_check = ttk.Checkbutton(input_frame, variable=self.coord_enabled)
        coord_check.grid(row=0, column=7, padx=5)
    
    def load_data(self):
        """Load saved data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.thread_data = data.get('threads', [])
                    self.follow_button_dir = data.get('follow_button_dir', '')
                    self.template_threshold = data.get('threshold', 0.8)
                    
                    # Reset runtime states
                    for thread in self.thread_data:
                        thread['running'] = False
                        thread['stop_flag'] = False
                        thread['status'] = "⏸ Dừng"
        except Exception as e:
            self.log("ERROR", f"❌ Lỗi khi tải dữ liệu: {str(e)}")
    
    def save_data(self):
        """Save current data to file"""
        try:
            # Prepare data to save (exclude runtime states)
            save_data = {
                'threads': [
                    {
                        'id': t['id'],
                        'auth': t['auth'],
                        'token': t['token'],
                        'device': t['device'],
                        'account': t['account'],
                        'account_id': t['account_id'],
                        'jobs': t['jobs'],
                        'earned': t['earned'],
                        'total': t['total'],
                        'failed': t['failed'],
                        'skipped': t['skipped'],
                        'delay': t['delay'],
                        'max_fails': t['max_fails'],
                        'screenshot_delay': t['screenshot_delay'],
                        'click_x': t.get('click_x', -1),
                        'click_y': t.get('click_y', -1),
                        'click_delay': t.get('click_delay', 3),
                        'coord_enabled': t.get('coord_enabled', False)
                    }
                    for t in self.thread_data
                ],
                'follow_button_dir': self.follow_button_dir,
                'threshold': self.template_threshold
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(save_data, f)
        except Exception as e:
            self.log("ERROR", f"❌ Lỗi khi lưu dữ liệu: {str(e)}")
    
    def on_closing(self):
        """Handle window closing event"""
        self.save_data()
        self.root.destroy()
    
    def create_follow_button_frame(self):
        """Create frame for managing follow button images"""
        follow_frame = ttk.LabelFrame(self.root, text="🖼️ Follow Button Templates", padding=5)
        follow_frame.pack(fill=tk.X, padx=10, pady=(0, 10), ipadx=5, ipady=5)
        
        # Button to load follow button images
        btn_frame = ttk.Frame(follow_frame)
        btn_frame.pack(fill=tk.X, pady=3)
        
        ttk.Button(btn_frame, text="📁 Load Follow Buttons", command=self.load_follow_buttons).pack(side=tk.LEFT, padx=5)
        
        # Threshold setting
        ttk.Label(btn_frame, text="Threshold:").pack(side=tk.LEFT, padx=(10, 5))
        self.threshold_var = tk.StringVar(value=str(self.template_threshold))
        threshold_entry = ttk.Entry(btn_frame, textvariable=self.threshold_var, width=5)
        threshold_entry.pack(side=tk.LEFT, padx=5)
        
        # Path display with wrapping
        self.follow_path_label = ttk.Label(
            btn_frame, 
            text=self.follow_button_dir or "No folder selected", 
            wraplength=400,
            anchor=tk.W
        )
        self.follow_path_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Frame to display loaded images with scrollbar
        img_container = ttk.Frame(follow_frame)
        img_container.pack(fill=tk.X, pady=5)
        
        # Scrollbar for images
        canvas = tk.Canvas(img_container, height=80, highlightthickness=0)
        scrollbar = ttk.Scrollbar(img_container, orient=tk.HORIZONTAL, command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.TOP, fill=tk.X, expand=True)
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.image_frame = scrollable_frame
        
        # Status label
        self.image_status_label = ttk.Label(follow_frame, text="No follow button images loaded")
        self.image_status_label.pack()
        
        # Load saved images
        if self.follow_button_dir:
            self.load_follow_buttons(self.follow_button_dir, initial_load=True)

    def create_stats_frame(self):
        """Create the statistics display frame"""
        stats_frame = ttk.LabelFrame(self.root, text="📊 Stats", padding=5)
        stats_frame.pack(fill=tk.X, padx=10, pady=(0, 5), ipadx=5, ipady=3)
        
        # Create stats labels in a compact grid
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        # Compact layout
        ttk.Label(stats_grid, text="Jobs:").grid(row=0, column=0, padx=2, pady=1, sticky=tk.W)
        self.total_jobs_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 9, 'bold'))
        self.total_jobs_label.grid(row=0, column=1, padx=2, pady=1, sticky=tk.W)
        
        ttk.Label(stats_grid, text="Earned:").grid(row=0, column=2, padx=5, pady=1, sticky=tk.W)
        self.total_earned_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 9, 'bold'))
        self.total_earned_label.grid(row=0, column=3, padx=2, pady=1, sticky=tk.W)
        
        ttk.Label(stats_grid, text="Failed:").grid(row=0, column=4, padx=5, pady=1, sticky=tk.W)
        self.total_failed_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 9, 'bold'))
        self.total_failed_label.grid(row=0, column=5, padx=2, pady=1, sticky=tk.W)
        
        ttk.Label(stats_grid, text="Skipped:").grid(row=0, column=6, padx=5, pady=1, sticky=tk.W)
        self.total_skipped_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 9, 'bold'))
        self.total_skipped_label.grid(row=0, column=7, padx=2, pady=1, sticky=tk.W)
        
        ttk.Label(stats_grid, text="Running:").grid(row=0, column=8, padx=5, pady=1, sticky=tk.W)
        self.running_threads_label = ttk.Label(stats_grid, text="0/0", font=('Helvetica', 9, 'bold'))
        self.running_threads_label.grid(row=0, column=9, padx=2, pady=1, sticky=tk.W)
        
        ttk.Label(stats_grid, text="Templates:").grid(row=0, column=10, padx=5, pady=1, sticky=tk.W)
        self.templates_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 9, 'bold'))
        self.templates_label.grid(row=0, column=11, padx=2, pady=1, sticky=tk.W)
        
        # Update stats from loaded data
        self.update_stats()

    def create_control_frame(self):
        """Create the control panel frame"""
        control_frame = ttk.LabelFrame(self.root, text="⚙️ Control", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5, ipadx=5, ipady=3)
        
        # Input fields in a grid for better use of space
        input_frame = ttk.Frame(control_frame)
        input_frame.pack(fill=tk.X, pady=3)
        
        # Row 1: Authorization
        ttk.Label(input_frame, text="🔑 Auth:").grid(row=0, column=0, sticky=tk.W, padx=3, pady=2)
        self.auth_entry = ttk.Entry(input_frame, width=30)
        self.auth_entry.grid(row=0, column=1, padx=3, pady=2, sticky=tk.W)
        
        # Row 2: Token
        ttk.Label(input_frame, text="🔒 Token:").grid(row=1, column=0, sticky=tk.W, padx=3, pady=2)
        self.token_entry = ttk.Entry(input_frame, width=30)
        self.token_entry.grid(row=1, column=1, padx=3, pady=2, sticky=tk.W)
        
        # Row 3: Device
        ttk.Label(input_frame, text="📱 Device:").grid(row=2, column=0, sticky=tk.W, padx=3, pady=2)
        self.device_combo = ttk.Combobox(input_frame, state="readonly", width=28)
        self.device_combo.grid(row=2, column=1, padx=3, pady=2, sticky=tk.W)
        
        # Row 4: Account
        ttk.Label(input_frame, text="👤 Account:").grid(row=3, column=0, sticky=tk.W, padx=3, pady=2)
        self.account_combo = ttk.Combobox(input_frame, state="readonly", width=28)
        self.account_combo.grid(row=3, column=1, padx=3, pady=2, sticky=tk.W)
        
        # Settings in a compact frame
        settings_frame = ttk.Frame(control_frame)
        settings_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(settings_frame, text="⏱ Job Delay:").pack(side=tk.LEFT, padx=3)
        self.delay_entry = ttk.Entry(settings_frame, width=5)
        self.delay_entry.insert(0, "10")
        self.delay_entry.pack(side=tk.LEFT, padx=3)
        
        # Screenshot Delay
        ttk.Label(settings_frame, text="📷 Screenshot Delay:").pack(side=tk.LEFT, padx=(10, 3))
        self.screenshot_delay_entry = ttk.Entry(settings_frame, width=5)
        self.screenshot_delay_entry.insert(0, "7")
        self.screenshot_delay_entry.pack(side=tk.LEFT)
        
        ttk.Label(settings_frame, text="⚠️ Max Fails:").pack(side=tk.LEFT, padx=(10, 3))
        self.max_fails_entry = ttk.Entry(settings_frame, width=5)
        self.max_fails_entry.insert(0, "3")
        self.max_fails_entry.pack(side=tk.LEFT)
        
        # Buttons in a compact grid
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=3)
        
        ttk.Button(btn_frame, text="🔄 Devices", command=self.scan_devices).grid(row=0, column=0, padx=2)
        ttk.Button(btn_frame, text="👥 Accounts", command=self.get_accounts).grid(row=0, column=1, padx=2)
        ttk.Button(btn_frame, text="➕ Add", command=self.add_thread).grid(row=0, column=2, padx=2)
        ttk.Button(btn_frame, text="▶️ Start All", command=self.start_all_threads).grid(row=0, column=3, padx=2)
        ttk.Button(btn_frame, text="⏹ Stop All", command=self.stop_all_threads).grid(row=0, column=4, padx=2)
        ttk.Button(btn_frame, text="🔄 Update Accounts", command=self.update_accounts).grid(row=0, column=5, padx=2)
    
    def create_thread_frame(self):
        """Create the thread management frame"""
        self.thread_frame = ttk.LabelFrame(self.paned_window, text="📊 Threads", padding=5)
        
        # Create treeview with scrollbars
        tree_container = ttk.Frame(self.thread_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        # Vertical scrollbar
        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Horizontal scrollbar
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create treeview with correct columns
        columns = ("id", "auth", "token", "device", "account", "jobs", "earned", "total", "failed", "skipped", "status")
        self.thread_tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode="browse",
            height=5
        )
        self.thread_tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        vsb.config(command=self.thread_tree.yview)
        hsb.config(command=self.thread_tree.xview)
        
        # Configure columns with smaller widths
        columns_config = [
            ("id", "ID", 40, tk.CENTER),
            ("auth", "Auth", 80, tk.W),
            ("token", "Token", 70, tk.W),
            ("device", "Device", 90, tk.W),
            ("account", "Account", 90, tk.W),
            ("jobs", "Jobs", 50, tk.CENTER),
            ("earned", "Earned", 60, tk.CENTER),
            ("total", "Total", 60, tk.CENTER),
            ("failed", "Failed", 60, tk.CENTER),
            ("skipped", "Skipped", 60, tk.CENTER),
            ("status", "Status", 80, tk.CENTER)
        ]
        
        for col, heading, width, anchor in columns_config:
            self.thread_tree.heading(col, text=heading)
            self.thread_tree.column(col, width=width, anchor=anchor)
        
        # Context menu
        self.thread_menu = tk.Menu(self.root, tearoff=0, bg='white', fg=self.text_color,
                                 activebackground=self.info_color, activeforeground='white')
        self.thread_menu.add_command(label="▶️ Start", command=self.start_selected_thread)
        self.thread_menu.add_command(label="⏹ Stop", command=self.stop_selected_thread)
        self.thread_menu.add_separator()
        self.thread_menu.add_command(label="✏️ Change Account", command=self.change_account)
        self.thread_menu.add_command(label="📱 Change Device", command=self.change_device)
        self.thread_menu.add_command(label="⚙️ Change Settings", command=self.change_thread_settings)
        self.thread_menu.add_separator()
        self.thread_menu.add_command(label="🎯 Set Coordinates", command=self.set_coordinates)
        self.thread_menu.add_separator()
        self.thread_menu.add_command(label="❌ Remove", command=self.remove_selected_thread)
        
        self.thread_tree.bind("<Button-3>", self.show_thread_menu)
        
        # Update tree with loaded data
        self.update_thread_tree()

    def create_log_frame(self):
        """Create the log frame"""
        self.log_frame = ttk.LabelFrame(self.paned_window, text="📝 Logs", padding=5)
        
        self.log_text = scrolledtext.ScrolledText(
            self.log_frame,
            wrap=tk.WORD,
            height=6,
            bg='white',
            fg=self.text_color,
            insertbackground=self.text_color,
            font=('Helvetica', 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Add colored tags for different log levels
        self.log_text.tag_config("INFO", foreground=self.info_color)
        self.log_text.tag_config("SUCCESS", foreground=self.success_color)
        self.log_text.tag_config("WARNING", foreground=self.warning_color)
        self.log_text.tag_config("ERROR", foreground=self.error_color)
        self.log_text.tag_config("DEBUG", foreground='purple')
        
        # Add clear log button at the bottom
        btn_frame = ttk.Frame(self.log_frame)
        btn_frame.pack(fill=tk.X, pady=3)
        
        clear_btn = ttk.Button(
            btn_frame,
            text="🧹 Clear Log",
            command=lambda: self.log_text.delete(1.0, tk.END)
        )
        clear_btn.pack(side=tk.RIGHT, padx=5)

    def scan_devices(self):
        """Scan for connected ADB devices"""
        try:
            self.log("INFO", "🔍 Đang quét thiết bị ADB...")
            
            # Try connecting to common emulator ports first
            common_ports = ['127.0.0.1:5555', '127.0.0.1:5556', 'emulator-5554', 'emulator-5556']
            for port in common_ports:
                subprocess.run(['adb', 'connect', port], capture_output=True, text=True)
            
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
            devices = [line.split('\t')[0] for line in result.stdout.splitlines() if '\tdevice' in line]
            
            if not devices:
                messagebox.showwarning("Không Có Thiết Bị", "Không tìm thấy thiết bị ADB nào. Vui lòng kết nối thiết bị hoặc bật giả lập.")
                self.log("ERROR", "❌ Không tìm thấy thiết bị ADB nào!")
                return
            
            self.devices = devices
            self.device_combo['values'] = devices
            if devices:
                self.device_combo.current(0)
            
            self.log("SUCCESS", f"✅ Tìm thấy {len(devices)} thiết bị ADB")
        except Exception as e:
            self.log("ERROR", f"❌ Lỗi khi quét thiết bị: {str(e)}")
            messagebox.showerror("Lỗi", f"Không thể quét thiết bị: {str(e)}")
    
    def get_accounts(self):
        """Get TikTok accounts using the provided authorization"""
        auth = self.auth_entry.get()
        token = self.token_entry.get()
        
        if not auth or not token:
            messagebox.showwarning("Thiếu Thông Tin", "Vui lòng nhập Authorization và Token trước!")
            return
        
        self._get_accounts(auth, token)
    
    def update_accounts(self):
        """Update accounts for all threads"""
        for data in self.thread_data:
            if not data["running"]:
                self._get_accounts_for_thread(data["auth"], data["token"], data["id"])
    
    def _get_accounts_for_thread(self, auth, token, thread_id):
        """Get accounts for a specific thread"""
        try:
            self.log("INFO", f"🔍 Luồng #{thread_id}: Đang cập nhật danh sách tài khoản...")
            
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json;charset=utf-8',
                'Authorization': auth,
                't': token,
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
                'Referer': 'https://app.golike.net/account/manager/tiktok',
            }
            
            response = requests.get(
                'https://gateway.golike.net/api/tiktok-account', 
                headers=headers, 
                json={}, 
                impersonate="chrome"
            ).json()
            
            if response["status"] != 200:
                self.log("ERROR", f"❌ Luồng #{thread_id}: Không thể lấy danh sách tài khoản. Kiểm tra lại Authorization và Token!")
                return
            
            # Find and update the thread
            for data in self.thread_data:
                if data["id"] == thread_id and data["auth"] == auth and data["token"] == token:
                    self.accounts = response["data"]
                    account_names = [acc["nickname"] for acc in self.accounts]
                    
                    # Update the thread if account is no longer available
                    if data["account"] not in account_names and account_names:
                        data["account"] = account_names[0]
                        data["account_id"] = self.accounts[0]["id"]
                    
                    self.log("SUCCESS", f"✅ Luồng #{thread_id}: Cập nhật {len(self.accounts)} tài khoản thành công")
                    self.update_thread_tree()
                    return
            
            self.log("WARNING", f"⚠️ Luồng #{thread_id}: Không tìm thấy luồng để cập nhật")
        except Exception as e:
            self.log("ERROR", f"❌ Luồng #{thread_id}: Lỗi khi lấy tài khoản: {str(e)}")
    
    def _get_accounts(self, auth, token):
        """Get accounts using specific auth and token"""
        try:
            self.log("INFO", "🔍 Đang lấy danh sách tài khoản TikTok...")
            
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json;charset=utf-8',
                'Authorization': auth,
                't': token,
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
                'Referer': 'https://app.golike.net/account/manager/tiktok',
            }
            
            response = requests.get(
                'https://gateway.golike.net/api/tiktok-account', 
                headers=headers, 
                json={}, 
                impersonate="chrome"
            ).json()
            
            if response["status"] != 200:
                messagebox.showerror("Lỗi", "Không thể lấy danh sách tài khoản. Kiểm tra lại Authorization và Token!")
                self.log("ERROR", "❌ Authorization hoặc Token không hợp lệ!")
                return
            
            self.accounts = response["data"]
            account_names = [acc["nickname"] for acc in self.accounts]
            self.account_combo['values'] = account_names
            if account_names:
                self.account_combo.current(0)
            
            self.log("SUCCESS", f"✅ Tìm thấy {len(self.accounts)} tài khoản TikTok")
        except Exception as e:
            self.log("ERROR", f"❌ Lỗi khi lấy tài khoản: {str(e)}")
            messagebox.showerror("Lỗi", f"Không thể lấy danh sách tài khoản: {str(e)}")
    
    def add_thread(self):
        """Add a new thread to the list"""
        if not self.validate_inputs():
            return
        
        thread_id = len(self.thread_data) + 1
        auth = self.auth_entry.get()
        token = self.token_entry.get()
        device = self.device_combo.get()
        account_idx = self.account_combo.current()
        account = self.accounts[account_idx]["nickname"] if account_idx >= 0 else ""
        account_id = self.accounts[account_idx]["id"] if account_idx >= 0 else ""
        delay = self.delay_entry.get()
        max_fails = self.max_fails_entry.get()
        screenshot_delay = self.screenshot_delay_entry.get()
        click_x = self.coord_x_entry.get()
        click_y = self.coord_y_entry.get()
        click_delay = self.click_delay_entry.get()
        coord_enabled = self.coord_enabled.get()
        
        thread_data = {
            "id": thread_id,
            "auth": auth,
            "token": token,
            "device": device,
            "account": account,
            "account_id": account_id,
            "jobs": 0,
            "earned": 0,
            "total": 0,
            "failed": 0,
            "skipped": 0,
            "status": "⏸ Dừng",
            "delay": int(delay) if delay.isdigit() else 10,
            "max_fails": int(max_fails) if max_fails.isdigit() else 3,
            "screenshot_delay": int(screenshot_delay) if screenshot_delay.isdigit() else 7,
            "click_x": int(click_x) if click_x.isdigit() else -1,
            "click_y": int(click_y) if click_y.isdigit() else -1,
            "click_delay": int(click_delay) if click_delay.isdigit() else 3,
            "coord_enabled": coord_enabled,
            "running": False,
            "stop_flag": False
        }
        
        self.thread_data.append(thread_data)
        self.update_thread_tree()
        self.update_stats()
        self.save_data()
        self.log("INFO", f"➕ Đã thêm luồng #{thread_id} cho tài khoản {account}")
    
    def validate_inputs(self):
        """Validate all required inputs are present"""
        errors = []
        
        if not self.auth_entry.get():
            errors.append("Vui lòng nhập Authorization")
        if not self.token_entry.get():
            errors.append("Vui lòng nhập Token")
        if not self.device_combo.get():
            errors.append("Vui lòng chọn thiết bị ADB")
        if not self.account_combo.get():
            errors.append("Vui lòng chọn tài khoản TikTok")
        
        if errors:
            messagebox.showerror("Lỗi Xác Thực", "\n".join(errors))
            return False
        return True
    
    def update_thread_tree(self):
        """Update the thread treeview with current data"""
        self.thread_tree.delete(*self.thread_tree.get_children())
        
        for data in self.thread_data:
            self.thread_tree.insert("", tk.END, 
                                  values=(
                                      data["id"],
                                      data["auth"][:10] + "..." if len(data["auth"]) > 10 else data["auth"],
                                      data["token"][:6] + "..." if len(data["token"]) > 6 else data["token"],
                                      data["device"],
                                      data["account"][:10] + "..." if len(data["account"]) > 10 else data["account"],
                                      data["jobs"],
                                      data["earned"],
                                      data["total"],
                                      data["failed"],
                                      data["skipped"],
                                      data["status"]
                                  ))
    
    def update_stats(self):
        """Update the statistics display"""
        if not self.thread_data:
            self.total_jobs_label.config(text="0")
            self.total_earned_label.config(text="0")
            self.total_failed_label.config(text="0")
            self.total_skipped_label.config(text="0")
            self.running_threads_label.config(text="0/0")
            self.templates_label.config(text=str(len(self.follow_buttons)))
            return
            
        self.total_stats = {
            'jobs': sum(t["jobs"] for t in self.thread_data),
            'earned': sum(t["total"] for t in self.thread_data),
            'failed': sum(t["failed"] for t in self.thread_data),
            'skipped': sum(t["skipped"] for t in self.thread_data),
            'running': sum(1 for t in self.thread_data if t["running"]),
            'templates': len(self.follow_buttons)
        }
        
        self.total_jobs_label.config(text=str(self.total_stats['jobs']))
        self.total_earned_label.config(text=str(self.total_stats['earned']))
        self.total_failed_label.config(text=str(self.total_stats['failed']))
        self.total_skipped_label.config(text=str(self.total_stats['skipped']))
        self.running_threads_label.config(text=f"{self.total_stats['running']}/{len(self.thread_data)}")
        self.templates_label.config(text=str(self.total_stats['templates']))
    
    def show_thread_menu(self, event):
        """Show context menu for thread"""
        item = self.thread_tree.identify_row(event.y)
        if item:
            self.thread_tree.selection_set(item)
            self.thread_menu.post(event.x_root, event.y_root)
    
    def start_selected_thread(self):
        """Start the selected thread"""
        selected = self.thread_tree.selection()
        if not selected:
            messagebox.showwarning("Không Có Lựa Chọn", "Vui lòng chọn một luồng trước!")
            return
        
        item = selected[0]
        thread_id = int(self.thread_tree.item(item, "values")[0])
        self.start_thread(thread_id)
    
    def stop_selected_thread(self):
        """Stop the selected thread"""
        selected = self.thread_tree.selection()
        if not selected:
            messagebox.showwarning("Không Có Lựa Chọn", "Vui lòng chọn một luồng trước!")
            return
        
        item = selected[0]
        thread_id = int(self.thread_tree.item(item, "values")[0])
        self.stop_thread(thread_id)
    
    def change_account(self):
        """Change the account for selected thread"""
        selected = self.thread_tree.selection()
        if not selected:
            messagebox.showwarning("Không Có Lựa Chọn", "Vui lòng chọn một luồng trước!")
            return
        
        item = selected[0]
        thread_id = int(self.thread_tree.item(item, "values")[0])
        
        # Get thread data
        thread_data = None
        for data in self.thread_data:
            if data["id"] == thread_id:
                thread_data = data
                break
        
        if not thread_data:
            self.log("ERROR", f"❌ Không tìm thấy luồng #{thread_id}")
            return
        
        # Get accounts using thread's auth and token
        self._get_accounts_for_thread(thread_data["auth"], thread_data["token"], thread_id)
        
        if not self.accounts:
            messagebox.showwarning("Không Có Tài Khoản", "Không có tài khoản nào để chọn!")
            return
        
        # Create account selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Đổi Tài Khoản")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        dialog.configure(bg='#2c3e50')
        self.center_window(dialog)
        
        ttk.Label(dialog, text="Chọn Tài Khoản Mới:").pack(pady=5)
        
        account_combo = ttk.Combobox(dialog, state="readonly")
        account_names = [acc["nickname"] for acc in self.accounts]
        account_combo['values'] = account_names
        account_combo.current(0)
        account_combo.pack(pady=5)
        
        def apply_changes():
            account_idx = account_combo.current()
            if account_idx >= 0:
                if thread_data["running"]:
                    messagebox.showwarning("Luồng Đang Chạy", "Không thể đổi tài khoản khi luồng đang chạy!")
                    dialog.destroy()
                    return
                
                thread_data["account"] = self.accounts[account_idx]["nickname"]
                thread_data["account_id"] = self.accounts[account_idx]["id"]
                self.update_thread_tree()
                self.save_data()
                self.log("INFO", f"🔄 Đã đổi tài khoản cho luồng #{thread_id} thành {thread_data['account']}")
            dialog.destroy()
        
        ttk.Button(dialog, text="Áp Dụng", command=apply_changes).pack(pady=10)
    
    def change_device(self):
        """Change the device for selected thread"""
        selected = self.thread_tree.selection()
        if not selected:
            messagebox.showwarning("Không Có Lựa Chọn", "Vui lòng chọn một luồng trước!")
            return
        
        if not self.devices:
            messagebox.showwarning("Không Có Thiết Bị", "Vui lòng quét thiết bị trước!")
            return
        
        item = selected[0]
        thread_id = int(self.thread_tree.item(item, "values")[0])
        
        # Get thread data
        thread_data = None
        for data in self.thread_data:
            if data["id"] == thread_id:
                thread_data = data
                break
        
        if not thread_data:
            self.log("ERROR", f"❌ Không tìm thấy luồng #{thread_id}")
            return
        
        # Create device selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Đổi Thiết Bị")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        dialog.configure(bg='#2c3e50')
        self.center_window(dialog)
        
        ttk.Label(dialog, text="Chọn Thiết Bị Mới:").pack(pady=5)
        
        device_combo = ttk.Combobox(dialog, state="readonly")
        device_combo['values'] = self.devices
        device_combo.current(0)
        device_combo.pack(pady=5)
        
        def apply_changes():
            device = device_combo.get()
            if device:
                if thread_data["running"]:
                    messagebox.showwarning("Luồng Đang Chạy", "Không thể đổi thiết bị khi luồng đang chạy!")
                    dialog.destroy()
                    return
                
                thread_data["device"] = device
                self.update_thread_tree()
                self.save_data()
                self.log("INFO", f"🔄 Đã đổi thiết bị cho luồng #{thread_id} thành {device}")
            dialog.destroy()
        
        ttk.Button(dialog, text="Áp Dụng", command=apply_changes).pack(pady=10)
    
    def set_coordinates(self):
        """Set coordinates for selected thread"""
        selected = self.thread_tree.selection()
        if not selected:
            messagebox.showwarning("Không Có Lựa Chọn", "Vui lòng chọn một luồng trước!")
            return
        
        item = selected[0]
        thread_id = int(self.thread_tree.item(item, "values")[0])
        
        # Find thread data
        thread_data = None
        for data in self.thread_data:
            if data["id"] == thread_id:
                thread_data = data
                break
        
        if not thread_data:
            self.log("ERROR", f"❌ Không tìm thấy luồng #{thread_id}")
            return
        
        # Create coordinate dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Thiết Lập Tọa Độ")
        dialog.geometry("300x250")
        dialog.resizable(False, False)
        dialog.configure(bg='#2c3e50')
        self.center_window(dialog)
        
        # Coordinates
        ttk.Label(dialog, text="Tọa độ X:").pack(pady=(10, 0))
        coord_x_var = tk.StringVar(value=str(thread_data["click_x"]))
        coord_x_entry = ttk.Entry(dialog, textvariable=coord_x_var, width=10)
        coord_x_entry.pack()
        
        ttk.Label(dialog, text="Tọa độ Y:").pack(pady=(10, 0))
        coord_y_var = tk.StringVar(value=str(thread_data["click_y"]))
        coord_y_entry = ttk.Entry(dialog, textvariable=coord_y_var, width=10)
        coord_y_entry.pack()
        
        ttk.Label(dialog, text="Delay click (s):").pack(pady=(10, 0))
        click_delay_var = tk.StringVar(value=str(thread_data["click_delay"]))
        click_delay_entry = ttk.Entry(dialog, textvariable=click_delay_var, width=10)
        click_delay_entry.pack()
        
        # Enable checkbox
        enable_var = tk.BooleanVar(value=thread_data.get("coord_enabled", False))
        enable_check = ttk.Checkbutton(dialog, text="Kích hoạt click theo tọa độ", variable=enable_var)
        enable_check.pack(pady=(10, 0))
        
        def apply_changes():
            try:
                thread_data["click_x"] = int(coord_x_var.get()) if coord_x_var.get().strip() and coord_x_var.get().isdigit() else -1
                thread_data["click_y"] = int(coord_y_var.get()) if coord_y_var.get().strip() and coord_y_var.get().isdigit() else -1
                thread_data["click_delay"] = int(click_delay_var.get()) if click_delay_var.get().isdigit() else 3
                thread_data["coord_enabled"] = enable_var.get()
                
                self.update_thread_tree()
                self.save_data()
                self.log("INFO", f"🎯 Đã cập nhật tọa độ cho luồng #{thread_id}")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Lỗi", "Vui lòng nhập số nguyên hợp lệ!")
        
        ttk.Button(dialog, text="Áp Dụng", command=apply_changes).pack(pady=15)
    
    def change_thread_settings(self):
        """Change settings for selected thread"""
        selected = self.thread_tree.selection()
        if not selected:
            messagebox.showwarning("Không Có Lựa Chọn", "Vui lòng chọn một luồng trước!")
            return
        
        item = selected[0]
        thread_id = int(self.thread_tree.item(item, "values")[0])
        
        # Find thread data
        thread_data = None
        for data in self.thread_data:
            if data["id"] == thread_id:
                thread_data = data
                break
        
        if not thread_data:
            self.log("ERROR", f"❌ Không tìm thấy luồng #{thread_id}")
            return
        
        # Create settings dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Thay Đổi Cài Đặt")
        dialog.geometry("300x250")
        dialog.resizable(False, False)
        dialog.configure(bg='#2c3e50')
        self.center_window(dialog)
        
        # Job Delay
        ttk.Label(dialog, text="⏱ Job Delay (giây):").pack(pady=(10, 0))
        delay_var = tk.StringVar(value=str(thread_data["delay"]))
        delay_entry = ttk.Entry(dialog, textvariable=delay_var, width=10)
        delay_entry.pack()
        
        # Screenshot Delay
        ttk.Label(dialog, text="📷 Screenshot Delay (giây):").pack(pady=(10, 0))
        ss_delay_var = tk.StringVar(value=str(thread_data["screenshot_delay"]))
        ss_delay_entry = ttk.Entry(dialog, textvariable=ss_delay_var, width=10)
        ss_delay_entry.pack()
        
        # Max Fails
        ttk.Label(dialog, text="⚠️ Max Fails:").pack(pady=(10, 0))
        max_fails_var = tk.StringVar(value=str(thread_data["max_fails"]))
        max_fails_entry = ttk.Entry(dialog, textvariable=max_fails_var, width=10)
        max_fails_entry.pack()
        
        def apply_changes():
            try:
                thread_data["delay"] = int(delay_var.get())
                thread_data["screenshot_delay"] = int(ss_delay_var.get())
                thread_data["max_fails"] = int(max_fails_var.get())
                
                self.update_thread_tree()
                self.save_data()
                self.log("INFO", f"⚙️ Đã cập nhật cài đặt cho luồng #{thread_id}")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Lỗi", "Vui lòng nhập số nguyên hợp lệ!")
        
        ttk.Button(dialog, text="Áp Dụng", command=apply_changes).pack(pady=15)
    
    def remove_selected_thread(self):
        """Remove the selected thread"""
        selected = self.thread_tree.selection()
        if not selected:
            return
        
        item = selected[0]
        thread_id = int(self.thread_tree.item(item, "values")[0])
        
        # Find and stop the thread if running
        for i, data in enumerate(self.thread_data):
            if data["id"] == thread_id:
                if data["running"]:
                    if not messagebox.askyesno("Xác Nhận", f"Luồng #{thread_id} đang chạy. Bạn có chắc muốn dừng và xóa?"):
                        return
                    data["stop_flag"] = True
                del self.thread_data[i]
                break
        
        self.update_thread_tree()
        self.update_stats()
        self.save_data()
        self.log("INFO", f"🗑 Đã xóa luồng #{thread_id}")
    
    def start_all_threads(self):
        """Start all threads"""
        if not self.thread_data:
            messagebox.showwarning("Không Có Luồng", "Không có luồng nào để bắt đầu!")
            return
        
        for data in self.thread_data:
            if not data["running"]:
                self.start_thread(data["id"])
    
    def stop_all_threads(self):
        """Stop all running threads"""
        if not any(data["running"] for data in self.thread_data):
            messagebox.showwarning("Không Có Luồng Đang Chạy", "Không có luồng nào đang chạy!")
            return
        
        if messagebox.askyesno("Xác Nhận", "Bạn có chắc muốn dừng TẤT CẢ các luồng đang chạy?"):
            for data in self.thread_data:
                if data["running"]:
                    self.stop_thread(data["id"])
    
    def start_thread(self, thread_id):
        """Start a specific thread"""
        for data in self.thread_data:
            if data["id"] == thread_id:
                if data["running"]:
                    self.log("WARNING", f"⚠️ Luồng #{thread_id} đã chạy rồi!")
                    return
                
                data["running"] = True
                data["stop_flag"] = False
                data["status"] = "▶ Đang chạy"
                
                thread = threading.Thread(
                    target=self.run_automation,
                    args=(data,),
                    daemon=True
                )
                thread.start()
                
                self.threads.append(thread)
                self.update_thread_tree()
                self.update_stats()
                self.save_data()
                self.log("SUCCESS", f"🚀 Bắt đầu luồng #{thread_id} - Tài khoản: {data['account']}")
                return
        
        self.log("ERROR", f"❌ Không tìm thấy luồng #{thread_id}")
    
    def stop_thread(self, thread_id):
        """Stop a specific thread"""
        for data in self.thread_data:
            if data["id"] == thread_id:
                if not data["running"]:
                    self.log("WARNING", f"⚠️ Luồng #{thread_id} không chạy!")
                    return
                
                data["stop_flag"] = True
                data["status"] = "⏸ Đang dừng..."
                self.update_thread_tree()
                self.save_data()
                self.log("INFO", f"⏹ Đang dừng luồng #{thread_id}...")
                return
        
        self.log("ERROR", f"❌ Không tìm thấy luồng #{thread_id}")
    
    def run_automation(self, thread_data):
        """Main automation function to run in thread"""
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=utf-8',
            'Authorization': thread_data["auth"],
            't': thread_data["token"],
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
            'Referer': 'https://app.golike.net/account/manager/tiktok',
        }
        
        account_id = thread_data["account_id"]
        device = thread_data["device"]
        delay = thread_data["delay"]
        max_fails = thread_data["max_fails"]
        screenshot_delay = thread_data["screenshot_delay"]
        fail_count = 0
        
        self.log("INFO", f"📡 Luồng #{thread_data['id']} đã sẵn sàng - Tài khoản: {thread_data['account']}")
        
        while not thread_data["stop_flag"]:
            try:
                # Get job
                params = {
                    'account_id': account_id,
                    'data': 'null',
                }
                
                response = requests.get(
                    'https://gateway.golike.net/api/advertising/publishers/tiktok/jobs',
                    params=params,
                    headers=headers,
                    json={},
                    impersonate="chrome"
                ).json()
                
                if response["status"] != 200:
                    self.log("ERROR", f"❌ Luồng #{thread_data['id']}: Không lấy được job")
                    fail_count += 1
                    thread_data["failed"] += 1
                    if fail_count >= max_fails:
                        self.log("WARNING", f"⚠️ Luồng #{thread_data['id']}: Đạt tối đa {max_fails} lỗi, đang dừng...")
                        break
                    
                    # Update UI
                    self.root.after(0, self.update_thread_tree)
                    self.root.after(0, self.update_stats)
                    self.root.after(0, self.save_data)
                    
                    time.sleep(delay)
                    continue
                
                job_data = response["data"]
                ads_id = job_data["id"]
                link = job_data["link"]
                object_id = job_data["object_id"]
                job_type = job_data["type"]
                
                if job_type != "follow":
                    # Skip non-follow jobs
                    self.skip_job(headers, ads_id, object_id, account_id, job_type)
                    thread_data["skipped"] += 1
                    
                    # Update UI
                    self.root.after(0, self.update_thread_tree)
                    self.root.after(0, self.update_stats)
                    self.root.after(0, self.save_data)
                    
                    time.sleep(1)
                    continue
                
                # Open TikTok link via ADB
                self.log("INFO", f"🌐 Luồng #{thread_data['id']}: Đang mở link: {link}")
                subprocess.run(
                    ['adb', '-s', device, 'shell', 'am', 'start', '-a', 'android.intent.action.VIEW', '-d', link],
                    capture_output=True
                )
                
                self.log("INFO", f"⏳ Luồng #{thread_data['id']}: Đang chờ {screenshot_delay} giây để tải trang...")
                time.sleep(screenshot_delay)
                
                # Check if coordinate click is enabled
                if thread_data.get("coord_enabled", False) and thread_data["click_x"] >= 0 and thread_data["click_y"] >= 0:
                    # Click using coordinates
                    x = thread_data["click_x"]
                    y = thread_data["click_y"]
                    click_delay = thread_data.get("click_delay", 3)
                    
                    self.log("INFO", f"⏳ Luồng #{thread_data['id']}: Đang chờ {click_delay} giây trước khi click...")
                    time.sleep(click_delay)
                    
                    self.log("INFO", f"👆 Luồng #{thread_data['id']}: Đang bấm tại tọa độ ({x}, {y})")
                    subprocess.run(
                        ['adb', '-s', device, 'shell', 'input', 'tap', str(x), str(y)],
                        capture_output=True
                    )
                else:
                    # Verify follow button and get its position
                    button_info = self.verify_follow_button(device, thread_data["id"])
                    if not button_info:
                        self.log("WARNING", f"⚠️ Luồng #{thread_data['id']}: Không tìm thấy nút Follow phù hợp! Đánh dấu là thất bại...")
                        
                        # Skip this job and mark as failed
                        self.skip_job(headers, ads_id, object_id, account_id, job_type)
                        thread_data["failed"] += 1
                        fail_count += 1
                        
                        # Update UI
                        self.root.after(0, self.update_thread_tree)
                        self.root.after(0, self.update_stats)
                        self.root.after(0, self.save_data)
                        
                        # Check if we should stop
                        if fail_count >= max_fails:
                            self.log("WARNING", f"⚠️ Luồng #{thread_data['id']}: Đạt tối đa {max_fails} lỗi, đang dừng...")
                            break
                        
                        # Short delay before next job
                        time.sleep(2)
                        continue
                    
                    # Perform the follow action
                    self.log("INFO", f"👆 Luồng #{thread_data['id']}: Đang bấm nút Follow")
                    x = button_info['x'] + button_info['width'] // 2
                    y = button_info['y'] + button_info['height'] // 2
                    
                    # Execute the tap command
                    subprocess.run(
                        ['adb', '-s', device, 'shell', 'input', 'tap', str(x), str(y)],
                        capture_output=True
                    )
                
                # Wait 3 seconds for the action to complete
                time.sleep(3)
                
                # Wait for job to complete
                self.log("INFO", f"⏳ Luồng #{thread_data['id']}: Đang chờ {delay} giây...")
                for remaining in range(delay, 0, -1):
                    if thread_data["stop_flag"]:
                        break
                    time.sleep(1)
                
                if thread_data["stop_flag"]:
                    break
                
                # Complete the job
                json_data = {
                    'ads_id': ads_id,
                    'account_id': account_id,
                    'async': True,
                    'data': None,
                }
                
                response = requests.post(
                    'https://gateway.golike.net/api/advertising/publishers/tiktok/complete-jobs',
                    headers=headers,
                    json=json_data,
                    impersonate="chrome"
                ).json()
                
                if response["status"] == 200:
                    thread_data["jobs"] += 1
                    earned = response["data"]["prices"]
                    thread_data["earned"] = earned
                    thread_data["total"] += earned
                    fail_count = 0
                    
                    self.log(
                        "SUCCESS", 
                        f"✅ Luồng #{thread_data['id']}: Hoàn thành job #{thread_data['jobs']} (+{earned}đ)"
                    )
                else:
                    # If job completion fails, skip the job
                    self.log("ERROR", f"❌ Luồng #{thread_data['id']}: Lỗi hoàn thành job, đang bỏ qua...")
                    self.skip_job(headers, ads_id, object_id, account_id, job_type)
                    thread_data["skipped"] += 1
                    fail_count += 1
                    
                    self.log(
                        "WARNING", 
                        f"⚠️ Luồng #{thread_data['id']}: Đã bỏ qua job (Lỗi: {fail_count}/{max_fails})"
                    )
                
                # Update UI
                self.root.after(0, self.update_thread_tree)
                self.root.after(0, self.update_stats)
                self.root.after(0, self.save_data)
                
                # Check if we should stop
                if fail_count >= max_fails:
                    self.log("WARNING", f"⚠️ Luồng #{thread_data['id']}: Đạt tối đa lỗi, đang dừng...")
                    break
                
                # Short delay between jobs
                time.sleep(1)
                
            except Exception as e:
                self.log("ERROR", f"❌ Luồng #{thread_data['id']}: Lỗi - {str(e)}")
                thread_data["failed"] += 1
                self.root.after(0, self.update_stats)
                self.root.after(0, self.save_data)
                time.sleep(5)
        
        # Clean up
        thread_data["running"] = False
        thread_data["status"] = "⏸ Dừng"
        self.root.after(0, self.update_thread_tree)
        self.root.after(0, self.update_stats)
        self.root.after(0, self.save_data)
        self.log("INFO", f"🛑 Luồng #{thread_data['id']} đã dừng")
    
    def verify_follow_button(self, device_id, thread_id):
        """Verify the presence of a follow button on the screen and return its position"""
        if not self.follow_buttons:
            self.log("WARNING", f"⚠️ Luồng #{thread_id}: Chưa tải hình ảnh nút Follow!")
            return None

        try:
            # Capture screenshot
            self.log("INFO", f"📸 Luồng #{thread_id}: Đang chụp màn hình...")
            result = subprocess.run(
                ['adb', '-s', device_id, 'exec-out', 'screencap', '-p'],
                capture_output=True,
                check=True
            )
            
            # Lưu ảnh tạm để debug
            debug_path = f"debug_{thread_id}.png"
            with open(debug_path, 'wb') as f:
                f.write(result.stdout)
            
            # Đọc ảnh với OpenCV
            screenshot = cv2.imread(debug_path)
            if screenshot is None:
                self.log("ERROR", f"❌ Luồng #{thread_id}: Không thể đọc ảnh chụp màn hình")
                return None
            
            # Ghi log kích thước ảnh
            self.log("DEBUG", f"📏 Kích thước ảnh chụp: {screenshot.shape[1]}x{screenshot.shape[0]}")
            
            # Chuyển sang ảnh xám
            screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            
            best_match = {'max_val': 0}
            found = False
            
            for template_path in self.follow_buttons:
                template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
                if template is None:
                    self.log("ERROR", f"❌ Không đọc được template: {template_path}")
                    continue
                    
                # Ghi log kích thước template
                self.log("DEBUG", f"📏 Template: {template_path} - {template.shape[1]}x{template.shape[0]}")
                
                # Kiểm tra kích thước template
                if template.shape[0] > screenshot.shape[0] or template.shape[1] > screenshot.shape[1]:
                    self.log("WARNING", f"⚠️ Template quá lớn: {template_path}")
                    continue
                    
                # Template matching
                res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                
                # Cập nhật kết quả tốt nhất
                if max_val > best_match['max_val']:
                    best_match = {
                        'max_val': max_val,
                        'loc': max_loc,
                        'tpl': template_path,
                        'size': template.shape[::-1]  # (width, height)
                    }
                
                # Kiểm tra ngưỡng
                if max_val >= self.template_threshold:
                    self.log("SUCCESS", f"✅ Tìm thấy nút Follow ({max_val:.2f}): {os.path.basename(template_path)}")
                    found = True
                    break
            
            # Xử lý kết quả
            if found:
                w, h = best_match['size']
                return {
                    'x': best_match['loc'][0],
                    'y': best_match['loc'][1],
                    'width': w,
                    'height': h
                }
            else:
                # Lưu ảnh debug nếu không tìm thấy
                fail_path = f"fail_{thread_id}.png"
                cv2.imwrite(fail_path, screenshot)
                self.log("WARNING", f"⚠️ Không tìm thấy nút Follow! Độ khớp cao nhất: {best_match['max_val']:.2f}")
                self.log("DEBUG", f"🔍 Xem ảnh debug tại: {os.path.abspath(debug_path)}")
                self.log("DEBUG", f"🔍 Xem ảnh lỗi tại: {os.path.abspath(fail_path)}")
                return None
                
        except Exception as e:
            self.log("ERROR", f"❌ Lỗi khi kiểm tra nút Follow: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def skip_job(self, headers, ads_id, object_id, account_id, job_type):
        """Skip a job that's not the right type"""
        try:
            # Report the job
            json_data1 = {
                'description': 'Tôi đã làm Job này rồi',
                'users_advertising_id': ads_id,
                'type': 'ads',
                'provider': 'tiktok',
                'fb_id': account_id,
                'error_type': 6,
            }
            requests.post(
                'https://gateway.golike.net/api/report/send', 
                headers=headers, 
                json=json_data1, 
                impersonate="chrome"
            )
            
            # Skip the job
            json_data = {
                'ads_id': ads_id,
                'object_id': object_id,
                'account_id': account_id,
                'type': job_type,
            }
            requests.post(
                'https://gateway.golike.net/api/advertising/publishers/tiktok/skip-jobs',
                headers=headers,
                json=json_data,
                impersonate="chrome"
            )
            
            self.log("INFO", f"⏭ Đã bỏ qua job {job_type}")
        except Exception as e:
            self.log("ERROR", f"❌ Lỗi khi bỏ qua job: {str(e)}")
    
    def center_window(self, window):
        """Center a window on screen"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    
    def log(self, level, message):
        """Add a message to the log with appropriate color"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.root.after(0, lambda: self._update_log(level, log_message))
    
    def _update_log(self, level, message):
        """Update the log widget (must be called from main thread)"""
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, message, level)
        self.log_text.configure(state='disabled')
        self.log_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = TikTokAutomationGUI(root)
    root.mainloop()