from ultralytics import YOLO
import numpy as np
import cv2

class Inference:
    def __init__(self):
        self.model_lane = YOLO('../models/best_lane.pt')
        self.model_sign = YOLO('../models/everything_2.pt')


    # return = (frame, objects)
    def predict(self, frame: np.ndarray) -> tuple[np.ndarray, list[dict[str: tuple[int, int, int, int]]], set[int]]:
        results_lane = self.model_lane(frame, verbose=False)
        results_sign = self.model_sign(frame, verbose=False)

        detects = []
        cls_list = []

        for result in results_lane:
            masks = result.masks.data.cpu().numpy() if result.masks else []
            boxes = result.boxes.data.cpu().numpy() if result.boxes else []
            scores = result.boxes.conf.cpu().numpy() if result.boxes else []
            class_ids = result.boxes.cls.cpu().numpy() if result.boxes else []

            # 세그멘테이션 마스크 그리기
            for mask in masks:
                mask = (mask * 255).astype('uint8')  # 마스크를 0-255 범위로 변환
                colored_mask = cv2.merge([mask, mask, mask])  # 마스크를 3채널로 변환
                frame = cv2.addWeighted(frame, 1, colored_mask, 0.5, 0)  # 프레임에 마스크를 합성

            # 바운딩 박스 그리기
            for i, box in enumerate(boxes):
                x1, y1, x2, y2 = map(int, box[:4])
                score = scores[i]
                # 바운딩 박스 그리기
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                # 점수 텍스트 표시
                label = f'{score:.2f}'
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 2)
                # 클래스 id 표시
                class_id = int(class_ids[i])
                class_name = self.model_lane.names[class_id]
                label = f'{class_name}'
                cv2.putText(frame, label, (x1 + 40, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 2)

                detects.append({label: (x1, y1, x2, y2)})
                cls_list.append(class_id)


        for result in results_sign:
            masks = result.masks.data.cpu().numpy() if result.masks else []
            boxes = result.boxes.data.cpu().numpy() if result.boxes else []
            scores = result.boxes.conf.cpu().numpy() if result.boxes else []
            class_ids = result.boxes.cls.cpu().numpy() if result.boxes else []

            # 세그멘테이션 마스크 그리기
            for mask in masks:
                mask = (mask * 255).astype('uint8')  # 마스크를 0-255 범위로 변환
                colored_mask = cv2.merge([mask, mask, mask])  # 마스크를 3채널로 변환
                frame = cv2.addWeighted(frame, 1, colored_mask, 0.5, 0)  # 프레임에 마스크를 합성

            # 바운딩 박스 그리기
            for i, box in enumerate(boxes):
                x1, y1, x2, y2 = map(int, box[:4])
                score = scores[i]
                # 바운딩 박스 그리기
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # 점수 텍스트 표시
                label = f'{score:.2f}'
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 2)
                # 클래스 id 표시
                class_id = int(class_ids[i])
                class_name = self.model_sign.names[class_id]
                label = f'{class_name}'
                cv2.putText(frame, label, (x1 + 40, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 2)

                detects.append({label: (x1, y1, x2, y2)})
                cls_list.append(class_id+1)
        
        cls_set = set(cls_list)

        return (frame, detects, cls_set)
    