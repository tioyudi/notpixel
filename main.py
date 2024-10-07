import requests
import time

# API Base URL
base_url = "https://notpx.app/api/v1"

# Load tokens from file
with open("query.txt", "r") as file:
    tokens = [token.strip() for token in file.readlines()]

# Countdown function
def countdown(minutes):
    seconds = minutes * 60
    while seconds:
        mins, secs = divmod(seconds, 60)
        print(f"Menunggu {mins:02d}:{secs:02d} sebelum menjalankan ulang...", end="\r")
        time.sleep(1)
        seconds -= 1
    print("\nMulai ulang...")

# Function to handle API requests
def get_request(endpoint, headers):
    response = requests.get(f"{base_url}{endpoint}", headers=headers)
    response.raise_for_status()  # Raise error for bad responses
    return response.json()

def post_request(endpoint, payload, headers):
    response = requests.post(f"{base_url}{endpoint}", json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

# Function to refresh the token
def refresh_token(headers):
    print("Token tidak valid, mencoba untuk memperbarui token dengan POST...")
    # Define the payload needed to refresh the token (this is an example)
    payload = {
        # Include necessary parameters for token refresh
    }
    refresh_response = post_request("/auth/refresh", payload, headers)  # Adjust the endpoint accordingly
    new_token = refresh_response.get("newToken")  # Adjust based on actual response
    print(f"Token baru diperoleh: {new_token}")
    return new_token

# Loop for each token
while True:
    for idx, token in enumerate(tokens):
        print(f"Menjalankan script dengan token {idx + 1}")

        headers = {
            "accept": "application/json, text/plain, */*",
            "authorization": f"initData {token}",
            "origin": "https://app.notpx.app",
            "referer": "https://app.notpx.app/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }

        try:
            user_info = get_request("/users/me", headers)
            print(f"[Name]: {user_info['firstName']}, [Balance]: {user_info['balance']}")

            status_info = get_request("/mining/status", headers)
            charges = status_info['charges']
            print(f"[Total Repaint]: {status_info['repaintsTotal']}, [Balance Repaint]: {charges}")

            if charges > 0:
                for _ in range(charges):
                    payload = {"pixelId": 711514, "newColor": "#000000"}
                    response = post_request("/repaint/start", payload, headers)
                    print(f"[Balance]: {response['balance']}")
                    time.sleep(0.5)  # Rate limiting
            else:
                print("Tidak ada charges tersedia")

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                # Refresh the token and update headers
                new_token = refresh_token(headers)
                headers["authorization"] = f"initData {new_token}"  # Update headers with new token

                # Retry the original requests after refreshing the token
                try:
                    user_info = get_request("/users/me", headers)
                    print(f"[Name]: {user_info['firstName']}, [Balance]: {user_info['balance']}")

                    status_info = get_request("/mining/status", headers)
                    charges = status_info['charges']
                    print(f"[Total Repaint]: {status_info['repaintsTotal']}, [Balance Repaint]: {charges}")

                    if charges > 0:
                        for _ in range(charges):
                            payload = {"pixelId": 711514, "newColor": "#000000"}
                            response = post_request("/repaint/start", payload, headers)
                            print(f"[Balance]: {response['balance']}")
                            time.sleep(0.5)  # Rate limiting
                    else:
                        print("Tidak ada charges tersedia")

                except requests.exceptions.HTTPError as e:
                    print(f"Error after refreshing token: {e}")

            else:
                print(f"Error: {e}")

        except KeyError as e:
            print(f"Key error: {e} - check the structure of the API response.")

        print("Akun Berikutnya")

    print("Semua akun selesai dimuat")
    countdown(5)
