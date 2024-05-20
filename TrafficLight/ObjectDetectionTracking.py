import datetime
from ultralytics import YOLO
import cv2
from helper import create_video_writer
import time
from videoPlay import VideoPlayer
from deep_sort_realtime.deepsort_tracker import DeepSort
import threading

CONFIDENCE_THRESHOLD = 0.5 # 임계값
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)

video_file = None
PassTime = None

start = 0
s = 0
def TrafficLight(frame):
    global start, s
    cv2.circle(frame, (50, 50), 25, (0, 0, 255), thickness=-1)
    cv2.circle(frame, (50, 110), 25, (0, 255, 0), thickness=-1)
    cv2.putText(frame, str(start), (40, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
    s = s + 1
    if(s % 20 == 0):
        start += 1

def video_processing():
    global video_file
    while True:
        while True:
            if str(video_file) != "None":
                break

        while str(video_file) != "None":
            video_cap = cv2.VideoCapture(video_file)
            writer = create_video_writer(video_cap, "output.mp4")
            model = YOLO("bestmediumtest4.pt")
            tracker = DeepSort(max_age=50)

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
                    class_id = int(data[5])

                    if(class_id == 1):
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
                    cv2.putText(frame, str(track_id), (xmin + 5, ymin - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, WHITE, 1)

                TrafficLight(frame)

                cv2.imshow("Frame", frame)
                writer.write(frame)
                if cv2.waitKey(1) == ord("q"):
                    break
            
            video_file = "None"
            video_cap.release()
            writer.release()
            cv2.destroyAllWindows()

        global start, s
        start = 0
        s = 0


def VideoLoad():
    global video_file, PassTime
    while True:
        player = VideoPlayer()
        player.run()
        video_file = player.get_file_path()
        PassTime = player.get_time()
        print("Video file:", video_file)
        print("time : ", PassTime)
        time.sleep(1)

def Tracking():
    # 영상 불러오는 스레드
    threading.Thread(target=VideoLoad).start()

    # 트래킹 하는 스레드
    threading.Thread(target=video_processing).start()

Tracking()
