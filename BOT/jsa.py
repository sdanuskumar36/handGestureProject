import cv2
import mediapipe as mp
import mqtt
import time
import math

mp_hands=mp.solutions.hands
mp_draw=mp.solutions.drawing_utils
hands=mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75
)

GESTURE_COMMANDS={
    "OK":"forward",
    "INDEX":"reverse",
    "PEACE":"left",
    "ROCK":"right",
    "STOP":"stop"
}

last_gesture=None
stable_count=0
last_sent_command=None
last_send_time=0
REQUIRED_FRAMES=8
SEND_INTERVAL=0.7

def distance(lm1,lm2):
    return math.sqrt((lm1.x-lm2.x)**2+(lm1.y-lm2.y)**2)

def get_fingers(hand):
    lm=hand.landmark
    index=lm[8].y<lm[6].y
    middle=lm[12].y<lm[10].y
    ring=lm[16].y<lm[14].y
    little=lm[20].y<lm[18].y
    return index,middle,ring,little

def recognize_gesture(hand):
    lm=hand.landmark
    index,middle,ring,little=get_fingers(hand)

    thumb_index_distance=distance(lm[4],lm[8])
    palm_size=distance(lm[0],lm[9])

    if palm_size>0:
        ok_ratio=thumb_index_distance/palm_size
    else:
        ok_ratio=999

    if ok_ratio<0.55 and middle and ring and little:
        return "OK"

    if index and middle and ring and little:
        return "STOP"

    if index and middle and not ring and not little:
        return "PEACE"

    if index and not middle and not ring and little:
        return "ROCK"

    if index and not middle and not ring and not little:
        return "INDEX"

    return "UNKNOWN"

def send_command(command):
    global last_sent_command,last_send_time
    current_time=time.time()

    if command=="":
        return

    if command==last_sent_command:
        return

    if current_time-last_send_time<SEND_INTERVAL:
        return

    mqtt.send("robo1",command)

    print("MQTT COMMAND SENT:",command)

    last_sent_command=command
    last_send_time=current_time

cap=cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Cannot open webcam")
    exit()

print("HAND GESTURE ROBOT CONTROL")
print("OK -> FORWARD")
print("INDEX -> REVERSE")
print("PEACE -> LEFT")
print("ROCK -> RIGHT")
print("OPEN PALM -> STOP")
print("Press Q to quit")

while True:
    success,frame=cap.read()

    if not success:
        print("ERROR: Cannot read webcam")
        break

    frame=cv2.flip(frame,1)
    rgb_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    result=hands.process(rgb_frame)

    gesture="NO HAND"
    command=""

    if result.multi_hand_landmarks:
        hand=result.multi_hand_landmarks[0]

        mp_draw.draw_landmarks(
            frame,
            hand,
            mp_hands.HAND_CONNECTIONS
        )

        current_gesture=recognize_gesture(hand)
        gesture=current_gesture

        if current_gesture==last_gesture:
            stable_count+=1
        else:
            last_gesture=current_gesture
            stable_count=1

        if stable_count>=REQUIRED_FRAMES:
            if current_gesture in GESTURE_COMMANDS:
                command=GESTURE_COMMANDS[current_gesture]
                send_command(command)
    else:
        last_gesture=None
        stable_count=0

    cv2.putText(
        frame,
        "Gesture: "+gesture,
        (10,40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0,0,255),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "Command: "+command,
        (10,80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0,255,0),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "Stable: "+str(stable_count),
        (10,120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255,255,0),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "MQTT: Connected",
        (10,160),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255,255,0),
        2,
        cv2.LINE_AA
    )

    cv2.imshow("Hand Gesture Robot Control",frame)

    if cv2.waitKey(1)&0xFF==ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()
mqtt.client.loop_stop()
mqtt.client.disconnect()

print("Program stopped.")q