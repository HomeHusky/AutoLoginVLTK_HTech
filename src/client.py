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

    # URL với hai cổng
    urls = ['http://171.251.6.89:3030/receive-data', 'http://171.251.6.89:3000/receive-data']

    # Dữ liệu cần gửi
    data = {
        "workstation_id": workstation_id,
        "accounts": total_income,
        "low_income_accounts": low_income_accounts,
        "check_time": check_time,
        "kpi_value": kpi_value,
        "car_list": car_list,
        "time_loop_send": time_loop_send,
    }

    print("data: ", data)

    for url in urls:
        try:
            # Gửi yêu cầu POST đến server
            response = requests.post(url, json=data, allow_redirects=False)
            if response.status_code == 200:
                print("Gửi dữ liệu thành công đến:", url)
                print("Phản hồi từ server:", response.json())
                return  # Thoát nếu gửi thành công
            else:
                print(f"Lỗi: {response.status_code} - {response.text} khi gửi đến {url}")
        except Exception as e:
            print(f"Lỗi khi gửi dữ liệu đến {url}:", e)

    print("Không thể gửi dữ liệu đến bất kỳ server nào.")

if __name__ == "__main__":
    # Cung cấp các tham số giả để kiểm tra
    send_data(total_income=[], low_income_accounts=[], check_time="2024-12-30 12:00:00", 
              kpi_value=100, car_list=[], time_loop_send=60)