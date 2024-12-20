import requests
import GlobalFunction as GF
import os
import json

def load_workstation_id(filepath='monitor_time.json'):
    # Tải thông tin workstation ID từ file JSON
    with open(os.path.join(GF.join_directory_data(), filepath), 'r') as f:
        data = json.load(f)
        return data['title_mail']

def send_data(total_income, low_income_accounts, check_time, kpi_value, car_list, time_loop_send):
    # Lấy Workstation ID
    workstation_id = load_workstation_id()

    # URL mới với cổng 3000
    url = 'http://27.69.250.4:3030/receive-data'

    # Dữ liệu cần gửi
    data = {
        "workstation_id": workstation_id,
        "accounts": total_income,
        "low_income_accounts": low_income_accounts,
        "check_time": check_time,
        "kpi_value": kpi_value,
        "car_list": car_list,
        "time_loop_send": time_loop_send,
        # "accounts": [
        #     {"account": "Account1", "quantity": 100},
        #     {"account": "Account2", "quantity": 200},
        #     {"account": "Account3", "quantity": 150},
        # ]
    }

    print("data: ", data)

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
