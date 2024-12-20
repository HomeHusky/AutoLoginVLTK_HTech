import requests
import GlobalFunction as GF
import os
import json

def load_workstation_id(filepath='monitor_time.json'):
    # Tải thông tin workstation ID từ file JSON
    with open(os.path.join(GF.join_directory_data(), filepath), 'r') as f:
        data = json.load(f)
        return data['title_mail']

def send_data():
    # Lấy Workstation ID
    workstation_id = load_workstation_id()

    # URL mới với cổng 3000
    url = 'http://27.69.250.4:3000/receive-data'

    # Dữ liệu cần gửi
    data = {
        "workstation_id": workstation_id,
        "accounts": [
            {"account": "Account1", "quantity": 100},
            {"account": "Account2", "quantity": 200},
            {"account": "Account3", "quantity": 150},
        ]
    }

    try:
        # Gửi yêu cầu POST đến server
        response = requests.post(url, json=data, allow_redirects=False)
        if response.status_code == 200:
            print("Gửi dữ liệu thành công.")
            print("Phản hồi từ server:", response.json())
        else:
            print(f"Lỗi: {response.status_code} - {response.text}")
    except Exception as e:
        print("Lỗi khi gửi dữ liệu:", e)

if __name__ == "__main__":
    send_data()
