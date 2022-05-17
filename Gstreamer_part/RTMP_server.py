import cv2
import argparse
import time
import multiprocessing as mp
import mediapipe


mp_drawing = mediapipe.solutions.drawing_utils
mp_drawing_styles = mediapipe.solutions.drawing_styles
# hand pose tracking
mp_hands = mediapipe.solutions.hands
# object detection
mp_object_detection = mediapipe.solutions.object_detection
# Pose estimation
mp_pose = mediapipe.solutions.pose


def gstreamer_camera(queue):
    # Use the provided pipeline to construct the video capture in opencv
    pipeline = (
        "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), "
            "width=(int)1920, height=(int)1080, "
            "format=(string)NV12, framerate=(fraction)30/1 ! "
        "queue ! "
        "nvvidconv flip-method=2 ! "
            "video/x-raw, "
            "width=(int)1920, height=(int)1080, "
            "format=(string)BGRx, framerate=(fraction)30/1 ! "
        "videoconvert ! "
            "video/x-raw, format=(string)BGR ! "
        "appsink"
    )
    # Complete the function body
    print('gstreamer_camera start')
    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
    while True:
        _, frame = cap.read()
        queue.put(frame)
        #print('Add frame', '   ', queue.qsize())
    cap.release()
    
def gstreamer_rtmpstream(queue):
    # Use the provided pipeline to construct the video writer in opencv
    pipeline = (
        "appsrc ! "
            "video/x-raw, format=(string)BGR ! "
        "queue ! "
        "videoconvert ! "
            "video/x-raw, format=RGBA ! "
        "nvvidconv ! "
        "nvv4l2h264enc bitrate=8000000 ! "
        "h264parse ! "
        "flvmux ! "
        'rtmpsink location="rtmp://localhost/rtmp/live live=1"'
    )
    # Complete the function body
    # You can apply some simple computer vision algorithm here
    print('in gstreamer_rtmpstream')
    videoWrite = cv2.VideoWriter(pipeline, cv2.CAP_GSTREAMER, 0, 30.0, (1920, 1080))
    while True:
        new_frame = queue.get()
        if new_frame is None:
            break
        
        with open('../gRPC_part/Alg.txt', 'r') as f:
            AlgNo = int(f.read())
        
        # Hand pose tracking
        if AlgNo == 1:
            with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
                result = hands.process(new_frame)
                if result.multi_hand_landmarks:
                    for hand_landmarks in result.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                            new_frame,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            mp_drawing_styles.get_default_hand_landmarks_style(),
                            mp_drawing_styles.get_default_hand_connections_style())
            videoWrite.write(new_frame[::-1, :, :])
            print('Write frame. Hand pose Tracking')
        # Object Detection
        elif AlgNo == 2:
            with mp_object_detection.ObjectDetection(min_detection_confidence=0.1) as object_detection:
                result = object_detection.process(new_frame)
                if result.detections:
                    for detection in result.detections:
                        mp_drawing.draw_detection(new_frame, detection)
            videoWrite.write(new_frame[::-1, :, :])
            print('Write frame. Object Detection')
        # Pose estimation
        elif AlgNo == 3:
            with mp_pose.Pose(min_tracking_confidence=0.1, min_detection_confidence=0.1, model_complexity=0) as pose:
                result = pose.process(new_frame)
                if result.pose_landmarks:
                    mp_drawing.draw_landmarks(
                        new_frame,
                        result.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())    
            videoWrite.write(new_frame[::-1, :, :])
            print('Write frame. Pose estimation')


# Complelte the code
if __name__ == '__main__':
    queue = mp.Queue(maxsize=1)
    
    p = mp.Process(target=gstreamer_camera, args=(queue, ))
    c = mp.Process(target=gstreamer_rtmpstream, args=(queue, ))
    p.start()
    c.start()
    try:
        p.join()
        c.join()
    except:
        p.terminate()
        c.terminate()
    

