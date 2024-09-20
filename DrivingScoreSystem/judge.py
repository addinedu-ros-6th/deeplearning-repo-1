from collections import deque

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

        self.stop_line_status_prev = 0
        self.kidzone_prev = 0

        #벌점 사항
        self.stop_line_prev = 0
        self.crosswalk_prev = 0
        self.speed_limit_30_prev = 0
        self.speed_limit_50_prev = 0
        self.speed_limit_100_prev = 0
        self.green_signal_prev = 0
        self.limit_100_status_prev = 0

        # self.velocity = 30

        # 새로운 객체 감지
        self.objects_list = set()
        self.objects_list_prev = set()
        self.objects_cnt = len(self.objects_list)
        self.objects_cnt_prev = self.objects_cnt
        self.is_new_object = False
        self.new_object = set()
       
        self.detected = [self.lane, self.dotted_lane, self.yellow_lane, self.stop_line, self.crosswalk, self.limit_30, self.limit_50, 
                         self.limit_100, self.kidzone, self.section_start, self.section_end, self.oneway, 
                         self.traffic_light_green, self.traffic_light_yellow, self.traffic_light_red, self.person]
        
        self.detected_classes = set()

        
    def verdict(self, detects: dict[str: tuple[int, int, int, int]], cls_set: set[int], velocity) -> tuple[str, int]:

        charge_id = 0

        self.penalty = 0
        stop_line_over = 10
        crosswalk_over = 15
        speed_limit_30_over = 30
        speed_limit_50_over = 10
        speed_limit_100_over = 20
        green_signal_over = 15

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
                self.objects_list_prev = self.objects_list
                self.objects_list.add(cls)

                self.objects_cnt_prev = self.objects_cnt
                self.objects_cnt = len(self.objects_list)

                if (self.objects_cnt > self.objects_cnt_prev) and (self.objects_list != self.objects_list_prev):
                    self.is_new_object = True
                    self.new_object = self.objects_list - self.objects_list_prev

                # print(f"Detected class: {cls}")
                # print(f"area : {area}")

                if cls == "lane" and (len(self.lane) == 5):
                    self.lane_status = 1
                    
                elif cls == "dotted_lane" and (len(self.dotted_lane) == 5):
                    self.dotted_lane_status = 1

                elif cls == "yellow_lane" and (len(self.yellow_lane) == 5):
                    self.yellow_lane_status = 1

                elif cls == "stop_line" and (len(self.stop_line) == 5):
                    if area > 13000:    
                        self.stop_line_status = 1
                        self.stop_line_status_prev = 1

                elif cls == "crosswalk" and (len(self.crosswalk) == 5):
                    if area > 55000:
                        self.crosswalk_status = 1

                elif cls == "limit_30" and (len(self.limit_30) == 5):
                    self.limit_30_status = 1  
                    self.limit = 30

                elif cls == "limit_50" and (len(self.limit_50) == 5):
                    self.limit_50_status = 1 
                    self.limit = 50

                elif cls == "limit_100" and (len(self.limit_100) == 5):
                    self.limit_100_status = 1
                    self.limit_100_status_prev = 1
                    self.limit = 100

                elif cls == "kidzone" and (len(self.kidzone) == 5):
                    self.kidzone_status = 1  
                    self.kidzone_prev = 1

                elif cls == "section_start" and (len(self.section_start) == 5):
                    self.section_start_status = 1  

                elif cls == "section_end" and (len(self.section_end) == 5):
                    self.section_end_status = 1  

                elif cls == "oneway" and (len(self.oneway) == 5):
                    self.oneway_status = 1  

                elif cls == "traffic_light_green" and (len(self.traffic_light_green) == 5):
                    self.traffic_light_green_status = 1  

                elif cls == "traffic_light_yellow" and (len(self.traffic_light_yellow) == 5):
                    self.traffic_light_yellow_status = 1  

                elif cls == "traffic_light_red" and (len(self.traffic_light_red) == 5):
                    # if area > 1100:
                    self.traffic_light_red_status = 1
                       
                elif cls == "person" and (len(self.person) == 5):
                    if area > 10000:
                        self.person_status = 1
              
        # 횡단보도에 사람 있을 때 속도가 있으면 -15
        if self.crosswalk_status == 1 and self.person_status == 1 and velocity > 0 and self.crosswalk_prev == 0:
            self.penalty += crosswalk_over   
            self.crosswalk_prev = 1
            charge_id = 8
            print("crosswalk_over")

        # 초록불이고 정지선이 있을 때 속도가 10보다 작으면 -15
        if self.traffic_light_green == 1 and self.stop_line_status == 1 and velocity < 10 and self.green_signal_prev == 0:
            self.penalty += green_signal_over   
            self.green_signal_prev = 1
            charge_id = 4
            print("green_signal_over")

        #  # 구간 단속 50 이상이면 -10
        # if self.section_velocity > 30: 
        #     self.penalty += speed_limit_50_over   

        # 100 표지판이 보였다가 안보였을 때 속도가 100 이상이면 -10
        if self.limit_100_status == 0 and self.limit_100_status_prev == 1 and velocity > 100:
            self.penalty += speed_limit_100_over   
            self.speed_limit_100_prev = 0
            charge_id = 3
            print("speed_limit_100_over")
        
        status_mapping = { 'lane': 'lane_status', 'dotted_lane': 'dotted_lane_status', 'yellow_lane': 'yellow_lane_status', 'stop_line': 'stop_line_status',                             
                            'crosswalk': 'crosswalk_status', 'limit_30': 'limit_30_status', 'limit_50': 'limit_50_status', 'limit_100': 'limit_100_status',                             
                            'kidzone': 'kidzone_status', 'section_start': 'section_start_status', 'section_end': 'section_end_status',                             
                            'oneway': 'oneway_status', 'traffic_light_green': 'traffic_light_green_status', 'traffic_light_yellow': 'traffic_light_yellow_status',                             
                            'traffic_light_red': 'traffic_light_red_status', 'person': 'person_status'}

        # print("self.detected_classes", self.detected_classes)
        for cls in status_mapping:
            if cls not in self.detected_classes:
                setattr(self, status_mapping[cls], 0)

        # 신호등 빨간 불일 때 정지선이 있었다가 없으면 -10
        if self.traffic_light_red_status == 1 and self.stop_line_status == 0 and self.stop_line_status_prev == 1 and self.stop_line_prev == 0:
            self.penalty += stop_line_over   
            self.stop_line_over = 1
            self.stop_line_status_prev = 0
            charge_id = 5
            print("stop_line_over")

        # 어린이보호구역 표지판이 있다가 없어지고 빨간 영역이 있을때 속도가 30 초과이면 -30
        if self.kidzone == 0 and self.kidzone_prev == 1 and self.redzone_status == 1 and velocity > 30 and self.speed_limit_30_prev == 0:
            self.penalty += speed_limit_30_over   
            self.speed_limit_30_prev = 1
            charge_id = 1
            print("speed_limit_30_over")
        else:
            self.speed_limit_30_prev = 0

        return (charge_id, self.penalty, self.detected_classes, self.is_new_object, self.new_object)