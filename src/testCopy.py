import os
import json
import GlobalFunction as GF

def copy_auto_update_path_to_auto_update_path(json_path_accounts, json_path_fail):
# Đọc file accounts
    with open(os.path.join(GF.join_directory_data(), json_path_fail), 'w', encoding='utf-8') as f:
        f.write('')  # Ghi file trống để xóa dữ liệu

    with open(os.path.join(GF.join_directory_data(), json_path_accounts), 'r', encoding='utf-8') as accounts_file:
        data = json.load(accounts_file)
    
    # Kiểm tra xem file fail_server.json có tồn tại không
    if not os.path.exists(json_path_fail):
        # Tạo file nếu chưa tồn tại
        fail_data = {"auto_update_paths": []}
        with open(os.path.join(GF.join_directory_data(), json_path_fail), 'w', encoding='utf-8') as fail_file:
            json.dump(fail_data, fail_file, ensure_ascii=False, indent=4)
    
    # Đọc file fail_server.json
    with open(os.path.join(GF.join_directory_data(), json_path_fail), 'r', encoding='utf-8') as fail_file:
        fail_data = json.load(fail_file)
    
    # Lấy danh sách server_fail hiện tại
    server_fail_list = fail_data.get("auto_update_paths", [])
    
    # Duyệt qua từng account và thêm auto_update_path nếu chưa có
    for account in data["accounts"]:
        auto_update_path = account.get("auto_update_path")
        if auto_update_path and auto_update_path not in server_fail_list:
            server_fail_list.append(auto_update_path)
    
    # Cập nhật lại fail_server.json
    fail_data["auto_update_paths"] = server_fail_list
    with open(os.path.join(GF.join_directory_data(), json_path_fail), 'w', encoding='utf-8') as fail_file:
        json.dump(fail_data, fail_file, ensure_ascii=False, indent=4)

def copy_auto_update_path_to_fix_web_ctcx_path(json_path_accounts = 'accounts.json', json_path_fail = 'fix_web_ctcx.json'):

    with open(os.path.join(GF.join_directory_data(), json_path_fail), 'w', encoding='utf-8') as f:
        f.write('')  # Ghi file trống để xóa dữ liệu

    with open(os.path.join(GF.join_directory_data(), json_path_accounts), 'r', encoding='utf-8') as accounts_file:
        data = json.load(accounts_file)
    
    # Kiểm tra xem file json_path_fail có tồn tại không
    if not os.path.exists(json_path_fail):
        # Tạo file nếu chưa tồn tại
        fail_data = {"fix_web_ctcx_paths": []}
        with open(os.path.join(GF.join_directory_data(), json_path_fail), 'w', encoding='utf-8') as fail_file:
            json.dump(fail_data, fail_file, ensure_ascii=False, indent=4)
    
    # Đọc file fail_server.json
    with open(os.path.join(GF.join_directory_data(), json_path_fail), 'r', encoding='utf-8') as fail_file:
        fail_data = json.load(fail_file)
    
    # Lấy danh sách server_fail hiện tại
    server_fail_list = fail_data.get("fix_web_ctcx_paths", [])
    server_online = []
    
    # Duyệt qua từng account và thêm auto_update_path nếu chưa có
    for account in data["accounts"]:
        auto_update_path = account.get("auto_update_path")
        isOnline = account.get("is_logged_in")
        if isOnline == False:
            if auto_update_path not in server_online:
                if auto_update_path and auto_update_path not in server_fail_list:
                    server_fail_list.append(auto_update_path)
        else:
            server_online.append(auto_update_path)
    # Cập nhật lại fail_server.json
    fail_data["fix_web_ctcx_paths"] = server_fail_list
    with open(os.path.join(GF.join_directory_data(), json_path_fail), 'w', encoding='utf-8') as fail_file:
        json.dump(fail_data, fail_file, ensure_ascii=False, indent=4)
    
    print(f"Sao chép đường dẫn auto_update_path thành công vào {json_path_fail}.")

def replace_AutoUpdate_to_fix_web_ctcx(file_path):
    # Đọc nội dung file JSON
    with open(os.path.join(GF.join_directory_data(), file_path), 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Thay đổi "AutoUpdate.exe" thành "fix_web_ctcx"
    data["fix_web_ctcx_paths"] = [path.replace("AutoUpdate.exe", "fix_web_ctcx") for path in data["fix_web_ctcx_paths"]]

    # Ghi lại nội dung đã thay đổi vào file
    with open(os.path.join(GF.join_directory_data(), file_path), 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# Đường dẫn đến file JSON
json_path_accounts = 'accounts.json'
json_path_fail = 'autoUpdate_path.json'
fix_web_ctcx_path = 'fix_web_ctcx.json'
# copy_auto_update_path_to_auto_update_path(json_path_accounts, json_path_fail)

# copy_auto_update_path_to_fix_web_ctcx_path(json_path_accounts, fix_web_ctcx_path)

replace_AutoUpdate_to_fix_web_ctcx('fix_web_ctcx.json')