import requests

def print_hello_world():
    try:
        response = requests.get('https://httpbin.org/get')
        if response.status_code == 200:
            print("Hello, World!")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    print_hello_world()