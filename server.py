import socket
import json
import threading
import queue
import io
import base64
from imageio import imread
import mysql.connector
import datetime
import pytz
import time
from playsound import playsound

# import p
# import io
import cv2
# from imageio import imread
# import matplotlib.pyplot as plt
# from PIL import Image
# from io import BytesIO

connected_clients = []

# MySQL 데이터베이스 연결 정보
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'dudfuf123',
    'database': 'db_hknu'
}

# 공유 변수
count = 0
timezone = 'Asia/Seoul'
tz = pytz.timezone(timezone)
now = datetime.datetime.now(tz)
past_minute = int(now.strftime('%S'))
past_minute_update = int(now.strftime('%S'))
data_id = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
# 처리할 작업을 담는 큐
task_queue = queue.Queue()

def sound_output():
    playsound(r"C:\playsound\hi.mp3")  # 차단봉을 열겠습니다
    time.sleep(5)
    playsound(r"C:\playsound\hi2.mp3")  # 차단봉이 곧 닫힙니다.
    time.sleep(2)
    playsound(r"C:\playsound\hi3.mp3")  # 차단봉을 닫겠습니다.

# 데이터베이스 연결 함수
def connect_to_db():
    return mysql.connector.connect(**db_config)

#데이터베이스에 데이터 삽입 함수
def insert_data_to_db(json_data,json_data_id):
    try:
        now = datetime.datetime.now(tz)
        now_time = now.strftime('%H:%M:%S')
        conn = connect_to_db() # db에연결
        cursor = conn.cursor()
        if (json_data_id==1 or json_data_id==3): # 사람 인식 정보 db_person 테이블에 삽입
            sql = "INSERT INTO db_person (id, label, timee) VALUES (%s, %s, %s)"
            cursor.execute(sql, (json_data['id'], json_data['label'], now_time))
            conn.commit()
        elif (json_data_id==2 or json_data_id==4): # 차량 인식 정보 db_car 테이블에 삽입
            sql = "INSERT INTO db_car (id, label, timee) VALUES (%s, %s, %s)"
            cursor.execute(sql, (json_data['id'], json_data['label'], now_time))
            conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        pass


def handle_client_data(data, client_socket):
    global past_minute, count, past_minute_update, data_id
    try:
        # 클라이언트로부터 데이터 받기
        json_data = json.loads(data.decode())
        json_data_idd = json_data.get("id")
        insert_data_to_db(json_data, json_data_idd)  # mysql db에 사람, 차량 인식 정보 삽입 함수 호출
        print(json_data)

        # 각각의 클라이언트에서 받은 데이터를 딕셔너리에 저장
        if json_data_idd in data_id:
            data_id[json_data_idd] = json_data_idd
        print(data_id[1], data_id[2], data_id[3], data_id[4], data_id[5], data_id[6])

        timezone = 'Asia/Seoul'
        tz = pytz.timezone(timezone)
        now = datetime.datetime.now(tz)
        now_minute = int(now.strftime('%S'))
        time_diff = now_minute - past_minute  # 시간 차 계산
        time_diff_update = now_minute - past_minute_update  # 시간 차 계산
        data_motor = {"motor": 1}
        data_send = json.dumps(data_motor)  # 모터 명령어 생성

        if time_diff < 0:  # 음수면 양수로 변환
            time_diff += 60
        if time_diff_update < 0:  # 음수면 양수로 변환
            time_diff_update += 60
            print(time_diff)
        print(time_diff_update)


        if count == 0 or time_diff > 20:  # 첫 번째 동작 or 전 동작 후 20초
            if (data_id[1] == 1 or data_id[3] == 3) and ((data_id[2] != 2) and (data_id[4] != 4)):  # 사람이 있고 차량이 없는가
                print('Motor activated')
                # t1 = threading.Thread(target=sound_output)
                # t1.start()  # 음성출력 스레드 실행
                for client_socket in connected_clients:
                    client_socket.send(data_send.encode())  # 5,6번 클라이언트에게 모터 동작 명령
                    print("send complete")
                    count += 1  # 동작 횟수 증가
                    past_minute = int(now.strftime('%S'))  # 동작 후 시간 업데이트
            else:
                print('Motor not activated')
            past_minute_update = int(now.strftime('%S'))  # 알고리즘 수행 후 시간 업데이트

        if time_diff_update > 2:  # 2초 마다 데이터 갱신
            data_id[2] = 0
            data_id[4] = 0
            print('데이터를 초기화 했습니다')
            print('------------------------------------')

    except Exception as e:
        pass

# 클라이언트 연결 처리 함수
def handle_client_connection(client_socket):
    while True:
        # 클라이언트로부터 데이터 받기
        try:
            data = client_socket.recv(1024).decode()
            print(data)
            print(' ')
            json_data = json.loads(data)

            json_data_id = json_data.get("id")
            if json_data_id == 5 or json_data_id == 6:  # 클라이언트 5,6번만 리스트에 넣기
                connected_clients.append(client_socket)


            if not data:
                break
            # 작업 큐에 클라이언트 데이터 처리 작업 추가
            task_queue.put((handle_client_data, data, client_socket))
        except json.JSONDecodeError as e:
            # print(f"Error decoding JSON data: {e}")
            pass


# 작업 처리 함수
def process_tasks():
    while True:
        # 작업 큐에서 작업 가져오기
        task, data, client_socket = task_queue.get()

        # 작업 실행
        task(data, client_socket)

        # 작업 큐에서 작업 제거
        task_queue.task_done()


def run_server():
    # 서버 소켓 생성
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('192.168.45.3', 9999))
    server_socket.listen()

    # 작업 처리 스레드 생성
    for i in range(10):
        t = threading.Thread(target=process_tasks)
        t.daemon = True
        t.start()

    # 클라이언트 연결 처리
    while True:
        print('Waiting connection from client... ')
        client_socket, address = server_socket.accept()
        print(f'New connection from {address}')

        # 클라이언트 연결 처리 스레드 생성
        t = threading.Thread(target=handle_client_connection, args=(client_socket,))
        t.daemon = True
        t.start()

if __name__ == '__main__':
    run_server()
server_socket.close()