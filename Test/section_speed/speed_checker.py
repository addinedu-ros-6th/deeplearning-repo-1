import socket 
import serial
import time

SpeedChecker = serial.Serial(port='/dev/ttyACM0', baudrate= 9600, timeout= 1)

def handle_client(client_socket, client_address):
    print(f"Connected to {client_address}") 
   
    try:
        while True:
            a=SpeedChecker.readline()
            section_speed = a.decode()
            section_speed = section_speed.strip()
            print(section_speed)

            if section_speed:  # section_speed가 비어있지 않으면 전송
                client_socket.sendall(section_speed.encode('utf-8'))

            time.sleep(0.1)

    except (BrokenPipeError, ConnectionResetError):
        print(f"Client {client_address} disconnected")
    finally:
        client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind(('0.0.0.0', 3333)) 
    server_socket.listen(5) 
    print("Server started. Waiting for connections...")

    while True:
        try:
            client_socket, client_address = server_socket.accept() 
            handle_client(client_socket, client_address)
        except KeyboardInterrupt:
            print("Server is shutting down...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

    server_socket.close()

if __name__ == "__main__":
    main()