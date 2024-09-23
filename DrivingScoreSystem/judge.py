from collections import deque
import numpy as np
import cv2
import time

'''
PenaltyData table:
id  penalty_type                    penalty_score
1   kidzone_speed_violation         30
2   section_speed_violation         10
3   speed_violation                 20
4   traffic_sign_green_violation    15
5   traffic_sign_red_violation      15
6   stop_line_violation             10
7   lane_violation                  5
8   human_on_crosswalk_violation    15
'''

class Judge:
    def __init__(self):
        self.charge = ""
        
        length = 5
        self.lane = deque(maxlen=length)
        self.dotted_lane = deque(maxlen=length)
        self.yellow_lane = deque(maxlen=length)
        self.stop_line = deque(maxlen=length)
        self.crosswalk = deque(maxlen=length)
        self.limit_30 = deque(maxlen=length)
        self.limit_50 = deque(maxlen=length)
        self.limit_100 = deque(maxlen=length)
        self.kidzone = deque(maxlen=length)
        self.section_start = deque(maxlen=length)
        self.section_end = deque(maxlen=length)
        self.oneway = deque(maxlen=length)
        self.traffic_light_green = deque(maxlen=length)
        self.traffic_light_yellow = deque(maxlen=length)
        self.traffic_light_red = deque(maxlen=length)
        self.person = deque(maxlen=length)

        # 상태 변수 초기화
        self.lane_status = 0
        self.dotted_lane_status = 0
        self.yellow_lane_status = 0
        self.stop_line_status = 0
        self.crosswalk_status = 0
        self.limit_30_status = 0
        self.limit_50_status = 0
        self.limit_100_status = 0
        self.kidzone_status = 0
        self.section_start_status = 0
        self.section_end_status = 0
        self.oneway_status = 0
        self.traffic_light_green_status = 0
        self.traffic_light_yellow_status = 0
        self.traffic_light_red_status = 0
        self.person_status = 0
        self.redzone_status = 0
         # 미감지 변수 초기화
        self.lane_miss_count = 0
        self.dotted_lane_miss_count = 0
        self.yellow_lane_miss_count = 0
        self.stop_line_miss_count = 0
        self.crosswalk_miss_count = 0
        self.limit_30_miss_count = 0
        self.limit_50_miss_count = 0
        self.limit_100_miss_count = 0
        self.kidzone_miss_count = 0
        self.section_start_miss_count = 0
        self.section_end_miss_count = 0
        self.oneway_miss_count = 0
        self.traffic_light_green_miss_count = 0
        self.traffic_light_yellow_miss_count = 0
        self.traffic_light_red_miss_count = 0
        self.person_miss_count = 0
        self.redzone_miss_count = 0
        self.detect_light_green_time = 0
        
        self.stop_line_status_prev = 0
        self.kidzone_prev = 0
        self.detect_light_green_time_prev = 0

        #벌점 사항
        self.stop_line_prev = 0
        self.crosswalk_prev = 0
        self.speed_limit_30_prev = 0
        self.speed_limit_50_prev = 0
        self.speed_limit_100_prev = 0
        self.green_signal_prev = 0
        self.limit_100_status_prev = 0
        self.speed_violation_prev = 0
        self.traffic_sign_green_violation_prev = 0
        self.traffic_sign_red_violation_prev = 0
        self.stop_line_violation_prev = 0
        self.human_on_crosswalk_violation_prev = 0

        # self.velocity = 30

        # 새로운 객체 감지
        self.objects_list = set()
        self.objects_list_prev = set()
        self.objects_cnt = len(self.objects_list)
        self.objects_cnt_prev = self.objects_cnt
        self.is_new_object = False
        self.new_object = set()
       
        self.detected = [self.lane, self.dotted_lane, self.limit_100, self.traffic_light_green,
                         self.crosswalk, self.oneway, self.section_start, self.stop_line,
                         self.traffic_light_red, self.kidzone, self.limit_30, self.person,
                         self.traffic_light_yellow, self.yellow_lane, self.limit_50, self.section_end]
        
    def verdict(self, detects: dict[str: tuple[int, int, int, int]], cls_set: set[int], velocity, frame, section_speed) -> tuple[str, int]:
        self.objects_list = set()
        self.objects_cnt = len(self.objects_list)
        self.is_new_object = False
        # print('section_speed========================',section_speed)
        self.detected_classes = set()

        charge_id = 0

        detect_count = 4
        undetected_count = 3

        kidzone_speed_violation = 30
        section_speed_violation = 10
        speed_violation = 20
        traffic_sign_green_violation = 15
        traffic_sign_red_violation = 15
        stop_line_violation = 10
        lane_violation = 5
        human_on_crosswalk_violation = 15
   
        self.penalty = 0    

        # 탐지된 객체 업데이트
        for idx in range(len(self.detected)):
            if idx in cls_set:
                self.detected[idx].append(True)
            else:
                self.detected[idx].append(False)

        # print(detects)
        
        for detect in detects:
            self.detected_classes.update(detect.keys())

            for cls, bb_coordinates in detect.items():
                x1, y1, x2, y2 = bb_coordinates
                width = x2 - x1
                height = y2 - y1
                area = width * height
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2

                # 새로운 객체 감지
                self.objects_list.add(cls)
                self.objects_cnt = len(self.objects_list)

                if (self.objects_cnt > self.objects_cnt_prev) and (self.objects_list != self.objects_list_prev):
                    print("new object detected!!!")
                    self.is_new_object = True
                    self.new_object = self.objects_list - self.objects_list_prev
            

                if cls == "lane" and (len(self.lane) == 5) and (self.lane.count(True) >= detect_count):
                    self.lane_status = 1
                    
                elif cls == "dotted_lane" and (len(self.dotted_lane) == 5) and (self.dotted_lane.count(True) >= detect_count):
                    self.dotted_lane_status = 1

                elif cls == "yellow_lane" and (len(self.yellow_lane) == 5) and (self.yellow_lane.count(True) >= detect_count):
                    self.yellow_lane_status = 1

                elif cls == "stop_line" and (len(self.stop_line) == 5) and (self.stop_line.count(True) >= detect_count):
                    if area > 8000:    
                        self.stop_line_status = 1
                        self.stop_line_status_prev = 1

                elif cls == "crosswalk" and (len(self.crosswalk) == 5) and (self.crosswalk.count(True) >= detect_count):
                    if area > 20000:
                        self.crosswalk_status = 1  

                elif cls == "limit_30" and (len(self.limit_30) == 5) and (self.limit_30.count(True) >= detect_count):
                    self.limit_30_status = 1  
                    self.limit = 30

                elif cls == "limit_50" and (len(self.limit_50) == 5) and (self.limit_50.count(True) >= detect_count):
                    self.limit_50_status = 1 
                    self.limit = 50

                elif cls == "limit_100" and (len(self.limit_100) == 5) and (self.limit_100.count(True) >= detect_count):
                    self.limit_100_status = 1
                    self.limit_100_status_prev = 1
                    self.limit = 100

                elif cls == "kidzone" and (len(self.kidzone) == 5) and (self.kidzone.count(True) >= detect_count):
                    self.kidzone_status = 1  
                    self.kidzone_prev = 1

                elif cls == "section_start" and (len(self.section_start) == 5) and (self.section_start.count(True) >= detect_count):
                    self.section_start_status = 1  

                elif cls == "section_end" and (len(self.section_end) == 5) and (self.section_end.count(True) >= detect_count):
                    self.section_end_status = 1  

                elif cls == "oneway" and (len(self.oneway) == 5) and (self.oneway.count(True) >= detect_count):
                    self.oneway_status = 1  

                elif cls == "traffic_light_green" and (len(self.traffic_light_green) == 5) and (self.traffic_light_green.count(True) >= detect_count):
                    self.traffic_light_green_status = 1  
                    if self.detect_light_green_time_prev == 0:
                        self.detect_light_green_time = time.time()
                        self.detect_light_green_time_prev = 1

                elif cls == "traffic_light_yellow" and (len(self.traffic_light_yellow) == 5) and (self.traffic_light_yellow.count(True) >= detect_count):
                    self.traffic_light_yellow_status = 1  

                elif cls == "traffic_light_red" and (len(self.traffic_light_red) == 5) and (self.traffic_light_red.count(True) >= detect_count):
                    # if area > 1100:
                    self.traffic_light_red_status = 1
                       
                elif cls == "person" and (len(self.person) == 5) and (self.person.count(True) >= detect_count):
                    if area > 10000:
                        self.person_status = 1

        if (self.kidzone_status == 1) or (self.redzone_status == 1):
           
            # Step 2: Detect red lane markers only
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([160, 100, 100])
            upper_red2 = np.array([180, 255, 255])


            red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            red_mask = cv2.bitwise_or(red_mask1, red_mask2)

            # 노이즈 제거
            kernel = np.ones((30,30), np.uint8)
            red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
            red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)

            # Find and draw contours for lane markers
            contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 4000:  # Ignore small noise
                    self.redzone_status = 1
                    print("YES", "kidzone_status:", self.kidzone_status, "redzone_status:", self.redzone_status)
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Blue bounding box for lanes
                else:
                    self.redzone_status = 0
                    print("No", "kidzone_status:", self.kidzone_status, "redzone_status:", self.redzone_status)
                    continue
 

                    # self.kidzone_status = 0

        
        # 횡단보도에 사람 있을 때 속도가 있으면 -15
        if self.crosswalk_status == 1 and self.person_status == 1 and velocity > 0 and self.human_on_crosswalk_violation_prev == 0:
            self.penalty += human_on_crosswalk_violation   
            self.human_on_crosswalk_violation_prev = 1
            charge_id = 8
            print("human_on_crosswalk_violation")

        # 초록불일 때 3초동안 속도가 10보다 작으면 -15
        if self.traffic_light_green_status == 1 and (time.time()-self.detect_light_green_time > 3) and velocity == 0 and self.traffic_sign_green_violation_prev == 0:
            self.penalty += traffic_sign_green_violation   
            self.traffic_sign_green_violation_prev  = 1
            self.detect_light_green_time_prev = 0
            charge_id = 4
            print("traffic_sign_green_violation")

         # 구간 단속 50 이상이면 -10
        if int(section_speed) > 50: 
            self.penalty += section_speed_violation
            charge_id = 2
            print("section_speed_violation")   

        
        # 3번 연속 감지되지 않았을 때 status를 0으로 바꾸는 로직
        status_mapping = {
            'lane': ('lane_status', 'lane_miss_count'),
            'dotted_lane': ('dotted_lane_status', 'dotted_lane_miss_count'),
            'yellow_lane': ('yellow_lane_status', 'yellow_lane_miss_count'),
            'stop_line': ('stop_line_status', 'stop_line_miss_count'),
            'crosswalk': ('crosswalk_status', 'crosswalk_miss_count'),
            'limit_30': ('limit_30_status', 'limit_30_miss_count'),
            'limit_50': ('limit_50_status', 'limit_50_miss_count'),
            'limit_100': ('limit_100_status', 'limit_100_miss_count'),
            'kidzone': ('kidzone_status', 'kidzone_miss_count'),
            'section_start': ('section_start_status', 'section_start_miss_count'),
            'section_end': ('section_end_status', 'section_end_miss_count'),
            'oneway': ('oneway_status', 'oneway_miss_count'),
            'traffic_light_green': ('traffic_light_green_status', 'traffic_light_green_miss_count'),
            'traffic_light_yellow': ('traffic_light_yellow_status', 'traffic_light_yellow_miss_count'),
            'traffic_light_red': ('traffic_light_red_status', 'traffic_light_red_miss_count'),
            'person': ('person_status', 'person_miss_count')
        }

        # print("self.detected_classes", self.detected_classes)
        for cls, (status_attr, miss_count_attr) in status_mapping.items():
            if cls not in self.detected_classes:
                # 감지되지 않으면 miss 카운터 증가
                miss_count = getattr(self, miss_count_attr)
                miss_count += 1
                setattr(self, miss_count_attr, miss_count)

                # 3번 연속 감지되지 않았을 때 status를 0으로 변경
                if miss_count >= undetected_count:
                    setattr(self, status_attr, 0)
            else:
                # 감지되면 miss 카운터 리셋
                setattr(self, miss_count_attr, 0)

        # 신호등 빨간 불일 때 정지선이 있었다가 없을때 속도가 있으면 -15
        if self.traffic_light_red_status == 1 and self.stop_line_status == 0 and self.stop_line_status_prev == 1 and velocity >= 10 and self.traffic_sign_red_violation_prev == 0:
            self.penalty += traffic_sign_red_violation   
            self.traffic_sign_red_violation_prev = 1
            charge_id = 5
            print("traffic_sign_red_violation")

        # 신호등 빨간 불일 때 정지선이 있었다가 없을때 속도가 0이면 -10
        if self.traffic_light_red_status == 1 and self.stop_line_status == 0 and self.stop_line_status_prev == 1 and velocity < 10 and self.stop_line_violation_prev == 0:
            self.penalty += stop_line_violation   
            self.stop_line_violation_prev = 1
            charge_id = 5
            print("stop_line_violation")

        # 어린이보호구역 표지판이 있다가 없어지고 빨간 영역이 있을때 속도가 30 초과이면 -30
        if self.kidzone_status == 0 and self.kidzone_prev == 1 and self.redzone_status == 1 and velocity > 30 and self.kidzone_speed_violation_30_prev == 0:
            self.penalty += kidzone_speed_violation   
            self.kidzone_speed_violation_30_prev = 1
            charge_id = 1
            print("kidzone_speed_violation")

        # 100 표지판이 보였다가 안보였을 때 속도가 100 이상이면 -20
        if self.limit_100_status == 0 and self.limit_100_status_prev == 1 and velocity > 100 and self.speed_violation_prev == 0:
            self.penalty += speed_violation   
            self.speed_violation_prev = 1
            charge_id = 3
            print("speed_violation")

        self.objects_cnt_prev = self.objects_cnt
        self.objects_list_prev = self.objects_list

        return (charge_id, self.penalty, self.detected_classes, self.is_new_object, self.new_object)