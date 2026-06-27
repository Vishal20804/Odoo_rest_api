print("RUNNING UPDATED SCRIPT")
import requests
BASE_URL = "http://localhost:8072"

ACCESS_TOKEN = None


def print_response(response):
    print("\nStatus Code:", response.status_code)
    try:
        print(response.json())
    except Exception:
        print(response.text)


def auth_headers():
    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }


# ------------------ SIGNUP ------------------ #

def signup():
    name = input("Name: ")
    login = input("Login: ")
    password = input("Password: ")

    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "name": name,
            "login": login,
            "password": password,
        },
        "id": 1,
    }

    response = requests.post(
        f"{BASE_URL}/api/signup",
        json=payload
    )

    print_response(response)


# ------------------ LOGIN ------------------ #

def login():
    global ACCESS_TOKEN

    login = input("Login: ")
    password = input("Password: ")

    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "login": login,
            "password": password,
        },
        "id": 1,
    }

    response = requests.post(
        f"{BASE_URL}/api/login",
        json=payload
    )

    print_response(response)

    data = response.json()

    if data.get("result", {}).get("success"):
        ACCESS_TOKEN = data["result"]["data"]["access_token"]
        print("\nLogin Successful.")
        print("Access Token Saved.")


# ------------------ GET PRODUCTS ------------------ #

def get_products(show=True):

    if not ACCESS_TOKEN:
        print("Please Login First.")
        return []
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {},
        "id": 1
    }

    response = requests.post(
        f"{BASE_URL}/api/products/list",
        headers=auth_headers(),
        json=payload
    )
    print("--------",response)
    print_response(response)

    try:
        result = response.json()["result"]

        if result["success"]:
            products = result["data"]

            if show:
                print("\n=========== PRODUCTS ===========")

                for p in products:
                    print(
                        f"ID : {p['id']} | "
                        f"Name : {p['name']} | "
                        f"Price : {p['sale_price']}"
                    )

            return products

    except:
        pass

    return []


# ------------------ CREATE PRODUCT ------------------ #

def create_product():

    if not ACCESS_TOKEN:
        print("Please Login First.")
        return

    name = input("Product Name : ")
    price = float(input("Sale Price : "))

    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "name": name,
            "list_price": price,
        },
        "id": 1,
    }

    response = requests.post(
        f"{BASE_URL}/api/products/create",
        headers=auth_headers(),
        json=payload,
    )

    print_response(response)


# ------------------ UPDATE PRODUCT ------------------ #

def update_product():

    if not ACCESS_TOKEN:
        print("Please Login First.")
        return

    products = get_products(False)

    if not products:
        return

    print("\nProducts:\n")

    for p in products:
        print(f"{p['id']} -> {p['name']} (₹{p['sale_price']})")

    product_id = input("\nEnter Product ID : ")

    name = input("New Name : ")
    price = float(input("New Price : "))

    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "name": name,
            "list_price": price,
        },
        "id": 1,
    }

    response = requests.post(
        f"{BASE_URL}/api/products/update/{product_id}",
        headers=auth_headers(),
        json=payload,
    )

    print_response(response)


# ------------------ DELETE PRODUCT ------------------ #

def delete_product():

    if not ACCESS_TOKEN:
        print("Please Login First.")
        return

    products = get_products(False)

    if not products:
        return

    print("\nProducts:\n")

    for p in products:
        print(f"{p['id']} -> {p['name']}")

    product_id = input("\nEnter Product ID : ")
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {},
        "id": 1,
    }
    response = requests.post(
        f"{BASE_URL}/api/products/delete/{product_id}",
        headers=auth_headers(),
        json=payload
    )

    print_response(response)


# ------------------ MENU ------------------ #

while True:

    print("""
==================================
1. Signup
2. Login
3. List Products
4. Create Product
5. Update Product
6. Delete Product
7. Exit
==================================
""")

    choice = input("Choice : ")

    if choice == "1":
        signup()

    elif choice == "2":
        login()

    elif choice == "3":
        get_products()

    elif choice == "4":
        create_product()

    elif choice == "5":
        update_product()

    elif choice == "6":
        delete_product()

    elif choice == "7":
        print("Good Bye...")
        break

    else:
        print("Invalid Choice")