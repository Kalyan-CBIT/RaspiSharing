import face_recognition
import os
import cv2
from flask import Flask, json, render_template, Response,jsonify,request
import time

from werkzeug.wrappers import response

app = Flask(__name__)


KNOWN_FACES_DIR = 'known'
UNKNOWN_FACES_DIR = 'unknown'
TOLERANCE = 0.5
FRAME_THICKNESS = 2
FONT_THICKNESS = 1
MODEL = 'cnn'  # default: 'hog', other one can be 'cnn' - CUDA accelerated (if available) deep-learning pretrained model
res = ''

def name_to_color(name):
    color = [(ord(c.lower())-97)*8 for c in name[:3]]
    return color


print('Loading known faces...')
known_faces = []
known_names = []

for name in os.listdir(KNOWN_FACES_DIR):

    for filename in os.listdir(f'{KNOWN_FACES_DIR}/{name}'):
        image = face_recognition.load_image_file(f'{KNOWN_FACES_DIR}/{name}/{filename}')
        # Always returns a list of found faces, for this purpose we take first face only (assuming one face per image as you can't be twice on one image)
        encoding = face_recognition.face_encodings(image)[0]
        # Append encodings and name
        known_faces.append(encoding)
        known_names.append(name)

print('Processing unknown faces...')

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/interrupt',methods=['GET','POST'])
def getDataFromApp():
    global res
    if request.method == 'POST':
        rdata = request.data
        rdata = json.loads(rdata.decode('utf-8'))
        print(rdata)
    return ' '


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def gen():
    frameUnknownCount,maxFrameUnkonwn = 0,5
    """Video streaming generator function."""
    cap = cv2.VideoCapture(0)
    #cap = cv2.VideoCapture('768x576.avi')
    while(cap.isOpened()):
      # Capture frame-by-frame
        cap.set(cv2.CAP_PROP_POS_FRAMES,0)
        ret, img = cap.read()
        if ret == True:
            width,height = int(img.shape[1]*0.5),int(img.shape[0]*0.5)
            img = cv2.resize(img, (width,height),None, fx=1, fy=1) 
            locations = face_recognition.face_locations(img)
            encodings = face_recognition.face_encodings(img, locations)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            for face_encoding, face_location in zip(encodings, locations):
                results = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)
                match = None
                if True in results:  # If at least one is true, get a name of first of found labels
                    match = known_names[results.index(True)]
                    print(f' - {match} from {results}')

                    # Each location contains positions in order: top, right, bottom, left
                    top_left = (face_location[3], face_location[0])
                    bottom_right = (face_location[1], face_location[2])

                    # Get color by name using our fancy function
                    color = name_to_color(match)

                    # # Paint frame
                    cv2.rectangle(img, top_left, bottom_right, color, FRAME_THICKNESS)

                    # # Now we need smaller, filled grame below for a name
                    # # This time we use bottom in both corners - to start from bottom and move 50 pixels down
                    top_left = (face_location[3], face_location[2])
                    bottom_right = (face_location[1], face_location[2] + 22)

                    # Paint frame
                    cv2.rectangle(img, top_left, bottom_right, color, cv2.FILLED)

                    # Wite a name
                    cv2.putText(img, match, (face_location[3] + 10, face_location[2] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), FONT_THICKNESS)
                else:
                    frameUnknownCount+=1
                    if frameUnknownCount > maxFrameUnkonwn:
                        print("Theif entered")
                        top_left = (face_location[3], face_location[0])
                        bottom_right = (face_location[1], face_location[2])
                        cv2.rectangle(img, top_left, bottom_right, color, FRAME_THICKNESS)
                        top_left = (face_location[3], face_location[2])
                        bottom_right = (face_location[1], face_location[2] + 22)
                        cv2.rectangle(img, top_left, bottom_right, (255,0,0), cv2.FILLED)
                        cv2.putText(img, "Thief", (face_location[3] + 10, face_location[2] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), FONT_THICKNESS)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            #cv2.imshow('Webcam',img)
            cv2.waitKey(2)
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else: 
            break
        

if __name__ == '__main__':
   app.run(host="192.168.0.161",port=5000,debug=True)