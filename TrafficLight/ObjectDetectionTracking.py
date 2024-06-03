from ultralytics import YOLO
import cv2
from helper import create_video_writer
import time
from videoPlay import VideoPlayer
from deep_sort_realtime.deepsort_tracker import DeepSort
import threading
import copy

import logging
logging.getLogger("ultralytics").setLevel(logging.ERROR)

CONFIDENCE_THRESHOLD = 0.5 # 임계값
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)

FRAME = 30

video_file = None
PassTime = None
checking = False
checking1 = False

start = 0
max_clock = 0

s = 0

def returnData():
    global start, max_clock

    return start, max_clock

def TrafficLight(frame):
    global start, s
    cv2.rectangle(frame, (15, 15, 70, 180), WHITE, thickness=-1)
    if(start == 0):
        cv2.circle(frame, (50, 50), 25, RED, thickness=-1)
    else:
        cv2.circle(frame, (50, 110), 25, GREEN, thickness=-1)
    cv2.putText(frame, str(start), (40, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
    s = s + 1
    if(s % FRAME == 0):
        if(start > 0):
            start -= 1
        else:
            start = 0

def video_processing():
    global video_file
    global start, s
    while True:
        while True:
            if str(video_file) != "None":
                break

        while str(video_file) != "None":
            video_cap = cv2.VideoCapture(video_file)
            #writer = create_video_writer(video_cap, "output.mp4")
            model = YOLO("best.pt")
            tracker = DeepSort(max_age=50)

            personTraking = {} # 사람들의 위치를 저장할 딕셔너리
            personTrakingTemp = {} # 사람들의 6초 위치
            personTrakingTemp2 = {} # 사람들의 직전 위치

            global PassTime # 주어진 신호등 시간
            global checking # 5초 남았을 때 한번 체킹을 위한 시간
            global checking1

            start = PassTime
            while True:
                ret, frame = video_cap.read()

                if not ret:
                    break

                #frame = cv2.resize(frame, (640, 640))

                detections = model(frame)[0]

                pedestrian = [] # 보행자 (위치, 신뢰도, id)
                crosswalk = [] # 횡단보도

                # 감지된 객체 리스트로 불러옴
                for data in detections.boxes.data.tolist():

                    # data = [xmin, ymin, xmax, ymax, confidence, class_id]

                    confidence = data[4]
                    if float(confidence) < CONFIDENCE_THRESHOLD:
                        continue

                    xmin, ymin, xmax, ymax = int(data[0]), int(data[1]), int(data[2]), int(data[3])

                    crossXmin, crossXmax = xmin, xmax

                    class_id = int(data[5])


                    if (class_id == 1):
                        pedestrian.append([[xmin, ymin, xmax - xmin, ymax - ymin], confidence, class_id])
                        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), GREEN, 2)
                        cv2.rectangle(frame, (xmin, ymin - 20), (xmin + 20, ymin), GREEN, -1)

                    else:
                        crosswalk.append([[xmin, ymin, xmax - xmin, ymax - ymin], confidence, class_id])
                        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), RED, 2)
                        cv2.putText(frame, "crosswalk", (xmin + 5, ymin - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, BLACK, 2)


                # 트래킹 부분
                tracks = tracker.update_tracks(pedestrian, frame=frame)
                for track in tracks:
                    if not track.is_confirmed():
                        continue

                    track_id = track.track_id
                    ltrb = track.to_ltrb()

                    xmin, ymin, xmax, ymax = int(ltrb[0]), int(ltrb[1]), int(ltrb[2]), int(ltrb[3])
                    
                    personTraking[track_id] = (xmax+xmin)/2 # x축을 기준으로 사람의 위치를 확인
                    
                    cv2.putText(frame, str(track_id), (xmin + 5, ymin - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, WHITE, 1)

                # speed, dis, clock
                clock = []

                if (s == (PassTime-5)*FRAME-1):
                    personTrakingTemp2 = copy.deepcopy(personTraking)

                if (start == 5 and not checking):
                    checking = True # 한번만 체크

                    for key in personTraking:
                        if (personTraking.get(key) != None and personTrakingTemp.get(key) != None and personTrakingTemp2.get(key)):
                            print("여기1 : ", personTraking)
                            print("여기2 : ", personTrakingTemp)
                            print("여기3 : ", personTrakingTemp2)
                            print(crossXmin, crossXmax)
                            if (personTraking[key] != personTrakingTemp2[key]):
                                if(personTraking[key] >= crossXmin and personTraking[key] <= crossXmax):
                                    speed = (abs(personTraking[key]-personTrakingTemp[key])/(s-tempStart))
                                    if(speed):
                                        if (personTraking[key]-personTrakingTemp[key] > 0): # 오른쪽
                                            clock.append((crossXmax - personTraking[key])/speed)
                                        elif (personTraking[key]-personTrakingTemp[key] < 0): # 왼쪽
                                            clock.append((personTraking[key] - crossXmin)/speed)
                                        
                    if(clock):
                        global max_clock
                        max_clock = int(max(clock) / FRAME) # 추가된 시간

                        if(max_clock >= 5):
                            if(max_clock >= 15):
                                max_clock = 10
                                start = 15
                            else:
                                start = max_clock
                                max_clock -= 5

                # 차량에게 넘겨줄때 start(신호등 남은시간) / max_clock(추가된 시간)

                if(start == 6 and not checking1):
                    checking1 = True
                    personTrakingTemp = copy.deepcopy(personTraking)
                    tempStart = s

                TrafficLight(frame)

                cv2.imshow("Frame", frame)
                #writer.write(frame)
                if cv2.waitKey(1) == ord("q"):
                    break
            
            video_file = "None"
            video_cap.release()
            #writer.release()
            cv2.destroyAllWindows()

        start = 0
        max_clock = 0
        s = 0
        checking = False
        checking1 = False


def VideoLoad():
    global video_file, PassTime
    while True:
        player = VideoPlayer()
        player.run()
        video_file = player.get_file_path()
        PassTime = player.get_time()
        print("Video file path :", video_file)
        print("신호등 시간 : ", PassTime)
        time.sleep(1)

# def Tracking():
#     threading.Thread(target=VideoLoad).start() # 영상 불러오는 스레드
#     threading.Thread(target=video_processing).start() # 트래킹 하는 스레드

# Tracking()
