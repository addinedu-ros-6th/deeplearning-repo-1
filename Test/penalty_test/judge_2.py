from collections import deque

class Judge:
    def __init__(self):
        self.charge = ""
        

        len = 5
        self.lane = deque(maxlen=len)
        self.dotted_lane = deque(maxlen=len)
        self.yellow_lane = deque(maxlen=len)
        self.stop_line = deque(maxlen=len)
        self.crosswalk = deque(maxlen=len)
        self.limit_30 = deque(maxlen=len)
        self.limit_50 = deque(maxlen=len)
        self.limit_100 = deque(maxlen=len)
        self.kidzone = deque(maxlen=len)
        self.section_start = deque(maxlen=len)
        self.section_end = deque(maxlen=len)
        self.oneway = deque(maxlen=len)
        self.traffic_light_green = deque(maxlen=len)
        self.traffic_light_yellow = deque(maxlen=len)
        self.traffic_light_red = deque(maxlen=len)
        self.person = deque(maxlen=len)

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
        self.redzone = 0

        #벌점 사항
        self.stop_line_over = 0
        self.crosswalk_over = 0
        self.speed_limit_30_over = 0
        self.speed_limit_50_over = 0
        self.speed_limit_100_over = 0

        self.velocity = 30

        self.detected = [self.lane, self.dotted_lane, self.yellow_lane, self.stop_line, self.crosswalk, self.limit_30, self.limit_50, 
                         self.limit_100, self.kidzone, self.section_start, self.section_end, self.oneway, 
                         self.traffic_light_green, self.traffic_light_yellow, self.traffic_light_red, self.person]

    def verdict(self, detects: dict[str: tuple[int, int, int, int]], cls_set: set[int]) -> tuple[str, int]:

        self.penalty = 0

        # 탐지된 객체 업데이트
        for idx in range(len(self.detected)):
            if idx in cls_set:
                self.detected[idx].append(True)
            else:
                self.detected[idx].append(False)

        print(detects)
        
        for detect in detects:
            for cls, bb_coordinates in detect.items():
                x1, y1, x2, y2 = bb_coordinates
                width = x2 - x1
                height = y2 - y1
                area = width * height
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2

                print(f"Detected class: {cls}")
                print(f"area : {area}")

                if cls == "lane" and (False not in self.lane) and (len(self.lane) == 5):
                    self.lane_status = 1
                    
                elif cls == "dotted_lane" and (False not in self.dotted_lane) and (len(self.dotted_lane) == 5):
                    self.dotted_lane_status = 1

                elif cls == "yellow_lane" and (False not in self.yellow_lane) and (len(self.yellow_lane) == 5):
                    self.yellow_lane_status = 1

                elif cls == "stop_line" and (len(self.stop_line) == 5):
                    if area > 13500:
                        self.stop_line_status = 1
                    elif self.stop_line_status == 1 and area < 6000:
                        self.stop_line_status = 0

                elif cls == "crosswalk" and (len(self.crosswalk) == 5):
                    if area > 32000:
                        self.crosswalk_status = 1

                elif cls == "limit_30" and (len(self.limit_30) == 5):
                    self.limit_30_status = 1  

                elif cls == "limit_50" and (len(self.limit_50) == 5):
                    self.limit_50_status = 1 

                elif cls == "limit_100" and (len(self.limit_100) == 5):
                    self.limit_100_status = 1

                elif cls == "kidzone" and (len(self.kidzone) == 5):
                    self.kidzone_status = 1  

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
                    if area > 1100:
                        self.traffic_light_red_status = 1
                       
                elif cls == "person" and (len(self.person) == 5):
                    if area > 1200:
                        self.person_status = 1
        
        # 신호등 빨간 불일 때 정지선 없음 감점 -10
        if self.traffic_light_red_status == 1 and self.stop_line_status == 0 and self.velocity > 10 and self.stop_line_over == 0:
            self.penalty += 10   
            self.stop_line_over = 1
            self.traffic_light_red_status = 0
       

        # 신호등 빨간 불일 때 정지선 없음 감점 -20
        if self.crosswalk_status == 1 and self.person_status == 1 and self.velocity > 10 and self.crosswalk_over == 0:
            self.penalty += 20   
            self.crosswalk_over = 1

        
         # 어린이 보호 구역 30 -15
        if self.kidzone == 1 and self.limit_30 == 1 and self.redzone == 0 and self.velocity > 30 and self.speed_limit_30_over == 0:
            self.penalty += 15   
            self.speed_limit_30_over = 1
        else:
            self.speed_limit_30_over = 0

        
        #  # 구간 단속 50 이상 -5
        # if self.section_velocity > 30: 
        #     self.penalty += 5   

        
          # 구간 단속 100 이상 -25
        if self.limit_100_status == 1 and self.velocity > 100 and self.speed_limit_100_over == 0: 
            self.penalty += 25   
            self.speed_limit_100_over = 1


        # if detects in self.detected
        



        return (self.charge, self.penalty)
