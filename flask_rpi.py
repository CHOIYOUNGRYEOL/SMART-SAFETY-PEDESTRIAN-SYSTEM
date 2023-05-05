from flask import Flask, Response, send_file
import cv2
import time
app = Flask(__name__)
@app.route('/')
def index():
    return 'Hello, world!'
def gen():
    while True:
        frame = cv2.imread('runs/detect/img/img1.jpg')
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.3)

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/image')
def image():
    return send_file('runs/detect/img/img1.jpg', mimetype='image/jpg')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
