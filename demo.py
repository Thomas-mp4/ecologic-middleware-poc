import time
import requests

BASE_URL = "http://127.0.0.1:8000"


def print_response(endpoint, response):
    print(f"\n--- Hitting Endpoint: {endpoint} ---")
    print(f"Response Status Code: {response.status_code}")
    try:
        print("Response JSON:")
        print(response.json())
    except ValueError:
        print("No JSON response")


def simulate_correct_sensor_data():
    endpoint = "/sensor-data"
    payload = {
        "sensor_id": "temp-sensor-001",
        "value": 25.3,
        "timestamp": "2025-01-28T15:00:00Z",
    }
    response = requests.post(f"{BASE_URL}{endpoint}", json=payload)
    print_response(endpoint, response)


def simulate_incorrect_sensor_data():
    endpoint = "/sensor-data"
    payload = {
        "sensor_id": "",
        "value": "invalid_value",
        "timestamp": "2025-01-28T15:00:00Z",
    }
    response = requests.post(f"{BASE_URL}{endpoint}", json=payload)
    print_response(endpoint, response)


def simulate_get_sensor_data():
    endpoint = "/sensor-data/temp-sensor-001"
    response = requests.get(f"{BASE_URL}{endpoint}")
    print_response(endpoint, response)


def simulate_get_bim_object():
    endpoint = "/bim/door-001"
    response = requests.get(f"{BASE_URL}{endpoint}")
    print_response(endpoint, response)


def simulate_update_bim_object():
    endpoint = "/bim/door-001"
    payload = {"status": "Installed"}
    response = requests.put(f"{BASE_URL}{endpoint}", json=payload)
    print_response(endpoint, response)


def simulate_create_work_order():
    endpoint = "/erp/work-order"
    payload = {
        "work_order_id": "WO-12345",
        "description": "Routine maintenance for crane",
        "cost_center": "CC-1001",
        "due_date": "2025-02-15T00:00:00Z",
    }
    response = requests.post(f"{BASE_URL}{endpoint}", json=payload)
    print_response(endpoint, response)


def simulate_invalid_work_order():
    endpoint = "/erp/work-order"
    payload = {
        "work_order_id": "",
        "description": "",
        "cost_center": "CC-1001",
        "due_date": "invalid-date-format",
    }
    response = requests.post(f"{BASE_URL}{endpoint}", json=payload)
    print_response(endpoint, response)


def simulate_upload_manual_data():
    endpoint = "/upload/manual-data"
    file_data = ("data.csv", b"id,value\n1,10\n2,20", "text/csv")
    response = requests.post(f"{BASE_URL}{endpoint}", files={"file": file_data})
    print_response(endpoint, response)


def simulate_send_notification():
    endpoint = "/notifications"
    data = {"email": "user@example.com", "message": "This is a test notification."}
    response = requests.post(f"{BASE_URL}{endpoint}", data=data)
    print_response(endpoint, response)


def simulate_get_serial_numbers():
    params = {
        "top": 5,
        "skip": 0,
    }
    endpoint = "/erp/serial-numbers"
    response = requests.get(f"{BASE_URL}{endpoint}", params=params)
    print_response(f"{endpoint}?{response.request.path_url.split('?')[1]}", response)


def main():
    print("Starting API Simulation...")

    simulate_correct_sensor_data()
    time.sleep(1)

    simulate_incorrect_sensor_data()
    time.sleep(1)

    simulate_get_sensor_data()
    time.sleep(1)

    simulate_get_bim_object()
    time.sleep(1)

    simulate_update_bim_object()
    time.sleep(1)

    simulate_create_work_order()
    time.sleep(1)

    simulate_invalid_work_order()
    time.sleep(1)

    simulate_upload_manual_data()
    time.sleep(1)

    simulate_send_notification()
    time.sleep(1)

    simulate_get_serial_numbers()
    time.sleep(1)

    print("\nAPI Simulation Completed.")


if __name__ == "__main__":
    main()
