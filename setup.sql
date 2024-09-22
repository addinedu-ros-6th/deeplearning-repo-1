CREATE TABLE UserData
{
    id int NOT NULL AUTO_INCREMENT PRIMARY KEY, 
    login_id varchar(32), 
    admin bool, 
    car_number char(8), 
    password varchar(32)
}

CREATE TABLE PenaltyData
{
    id int NOT NULL AUTO_INCREMENT PRIMARY KEY, 
    penalty_type varchar(32), 
    penalty_score int
}

CREATE TABLE ObjectData
{
    id int NOT NULL AUTO_INCREMENT PRIMARY KEY, 
    objects varchar(24), 
}

CREATE TABLE PenaltyLog
{
    time datetime NOT NULL, 
    user_id int, 
    penalty_id int, 
    speed int, 
    image_name varchar(16), 
    image_path = varchar(40), 
    json_data json, 
    score int, 
    FOREIGN KEY (user_id) REFERENCES UserData(id), 
    FOREIGN KEY (penalty_id) REFERENCES PenaltyData(id)
}

CREATE TABLE ObjectLog
{
    time datetime NOT NULL, 
    user_id int, 
    object_id int, 
    image_path varchar(40), 
    json_data json, 
    image_name varchar(16), 
    FOREIGN KEY (user_id) REFERENCES UserData(id), 
    FOREIGN KEY (object_id) REFERENCES ObjectData(id)
}

INSERT INTO UserData (id, login_id, admin, car_number, password) VALUES 
(1, 'admin1', true, '123가4567', 1234);

INSERT INTO PenaltyData (id, penalty_type, penalty_score) VALUES 
(1, kidzone_speed_violation, 30), 
(2, section_speed_violation, 10), 
(3, speed_violation, 20), 
(4, traffic_sign_green_violation, 15), 
(5, traffic_sign_red_violation, 15), 
(6, stop_line_violation, 10), 
(7, lane_violation, 5), 
(8, human_on_crosswalk_violation, 15);

INSERT INTO ObjectData (id, objects) VALUES 
(1, lane), 
(2, yellow_lane), 
(3, stop_line), 
(4, kidzone), 
(5, section_start), 
(6, section_end), 
(7, limit_30), 
(8, limit_50), 
(9, limit_100), 
(10, oneway), 
(11, dotted_lane), 
(12, traffic_light_red), 
(13, traffic_light_yellow), 
(14, traffic_light_green), 
(15, person);