## 1 프로젝트 소개

##  1.1 개요
- Camera 웹캠을 활용한 벌점 시스템을 이용하여 난폭운전감지하는 프로젝트

## 1.2 프로젝트 기간 : 2024. 08. 30 ~ 2024. 09. 25
  
## 1.3 역할 분담
|팀원|	역할 |
|:----------:|:----------:|
| 강지훈 | 모델학습,db설계,gui 설계,logging알고리즘 작성, 라벨링 | 
| 서성혁 | gui 개발,logging 알고리즘 작성, 시나리오 작성, 라벨링 | 
| 김주연 | 시리얼통신, 소켓 통신 구성, 시스템 아키텍쳐 설계, 감점 알고리즘 작성 |   
| 김정현 | 로봇 속도 구현, opencv 색상 검출, 시나리오 작성, opencv 데이터통신 |    
| 김기욱 | 트랙 설계,트랙 제작, 라벨링, 모델 학습 |    

## 1.4 기술 스택
|팀원|	역할 |
|:----------:|:----------:|
| 언어 | ![image](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) | 
| DB | ![image](https://img.shields.io/badge/MySQL-00000F?style=for-the-badge&logo=mysql&logoColor=white),![image](https://img.shields.io/badge/Amazon_AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)| 
| ComputerVision | ![image](https://github.com/user-attachments/assets/71869631-7845-472c-a033-f62ea5783e03) |   
| 김정현 | 로봇 속도 구현, opencv 색상 검출, 시나리오 작성, opencv 데이터통신 |    
| 김기욱 | 트랙 설계,트랙 제작, 라벨링, 모델 학습 |  
## 1.4 구현 기능 및 관련 기술
System Requirements

![image](https://github.com/user-attachments/assets/a0656b87-7abd-45bf-b08f-d8563af95463)

## 1.5 시스템 구성도
![image](https://github.com/user-attachments/assets/3f1c3042-8eff-41d2-87b2-f29da57473e4)

## 1.6 DATA BASE
![image](https://github.com/user-attachments/assets/8953e560-ecbf-4fd0-a911-a5c6c3ff4053)

## 1.7 도로 트랙 도면
![트랙](https://github.com/user-attachments/assets/b98b88d7-b56e-469f-99fd-9dbb435026dd)



## 1.7 GUI 구버전
![image](https://github.com/user-attachments/assets/a0c5b6f5-c8e7-45d0-9604-5001bf06335f)
![image](https://github.com/user-attachments/assets/010d945e-5b8e-47d9-912a-b6a479eabe97)
![image](https://github.com/user-attachments/assets/b9c7c3d3-78ed-4a7e-b50d-ec2b1353b3b6)
![image](https://github.com/user-attachments/assets/ecba9bd2-0d1c-4a7b-8289-8dcd2c700c56)

## 1.8 GUI 신버전
![Screenshot from 2024-09-24 18-13-04](https://github.com/user-attachments/assets/6554c368-3219-4772-bcf2-67263a1b77a7)
![Screenshot from 2024-09-24 18-13-24](https://github.com/user-attachments/assets/8f250aec-accd-4722-8b47-719b043f53f4)
![image](https://github.com/user-attachments/assets/db738b97-7717-46d0-83c8-55ef712b0d87)




## 1.8 프로그램 실행
```
cd dev_ws
```

```
cd deeplearning-repo-1
```

```
python3 main.py 실행
```
## 1.9 실행
![output_20240924_180932](https://github.com/user-attachments/assets/b0e36a43-b6ba-429f-bbad-f12ce942911d)

## 2 minibot 동작 및 딥러닝 학습 도출 결과 확인
바운딩박스 Accuracy 정확도 확인

![StopLine_NG](https://github.com/user-attachments/assets/e473bbc7-001d-4ab2-954a-f463fa1e89eb)<br>
![trafficLigth_Red_NG](https://github.com/user-attachments/assets/07b0898e-1c66-4586-94d7-aaf8d73a50e7)<br>
![tracfficLight_green_NG](https://github.com/user-attachments/assets/0a38ab38-7603-4699-a668-79e10c1e54f7)<br>
![crosswalk_on_Human_OK-min](https://github.com/user-attachments/assets/6e00b5c3-43ec-4d55-9247-a32465798d4b)<br>
![kidzone_30_NG](https://github.com/user-attachments/assets/f94e1cca-c3b3-4f4f-8c1e-45ab9242b9c3)<br>
![log_video1-ezgif com-optimize (1)](https://github.com/user-attachments/assets/9d31c3db-b6a1-4414-b2c5-aad61207e332)






