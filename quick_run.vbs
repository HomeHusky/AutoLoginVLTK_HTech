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

' Chạy script Python với cửa sổ minimize (7 = minimized, 2 = minimized nhưng có focus)
WshShell.Run """" & pythonPath & """ """ & scriptDir & "\src\autoLogin.py""", 7, False
