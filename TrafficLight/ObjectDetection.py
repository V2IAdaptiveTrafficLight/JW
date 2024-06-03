from ultralytics import YOLO
import cv2
from helper import create_video_writer
import time

import logging
logging.getLogger("ultralytics").setLevel(logging.ERROR)


CONFIDENCE_THRESHOLD = 0.5
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (0, 0, 255)

video_cap = cv2.VideoCapture("testesetsesadf.mp4")
#writer = create_video_writer(video_cap, "output.mp4")
model = YOLO("best.pt", verbose=False)

while True:
    ret, frame = video_cap.read()

    if not ret:
        break

    detections = model(frame)[0]

    for data in detections.boxes.data.tolist():

        confidence = data[4]

        if float(confidence) < CONFIDENCE_THRESHOLD:
            continue

        xmin, ymin, xmax, ymax = int(data[0]), int(data[1]), int(data[2]), int(data[3])

        class_id = int(data[5])

        if (class_id == 1):
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), GREEN, 2)

        else:
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), RED, 2)
            cv2.putText(frame, "crosswalk", (xmin + 5, ymin - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 2)

    cv2.imshow("Frame", frame)
    #writer.write(frame)
    if cv2.waitKey(1) == ord("q"):
        break

    time.sleep(0.01)

video_cap.release()
#writer.release()
cv2.destroyAllWindows()
