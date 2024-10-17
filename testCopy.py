import os
import json
import GlobalFunction as GF

def copy_auto_update_path_to_auto_update_path(accounts_file, output_file):
    # Kiểm tra xem file accounts.json có tồn tại không
    if not os.path.exists(accounts_file):
        print(f"File {accounts_file} không tồn tại.")
        return
    
    # Đọc dữ liệu từ accounts.json
    data = GF.read_json_file(accounts_file)
    
    # Chuẩn bị mảng chỉ chứa auto_update_path từ accounts.json
    auto_update_paths = [account.get("auto_update_path") for account in data.get("accounts", [])]
    
    # Kiểm tra nếu file autoUpdate_path.json đã tồn tại
    if os.path.exists(output_file):
        print(f"File {output_file} đã tồn tại, sẽ ghi đè nội dung.")
    
    # Ghi mảng auto_update_paths vào autoUpdate_path.json
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"auto_update_paths": auto_update_paths}, f, ensure_ascii=False, indent=4)
    
    print(f"Sao chép đường dẫn auto_update_path thành công vào {output_file}.")

# Gọi hàm
accounts_file = 'accounts.json'
output_file = 'autoUpdate_path.json'
copy_auto_update_path_to_auto_update_path(accounts_file, output_file)
