import cv2
import socket
import struct
import pickle
import time
from ultralytics import YOLO 

# 클래스 보이는 버전

# 클라이언트 소켓 설정
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.0.9', 9999))
data = b""
payload_size = struct.calcsize("Q")

print(payload_size)

model = YOLO('/home/sh/dev_ws/best.pt') 

while True:
    
    while len(data) < payload_size:       
        data += client_socket.recv(4096)
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("Q", packed_msg_size)[0]

    while len(data) < msg_size:
        data += client_socket.recv(4096)
    frame_data = data[:msg_size]
    data = data[msg_size:]
    frame = pickle.loads(frame_data)
    frame = cv2.resize(frame, (640, 480))

    # OpenCV를 사용하여 수신된 프레임 분석
    if frame is not None and frame.size > 0:  # Ensure frame is valid

        results = model(frame, verbose=True)
        # results = model.track(frame, persist=True) 

        # print(results) 
        # print() 
        # print() 

        # 추론 결과에서 세그멘테이션 마스크 및 바운딩 박스 정보 추출
        for result in results:
            masks = result.masks.data.cpu().numpy() if result.masks else []
            boxes = result.boxes.data.cpu().numpy() if result.boxes else []
            scores = result.boxes.conf.cpu().numpy() if result.boxes else []
            class_ids = result.boxes.cls.cpu().numpy() if result.boxes else []

            # 세그멘테이션 마스크 그리기
            for mask in masks:
                mask = (mask * 255).astype('uint8')  # 마스크를 0-255 범위로 변환
                colored_mask = cv2.merge([mask, mask, mask])  # 마스크를 3채널로 변환

                print("frame type:", type(frame)) 
                print("frame.shape:", frame.shape)
                print("colored_mask.shape:", colored_mask.shape)

                frame = cv2.addWeighted(frame, 1, colored_mask, 0.5, 0)  # 프레임에 마스크를 합성

            # 바운딩 박스 그리기
            for i, box in enumerate(boxes):
                x1, y1, x2, y2 = map(int, box[:4])
                score = scores[i]
                
                # 바운딩 박스 그리기
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # 점수 텍스트 표시
                label = f'{score:.2f}'
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # 클래스 id 표시
                class_id = int(class_ids[i])
                class_name = model.names[class_id]
                label = f'{class_name}'
                cv2.putText(frame, label, (x1 + 40, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.imshow('Received', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        print("Received an empty frame or invalid frame.")

client_socket.close()
cv2.destroyAllWindows()



