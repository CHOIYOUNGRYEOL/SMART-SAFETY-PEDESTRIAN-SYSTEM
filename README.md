# SMART-SAFETY-PEDESTRIAN-SYSTEM

## detect_person.py 
YOLOv5 내 실행파일임.
사람 인식했을 때 통신함, 불필요한 동작 제거, 소켓 클라이언트 코드 추가, 객체 인식 이미지 저장 추가

## detect_car.py 
YOLOv5 내 실행파일임. 
차량 인식했을 때 통신함, 불필요한 동작 제거, 소켓 클라이언트 코드 추가, 객체 인식 이미지 저장 추가

## server_last.py 
위 yolov5 클라이언트와 통신하는 서버.
정보를 받아서 MYSQL dB에 저장, 사람 있고, 차량 없을 때 모터 동작 명령 전송함.

## motor.py
모터 동작 클라이언트임.
서버로 부터 모터 동작 명령이 오면 신호등 제어, 모터 동작을 수행함.

## flask_laptop.py 
플라스크 웹 서버임. 
라즈베리파이 웹 서버로 접속, MYSQL DB 접속하여 데이터 시각화함.

## flask_rpi.py
라즈베리파이 웹 서버임. 
YOLOv5 인식 화면 플라스크 웹 서버에 띄움.

## templates 
HTML 있는 폴더임. flask_laptop.py와 연동
