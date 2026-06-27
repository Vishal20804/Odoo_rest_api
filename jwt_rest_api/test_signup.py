import requests

BASE_URL = "http://localhost:8072"


def signup():
    print("\n===== SIGNUP =====")

    name = input("Enter Name: ")
    login = input("Enter Login: ")
    password = input("Enter Password: ")

    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "name": name,
            "login": login,
            "password": password,
        },
        "id": 1
    }

    response = requests.post(
        f"{BASE_URL}/api/signup",
        json=payload
    )

    print("\nStatus Code:", response.status_code)
    print("Response:")
    print(response.json())


def login():
    print("\n===== LOGIN =====")

    login = input("Enter Login: ")
    password = input("Enter Password: ")

    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "login": login,
            "password": password,
        },
        "id": 1
    }

    response = requests.post(
        f"{BASE_URL}/api/login",
        json=payload
    )

    print("\nStatus Code:", response.status_code)

    data = response.json()

    print("Response:")
    print(data)

    # Agar login successful ho to token alag se print kar do
    if (
        data.get("result")
        and data["result"].get("success")
    ):
        print("\n========== TOKENS ==========")
        print("Access Token :")
        print(data["result"]["data"]["access_token"])

        print("\nRefresh Token :")
        print(data["result"]["data"]["refresh_token"])


while True:
    print("\n==============================")
    print("1. Signup")
    print("2. Login")
    print("3. Exit")
    print("==============================")

    choice = input("Enter Choice: ")

    try:
        if choice == "1":
            signup()
        elif choice == "2":
            login()
        elif choice == "3":
            print("Good Bye!")
            break
        else:
            print("Invalid Choice")
    except Exception as e:
        print("Error:", e)