# from flask import Flask, render_template,redirect
# import mysql.connector
# import matplotlib.pyplot as plt
# from datetime import datetime
# import matplotlib
#
# matplotlib.use('agg')
# app = Flask(__name__)
#
# mydb= mysql.connector.connect(
#     host = 'localhost',
#     user = 'root',
#     password = 'dudfuf123',
#     port= '3306',
#     database = 'db_hknu'
# )
#
# @app.route('/')
# def index():
#     return render_template("index.html")
#
# # @app.route("/redirect/<server>")
# # def redirect_to_server(server):
# #     if server == "server1":
# #         return redirect("http://192.168.45.222:5000")
# #     elif server == 'server2':
# #         return redirect('http://192.168.1.102')
# #     elif server == 'server3':
# #         return redirect('http://192.168.1.103')
# #     elif server == 'server4':
# #         return redirect('http://192.168.45.208:5000')
# #     else:
# #         return 'Invalid server'
# @app.route('/generic')
# def generic():
#     cur = mydb.cursor()
#     cur.execute("SELECT HOUR(timee) as hour, COUNT(*) FROM db_car GROUP BY HOUR(timee)")
#     fetchdata = cur.fetchall()
#     cur.execute("SELECT id, label, timee, COUNT(*) FROM db_car GROUP BY id, label, timee ORDER BY id DESC LIMIT 15")
#     fetchdata2 = cur.fetchall()
#     cur.close()
#     labels = [str(hour) for hour in range(24)]
#     hours = [row[0] for row in fetchdata]
#     counts = [row[1] for row in fetchdata]
#     plt.bar(hours, counts)
#     plt.title('Data by hour')
#     plt.xlabel('Hour')
#     plt.ylabel('Count')
#     plt.xticks(range(24), labels)
#     # Save the plot to a file
#     plt.savefig('static/images/plot1.png')
#     return render_template('generic.html', plot_url='static/images/plot1.png',data=fetchdata2)
#
# @app.route('/elements')
# def elements():
#     cur = mydb.cursor()
#     cur.execute("SELECT HOUR(timee) as hour, COUNT(*) FROM db_person GROUP BY HOUR(timee)")
#     fetchdata = cur.fetchall()
#     cur.execute("SELECT id, label, timee, COUNT(*) FROM db_person GROUP BY id, label, timee ORDER BY id DESC LIMIT 20")
#     fetchdata2 = cur.fetchall()
#     cur.close()
#     labels = [str(hour) for hour in range(24)]
#     hours = [row[0] for row in fetchdata]
#     counts = [row[1] for row in fetchdata]
#     plt.bar(hours, counts)
#     plt.title('Data by hour')
#     plt.xlabel('Hour')
#     plt.ylabel('Count')
#     plt.xticks(range(24), labels)
#     # Save the plot to a file
#     plt.savefig('static/images/plot2.png')
#     return render_template('elements.html', plot_url='static/images/plot2.png', data=fetchdata2)
#
# if __name__ == '__main__':
#     app.run(host='0.0.0.0')
from flask import Flask, render_template, redirect
import mysql.connector
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib
import threading
import socket
import base64
import numpy as np
import cv2
import json
matplotlib.use('agg')
app = Flask(__name__)

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='dudfuf123',
    port='3306',
    database='db_hknu'
)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/generic')
def generic():
    cur = mydb.cursor()
    cur.execute("SELECT HOUR(timee) as hour, COUNT(*) FROM db_car GROUP BY HOUR(timee)")
    fetchdata = cur.fetchall()
    cur.execute("SELECT id, label, timee, COUNT(*) FROM db_car GROUP BY id, label, timee ORDER BY id DESC LIMIT 15")
    fetchdata2 = cur.fetchall()
    cur.close()
    labels = [str(hour) for hour in range(24)]
    hours = [row[0] for row in fetchdata]
    counts = [row[1] for row in fetchdata]
    plt.bar(hours, counts)
    plt.title('Data by hour')
    plt.xlabel('Hour')
    plt.ylabel('Count')
    plt.xticks(range(24), labels)
    # Save the plot to a file
    plt.savefig('static/images/plot1.png')
    return render_template('generic.html', plot_url='static/images/plot1.png', data=fetchdata2)


@app.route('/elements')
def elements():
    cur = mydb.cursor()
    cur.execute("SELECT HOUR(timee) as hour, COUNT(*) FROM db_person GROUP BY HOUR(timee)")
    fetchdata = cur.fetchall()
    cur.execute("SELECT id, label, timee, COUNT(*) FROM db_person GROUP BY id, label, timee ORDER BY id DESC LIMIT 20")
    fetchdata2 = cur.fetchall()
    cur.close()
    labels = [str(hour) for hour in range(24)]
    hours = [row[0] for row in fetchdata]
    counts = [row[1] for row in fetchdata]
    plt.bar(hours, counts)
    plt.title('Data by hour')
    plt.xlabel('Hour')
    plt.ylabel('Count')
    plt.xticks(range(24), labels)
    # Save the plot to a file
    plt.savefig('static/images/plot2.png')
    return render_template('elements.html', plot_url='static/images/plot2.png', data=fetchdata2)


class ImageServer(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        client_socket, address = server_socket.accept()
        print("Connection from", address)
        img_bytes = b''
        while True:
            try:
                # Receive image data from server
                buffer = ''
                while True:
                    data = client_socket.recv(1024).decode()
                    print(data)
                    buffer += data
                    if '}' in buffer:
                        break
                json_data = json.loads(buffer)

                # Get image data from dictionary
                img_base64 = json_data['img']

                # Decode Base64-encoded image data
                img_binary = base64.b64decode(img_base64)

                # Convert binary data to image object
                img_np = np.frombuffer(img_binary, dtype=np.uint8)
                img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

                # Save image to file
                cv2.imwrite(r'C:\Users\USER\yolo_image\img1.jpg', img)
            except json.decoder.JSONDecodeError as e:
                print(f'JSONDecodeError: {e.msg} at line {e.lineno}, column {e.colno}')
            except Exception as e:
                print(f'Error: {str(e)}')



if __name__ == '__main__':
    # Start the Flask application
    image_server = ImageServer('192.168.45.88', 9999)
    image_server.start()
    app.run(host='0.0.0.0')

