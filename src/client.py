import requests
import GlobalFunction as GF
import os
import json

def load_workstation_id(filepath='monitor_time.json'):
    with open(os.path.join(GF.join_directory_data(), filepath), 'r') as f:
        data = json.load(f)
        return data['title_mail']

def send_data():
    workstation_id = load_workstation_id()

    # URL của server
    url = 'http://192.168.2.11:5000/receive-data'

    # Dữ liệu mẫu cần gửi (gửi nhiều tài khoản trong 1 lần)
    data = {
        "workstation_id": workstation_id,
        "accounts": [
            {"account": "Account1", "quantity": 100},
            {"account": "Account2", "quantity": 200},
            {"account": "Account3", "quantity": 150},
        ]
    }

    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("Gửi dữ liệu thành công.")
            print("Phản hồi từ server:", response.json())
        else:
            print(f"Lỗi: {response.status_code} - {response.text}")
    except Exception as e:
        print("Lỗi khi gửi dữ liệu:", e)
