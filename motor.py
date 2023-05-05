import socket
import json
import pigpio
import time
import threading

pi = pigpio.pi()

servo_pin = 18  # 12
min_pulse = 900  # 30 degree
max_pulse = 1950  # 135 degree
red_pin = 22  # 15
yellow_pin = 27  # 13
green_pin = 23  # 16
# ground_motor_pin = 6  # 6
# ground_led_pin = 14   # 14


pi.set_mode(servo_pin, pigpio.OUTPUT)
pi.set_servo_pulsewidth(servo_pin, min_pulse)
pi.set_PWM_dutycycle(red_pin, 0)
pi.set_PWM_dutycycle(yellow_pin, 0)
pi.set_PWM_dutycycle(green_pin, 255)
time.sleep(5)


def motor_on():
    time.sleep(5)
    pi.set_PWM_dutycycle(red_pin, 0)
    pi.set_PWM_dutycycle(yellow_pin, 255)
    pi.set_PWM_dutycycle(green_pin, 0)
    time.sleep(5)

    pi.set_PWM_dutycycle(red_pin, 255)
    pi.set_PWM_dutycycle(yellow_pin, 0)
    pi.set_PWM_dutycycle(green_pin, 0)

    pi.set_servo_pulsewidth(servo_pin, max_pulse)
    time.sleep(10)

    pi.set_PWM_dutycycle(red_pin, 0)
    pi.set_PWM_dutycycle(yellow_pin, 0)
    pi.set_PWM_dutycycle(green_pin, 255)
    pi.set_servo_pulsewidth(servo_pin, min_pulse)
    time.sleep(3)


def Recv(client_sock):
    json_object = {"id": 5, "label": 0, "timee": 0}
    send_data = json.dumps(json_object)
    client_sock.send(send_data.encode())
    while (True):
        try:
            data = client_sock.recv(1024)
            json_data = json.loads(data.decode())

            print('Received from' + ':', json_data)

            if (json_data.get("motor") == 1):
                print('motor operate')
                thread1 = threading.Thread(target=motor_on)
                thread1.start()

        except ValueError as e:
            continue


client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
svrIP = "192.168.45.28"
client_sock.connect((svrIP, 7999))
print('Connected to' + svrIP)
thread1 = threading.Thread(target=Recv, args=(client_sock,))
thread1.start()
