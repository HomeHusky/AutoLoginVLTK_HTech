# 🔐 HƯỚNG DẪN CHẠY VỚI QUYỀN ADMIN

## ⚠️ Vấn đề

Ứng dụng cần quyền **Administrator** để:
- Điều khiển cửa sổ game
- Mở Auto VLBS
- Thao tác với các process

Khi chạy bằng `quick_run.vbs` từ Startup, Windows không tự động cấp quyền admin.

## ✅ Giải pháp

### **Cách 1: Sử dụng quick_run.vbs (Đã sửa) ⭐ KHUYÊN DÙNG**

File `quick_run.vbs` đã được cập nhật để **tự động yêu cầu quyền admin**.

**Cách hoạt động:**
```vbscript
' Kiểm tra quyền admin và tự động yêu cầu nếu chưa có
If Not WScript.Arguments.Named.Exists("elevated") Then
    CreateObject("Shell.Application").ShellExecute "wscript.exe", _
        """" & WScript.ScriptFullName & """ /elevated", "", "runas", 1
    WScript.Quit
End If
```

**Khi chạy:**
1. File kiểm tra có quyền admin chưa
2. Nếu chưa → Hiện popup UAC yêu cầu quyền
3. Sau khi cấp quyền → Chạy Python script với admin

**Lưu ý:** Popup UAC sẽ xuất hiện mỗi lần khởi động máy.

---

### **Cách 2: Sử dụng quick_run_admin.bat**

Tôi đã tạo file `quick_run_admin.bat` với logic tương tự.

**Chạy:**
```bash
# Double click file
quick_run_admin.bat
```

**Hoặc thêm vào Startup:**
1. Win + R → `shell:startup`
2. Tạo shortcut của `quick_run_admin.bat`
3. Chuột phải shortcut → Properties
4. Advanced → ✅ Run as administrator

---

### **Cách 3: Tắt UAC cho file cụ thể (Không khuyên dùng)**

Sử dụng Task Scheduler để chạy mà không cần popup UAC:

**Bước 1: Tạo Task**
1. Win + R → `taskschd.msc`
2. Create Task (không phải Create Basic Task)
3. General tab:
   - Name: `AutoLogin Startup`
   - ✅ Run with highest privileges
   - ✅ Run whether user is logged on or not

**Bước 2: Triggers**
1. New Trigger
2. Begin the task: `At log on`
3. Specific user: `<Your username>`

**Bước 3: Actions**
1. New Action
2. Action: `Start a program`
3. Program/script: `wscript.exe`
4. Add arguments: `"D:\VoLam\AutoHomeHusky\AutoLoginVLTK_HTech_recreate\quick_run.vbs"`

**Bước 4: Conditions**
- ❌ Bỏ tích "Start the task only if the computer is on AC power"

**Bước 5: Settings**
- ✅ Allow task to be run on demand
- ✅ If the task fails, restart every: 1 minute

---

### **Cách 4: Chạy Python với admin mặc định**

Tạo shortcut Python với quyền admin:

**Bước 1: Tạo shortcut**
1. Chuột phải `python.exe` → Create shortcut
2. Đặt tên: `Python (Admin)`

**Bước 2: Set admin**
1. Chuột phải shortcut → Properties
2. Compatibility tab
3. ✅ Run this program as an administrator

**Bước 3: Sửa quick_run.vbs**
```vbscript
' Sử dụng Python shortcut với admin
pythonPath = "C:\Path\To\Python (Admin).lnk"
```

---

## 🎯 So sánh các cách

| Cách | Ưu điểm | Nhược điểm | Khuyên dùng |
|------|---------|------------|-------------|
| **Cách 1: quick_run.vbs** | Đơn giản, tự động | Popup UAC mỗi lần | ⭐⭐⭐⭐⭐ |
| **Cách 2: quick_run_admin.bat** | Tương tự Cách 1 | Popup UAC mỗi lần | ⭐⭐⭐⭐ |
| **Cách 3: Task Scheduler** | Không popup UAC | Phức tạp setup | ⭐⭐⭐ |
| **Cách 4: Python Admin** | Luôn có quyền | Ảnh hưởng tất cả script | ⭐⭐ |

---

## 📝 Kiểm tra quyền admin

Thêm code này vào Python để kiểm tra:

```python
import ctypes
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == "__main__":
    if is_admin():
        print("✅ Running with administrator privileges")
    else:
        print("❌ NOT running with administrator privileges")
        print("⚠️ Some features may not work properly!")
```

---

## 🚀 Khuyến nghị

**Dùng Cách 1** (quick_run.vbs đã sửa):
- ✅ Đơn giản nhất
- ✅ Tự động yêu cầu quyền
- ✅ Không cần setup phức tạp
- ⚠️ Chấp nhận popup UAC mỗi lần khởi động

**Nếu muốn tắt popup UAC:**
- Dùng Cách 3 (Task Scheduler)
- Setup 1 lần, sau đó không popup nữa

---

## 🔧 Troubleshooting

### **Vẫn không có quyền admin?**

1. **Kiểm tra UAC settings:**
   - Win + R → `UserAccountControlSettings`
   - Đặt ở mức thấp nhất (không khuyên dùng)

2. **Chạy thử bằng tay:**
   ```bash
   # Chuột phải quick_run.vbs → Run as administrator
   ```

3. **Kiểm tra trong Python:**
   ```python
   import ctypes
   print(ctypes.windll.shell32.IsUserAnAdmin())  # Should return 1
   ```

### **Popup UAC quá phiền?**

→ Dùng Task Scheduler (Cách 3)

---

## ✅ Kết luận

File `quick_run.vbs` đã được cập nhật để **tự động yêu cầu quyền admin**.

Bạn không cần làm gì thêm, chỉ cần:
1. Chạy `quick_run.vbs`
2. Click "Yes" trên popup UAC
3. Ứng dụng chạy với quyền admin ✅

**Hoặc setup Task Scheduler để tắt popup UAC hoàn toàn!** 🚀
