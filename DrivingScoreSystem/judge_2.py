from collections import deque

class Judge:
    def __init__(self):
        self.charge = ""
        self.penalty = 0

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

        # TODO: 순서 고치기
        self.detected = [self.lane, self.dotted_lane, self.yellow_lane, self.stop_line, self.crosswalk, self.limit_30, self.limit_50, 
                         self.limit_100, self.kidzone, self.section_start, self.section_end, self.oneway, 
                         self.traffic_light_green, self.traffic_light_yellow, self.traffic_light_red, self.person]

    def verdict(self, detects: dict[str: tuple[int, int, int, int]], cls_set: set[int]) -> tuple[str, int]:
        # TODO: set 잘 작동하는지 확인
        for idx in range(len(self.detected)):
            if idx in cls_set:
                self.detected[idx].append(True)
            else:
                self.detected[idx].append(False)

        for detect in detects:
            cls, bb_coordinates = detect.items()
            x1, y1, x2, y2 = bb_coordinates
            width = x2 - x1
            height = y2 - y1
            area = width * height
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            if cls == "lane":
                pass

            elif cls == "dotted_lane":
                pass

            elif cls == "yellow_lane":
                pass

            elif cls == "stop_line":
                pass

            elif cls == "crosswalk":
                pass

            elif cls == "limit_30":
                pass

            elif cls == "limit_50":
                pass

            elif cls == "limit_100":
                pass

            elif cls == "kidzone":
                pass

            elif cls == "section_start":
                pass

            elif cls == "section_end":
                pass

            elif cls == "oneway":
                pass

            elif cls == "traffic_light_green":
                pass

            elif cls == "traffic_light_yellow":
                pass

            elif cls == "traffic_light_red":
                pass

            elif cls == "person":
                pass

        return (self.charge, self.penalty)
    