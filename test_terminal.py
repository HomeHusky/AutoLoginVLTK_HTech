import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import subprocess
import threading

class TerminalApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("850x650+0+0")
        self.root.title("Tkinter Terminal")

        # Tạo widget Text cuộn để hiển thị đầu ra như terminal
        self.terminal_output = ScrolledText(root, wrap=tk.WORD, font=("Courier", 10))
        self.terminal_output.pack(expand=True, fill=tk.BOTH)

        # Tạo entry để nhập lệnh
        self.command_entry = tk.Entry(root, font=("Courier", 10))
        self.command_entry.pack(fill=tk.X)
        self.command_entry.bind("<Return>", self.run_command)

    def run_command(self, event):
        command = self.command_entry.get()
        self.command_entry.delete(0, tk.END)  # Xóa entry sau khi nhấn Enter

        # Chạy lệnh trong luồng riêng để không làm treo giao diện
        threading.Thread(target=self.execute_command, args=(command,)).start()

    def execute_command(self, command):
        try:
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True
            )
            # Đọc từng dòng đầu ra từ terminal và hiển thị lên widget Text
            for line in process.stdout:
                self.terminal_output.insert(tk.END, line)
                self.terminal_output.see(tk.END)  # Cuộn xuống cuối

            for line in process.stderr:
                self.terminal_output.insert(tk.END, line)
                self.terminal_output.see(tk.END)  # Cuộn xuống cuối
        except Exception as e:
            self.terminal_output.insert(tk.END, f"Error: {str(e)}\n")
            self.terminal_output.see(tk.END)

# Khởi tạo ứng dụng tkinter
root = tk.Tk()
app = TerminalApp(root)
root.mainloop()