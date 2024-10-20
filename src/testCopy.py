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

# Đường dẫn đến file JSON
json_path_accounts = 'accounts.json'
json_path_fail = 'autoUpdate_path.json'

copy_auto_update_path_to_auto_update_path(json_path_accounts, json_path_fail)
