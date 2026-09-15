import cv2
import mediapipe as mp
import mqtt
import time
import math


# ============================================================
# MEDIAPIPE SETUP
# ============================================================

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75
)


# ============================================================
# GESTURE → ROBOT COMMAND
# ============================================================

GESTURE_COMMANDS = {
    "OK": "forward",
    "INDEX": "reverse",
    "PEACE": "left",
    "ROCK": "right",
    "STOP": "stop"
}


# ============================================================
# STABILITY SETTINGS
# ============================================================

last_gesture = None
stable_count = 0

last_sent_command = None
last_send_time = 0

# Gesture must remain stable for this many frames
REQUIRED_FRAMES = 8

# Minimum time between commands
SEND_INTERVAL = 0.7


# ============================================================
# DISTANCE BETWEEN LANDMARKS
# ============================================================

def distance(lm1, lm2):

    return math.sqrt(
        (lm1.x - lm2.x) ** 2 +
        (lm1.y - lm2.y) ** 2
    )


# ============================================================
# GET FINGER STATUS
# ============================================================

def get_fingers(hand):

    lm = hand.landmark

    # Index finger
    index = lm[8].y < lm[6].y

    # Middle finger
    middle = lm[12].y < lm[10].y

    # Ring finger
    ring = lm[16].y < lm[14].y

    # Little finger
    little = lm[20].y < lm[18].y

    return index, middle, ring, little


# ============================================================
# GESTURE RECOGNITION
# ============================================================

def recognize_gesture(hand):

    lm = hand.landmark

    index, middle, ring, little = get_fingers(hand)


    # ========================================================
    # 1. OK SIGN 👌
    #
    # Thumb tip + index tip close together.
    # Middle + ring + little extended.
    # ========================================================

    thumb_index_distance = distance(
        lm[4],
        lm[8]
    )

    palm_size = distance(
        lm[0],
        lm[9]
    )

    if palm_size > 0:

        ok_ratio = (
            thumb_index_distance /
            palm_size
        )

    else:

        ok_ratio = 999


    if (
        ok_ratio < 0.55
        and
        middle
        and
        ring
        and
        little
    ):

        return "OK"


    # ========================================================
    # 2. STOP ✋
    #
    # All four fingers extended.
    # ========================================================

    if (
        index
        and
        middle
        and
        ring
        and
        little
    ):

        return "STOP"


    # ========================================================
    # 3. PEACE ✌️
    #
    # Index + middle extended.
    # Ring + little closed.
    # ========================================================

    if (
        index
        and
        middle
        and
        not ring
        and
        not little
    ):

        return "PEACE"


    # ========================================================
    # 4. ROCK 🤘
    #
    # Index + little extended.
    # Middle + ring closed.
    # ========================================================

    if (
        index
        and
        not middle
        and
        not ring
        and
        little
    ):

        return "ROCK"


    # ========================================================
    # 5. INDEX ☝️ - REVERSE
    #
    # Only index finger extended.
    # ========================================================

    if (
        index
        and
        not middle
        and
        not ring
        and
        not little
    ):

        return "INDEX"


    # ========================================================
    # UNKNOWN
    # ========================================================

    return "UNKNOWN"


# ============================================================
# SEND MQTT COMMAND
# ============================================================

def send_command(command):

    global last_sent_command
    global last_send_time

    current_time = time.time()


    # --------------------------------------------------------
    # Don't send empty command
    # --------------------------------------------------------

    if command == "":

        return


    # --------------------------------------------------------
    # Don't repeatedly send same command
    # --------------------------------------------------------

    if command == last_sent_command:

        return


    # --------------------------------------------------------
    # Minimum delay between commands
    # --------------------------------------------------------

    if (
        current_time - last_send_time
        <
        SEND_INTERVAL
    ):

        return


    # --------------------------------------------------------
    # Send JSON through mqtt.py
    # --------------------------------------------------------

    mqtt.send(
        "robo1",
        command
    )


    print()
    print("================================")
    print("MQTT COMMAND SENT:", command)
    print("================================")


    last_sent_command = command
    last_send_time = current_time


# ============================================================
# START CAMERA
# ============================================================

cap = cv2.VideoCapture(0)


if not cap.isOpened():

    print("ERROR: Cannot open webcam")

    exit()


print()
print("==========================================")
print("       HAND GESTURE ROBOT CONTROL")
print("==========================================")
print()
print("GESTURE CONTROL:")
print()
print("👌  OK            → FORWARD")
print("☝️  INDEX         → REVERSE")
print("✌️  PEACE         → LEFT")
print("🤘  ROCK          → RIGHT")
print("✋  OPEN PALM     → STOP")
print()
print("Press Q to quit")
print()


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    success, frame = cap.read()


    if not success:

        print("ERROR: Cannot read webcam")

        break


    # --------------------------------------------------------
    # Mirror webcam
    # --------------------------------------------------------

    frame = cv2.flip(
        frame,
        1
    )


    # --------------------------------------------------------
    # Convert BGR → RGB
    # --------------------------------------------------------

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    # --------------------------------------------------------
    # MediaPipe
    # --------------------------------------------------------

    result = hands.process(
        rgb_frame
    )


    gesture = "NO HAND"
    command = ""


    # ========================================================
    # HAND DETECTED
    # ========================================================

    if result.multi_hand_landmarks:

        hand = result.multi_hand_landmarks[0]


        # ----------------------------------------------------
        # Draw landmarks
        # ----------------------------------------------------

        mp_draw.draw_landmarks(
            frame,
            hand,
            mp_hands.HAND_CONNECTIONS
        )


        # ----------------------------------------------------
        # Recognize gesture
        # ----------------------------------------------------

        current_gesture = recognize_gesture(
            hand
        )

        gesture = current_gesture


        # ====================================================
        # STABILITY CHECK
        # ====================================================

        if (
            current_gesture ==
            last_gesture
        ):

            stable_count += 1

        else:

            last_gesture = current_gesture

            stable_count = 1


        # ====================================================
        # ACCEPT STABLE GESTURE
        # ====================================================

        if stable_count >= REQUIRED_FRAMES:

            if (
                current_gesture
                in GESTURE_COMMANDS
            ):

                command = GESTURE_COMMANDS[
                    current_gesture
                ]


                send_command(
                    command
                )


    else:

        last_gesture = None

        stable_count = 0


    # ========================================================
    # DISPLAY GESTURE
    # ========================================================

    cv2.putText(
        frame,
        "Gesture: " + gesture,
        (10, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 255),
        2,
        cv2.LINE_AA
    )


    # ========================================================
    # DISPLAY COMMAND
    # ========================================================

    cv2.putText(
        frame,
        "Command: " + command,
        (10, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2,
        cv2.LINE_AA
    )


    # ========================================================
    # DISPLAY STABILITY
    # ========================================================

    cv2.putText(
        frame,
        "Stable: " + str(stable_count),
        (10, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 0),
        2,
        cv2.LINE_AA
    )


    # ========================================================
    # DISPLAY MQTT STATUS
    # ========================================================

    cv2.putText(
        frame,
        "MQTT: Connected",
        (10, 160),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 0),
        2,
        cv2.LINE_AA
    )


    # ========================================================
    # SHOW CAMERA
    # ========================================================

    cv2.imshow(
        "Hand Gesture Robot Control",
        frame
    )


    # ========================================================
    # QUIT
    # ========================================================

    if (
        cv2.waitKey(1) & 0xFF
        ==
        ord("q")
    ):

        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()

hands.close()

mqtt.client.loop_stop()

mqtt.client.disconnect()

print()
print("Program stopped.")