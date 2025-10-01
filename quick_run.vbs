' Kiểm tra quyền admin và tự động yêu cầu nếu chưa có
If Not WScript.Arguments.Named.Exists("elevated") Then
    CreateObject("Shell.Application").ShellExecute "wscript.exe", """" & WScript.ScriptFullName & """ /elevated", "", "runas", 1
    WScript.Quit
End If

Set WshShell = CreateObject("WScript.Shell")

' Lấy đường dẫn thư mục hiện tại của script
scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Kiểm tra xem môi trường ảo có tồn tại không
envPython = scriptDir & "\env\Scripts\python.exe"
Set fso = CreateObject("Scripting.FileSystemObject")

If fso.FileExists(envPython) Then
    ' Sử dụng python từ môi trường ảo
    pythonPath = envPython
Else
    ' Sử dụng python từ hệ thống
    pythonPath = "python"
End If

' Chạy script Python với cửa sổ normal (1 = normal)
' Console sẽ tự động di chuyển xuống góc dưới trái bởi move_console.py
' 0 = Hidden, 1 = Normal, 2 = Minimized with focus, 7 = Minimized without focus
WshShell.Run """" & pythonPath & """ """ & scriptDir & "\src\autoLogin_v2.py""", 1, False
