import cv2
import socket
import struct
import pickle
import time
import serial
from datetime import datetime
import threading
import queue

# 전역 변수 설정
velocity = 0
encoder_l = 0
encoder_r = 0

# 아두이노 시리얼 통신 설정
ser = serial.Serial('/dev/ttyArduino', 9600, timeout=1)  # 보드레이트를 115200으로 증가
time.sleep(2)  # 시리얼 연결 안정화를 위한 대기 시간

pulsepermm = 0.0889
start_encoder_l = 0
start_encoder_r = 0

# 엔코더 데이터를 저장할 큐
encoder_queue = queue.Queue(maxsize=100)
def motor_forward():
    ser.write(b'F') # 아두이노로 'F' 전송 (전진)    

def motor_stop():
    ser.write(b'S')

def read_encoder():
    global encoder_l, encoder_r
    while True:
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').rstrip()
                parts = line.split()
                if len(parts) >= 4:
                    encoder_l = abs(int(parts[1]))
                    encoder_r = abs(int(parts[3]))
                    encoder_queue.put((encoder_l, encoder_r, time.time()))
            except Exception as e:
                print(f"Error reading encoder: {e}")
        time.sleep(0.001)  # 짧은 대기 시간

def calculate_velocity():
    global velocity, start_encoder_l, start_encoder_r
    last_time = time.time()
    while True:
        if not encoder_queue.empty():
            encoder_l, encoder_r, current_time = encoder_queue.get()
            elapsed_time = current_time - last_time
            if elapsed_time >= 0.1:  # 100ms마다 속도 계산
                rotation_encoder_l = encoder_l - start_encoder_l
                rotation_encoder_r = encoder_r - start_encoder_r

                distance_l = rotation_encoder_l * pulsepermm
                distance_r = rotation_encoder_r * pulsepermm

                velocity_l = distance_l / elapsed_time
                velocity_r = distance_r / elapsed_time
                
                velocity = (velocity_l + velocity_r) / 2

                start_encoder_l = encoder_l
                start_encoder_r = encoder_r
                last_time = current_time

                print(f"Velocity: {velocity}")
        time.sleep(0.001)  # 짧은 대기 시간

def handle_client(client_socket, client_address):
    print(f"Connected to {client_address}")
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv2.CAP_PROP_FPS, 30)  # FPS 설정

    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print("width:", width, ", height:", height)

    count = 0
    try:
        while cap.isOpened():
            count += 1

            ret, frame = cap.read()
            if not ret:
                break
            
            # 프레임과 속도 데이터를 하나의 패킷으로 만듦
            data = pickle.dumps((frame, velocity))
            count_data = struct.pack("I", count)
            data_with_count = count_data + data
            message_size = struct.pack("Q", len(data_with_count))

            client_socket.sendall(message_size + data_with_count)

            time.sleep(0.1)

    except (BrokenPipeError, ConnectionResetError):
        print(f"Client {client_address} disconnected")
    finally:
        cap.release()
        client_socket.close()

def main():
    motor_forward()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 9999))
    server_socket.listen(5)
    print("Server started. Waiting for connections...")

    # 엔코더 읽기 스레드 시작
    encoder_thread = threading.Thread(target=read_encoder)
    encoder_thread.daemon = True
    encoder_thread.start()

    # 속도 계산 스레드 시작
    velocity_thread = threading.Thread(target=calculate_velocity)
    velocity_thread.daemon = True
    velocity_thread.start()

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
        except KeyboardInterrupt:
            motor_stop()
            print("Server is shutting down...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

    server_socket.close()
    ser.close()  # 시리얼 포트 닫기

if __name__ == "__main__":
    main()