import cv2
import mediapipe as mp
import time
import pyautogui
from enum import Enum

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

#dead zones
deadzone_x = 60
deadzone_y = 60

#frames
frame_count = 0
results = None

#hands
palm_ids = [0, 5, 9, 13, 17]

#finger tips
tips = [8, 12, 16, 20]

#keys
w_pressed = False
s_pressed = False
a_pressed = False
d_pressed = False
shift_pressed = False

j_pressed = False
k_pressed = False

#movement states
class HorizontalState(Enum):
    CENTER = 0
    LEFT = 1
    RIGHT = 2
    
class VerticalState(Enum):
    CENTER = 0
    UP = 1
    DOWN = 2
    
horizontal = HorizontalState.CENTER
vertical = VerticalState.CENTER

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 60) #mine is capped at around 40 but you might have a better webcam


def get_finger_states(hand):
    l = hand.landmark
    
    #compare tip pos to joint 
    return (
        l[8].y < l[6].y,
        l[12].y < l[10].y,
        l[16].y < l[14].y,
        l[20].y < l[18].y,
    )
cv2.namedWindow("Webcam Controller", cv2.WINDOW_NORMAL)

prev_time = time.time()


while True:
    success, frame = cap.read()

    if not success:
        break
    
    
    #fps stuff comment this out later its only for testing cam specs
    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time

    frame = cv2.flip(frame, 1)
    
    h, w, _ = frame.shape
    
    cv2.putText(
            frame,
            f"FPS: {int(fps)}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )
    
    action = "k ACTIVE" if k_pressed else "k UNACTIVE"

    cv2.putText(
        frame,
        action,
        (int(w * 0.57), int(h * 0.7)),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 0),
        2
    )
    action = "J ACTIVE" if j_pressed else "J UNACTIVE"

    cv2.putText(
        frame,
        action,
        (int(w * 0.57), int(h * 0.5)),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 0),
        2
    )
    
    action = "shift ACTIVE" if shift_pressed else "shift UNACTIVE"
    
    cv2.putText(
        frame,
        action,
        (int(w * 0.57), int(h * 0.3)),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 0),
        2
    )

    tracking_frame = cv2.resize(frame, (160, 120))
    rgb = cv2.cvtColor(tracking_frame, cv2.COLOR_BGR2RGB)

    frame_count += 1
    if frame_count % 2 == 0 or frame_count == 1:
        results = hands.process(rgb)
    
    control_center_x = w // 4
    control_center_y = h // 2

    box_width = w // 2
    box_height = h - 20
    
    left = control_center_x - box_width // 2
    right = control_center_x + box_width // 2

    top = control_center_y - box_height // 2
    bottom = control_center_y + box_height // 2

    cv2.rectangle(
        frame,
        (left, top),
        (right, bottom),
        (0, 255, 255),
        2
    )
    
    cv2.line(
        frame,
        (left + box_width // 3, top),
        (left + box_width // 3, bottom),
        (100, 100, 100),
        2
    )

    cv2.line(
        frame,
        (left + 2 * box_width // 3, top),
        (left + 2 * box_width // 3, bottom),
        (100, 100, 100),
        2
    )

    cv2.line(
        frame,
        (left, top + box_height // 3),
        (right, top + box_height // 3),
        (100, 100, 100),
        2
    )

    cv2.line(
        frame,
        (left, top + 2 * box_height // 3),
        (right, top + 2 * box_height // 3),
        (100, 100, 100),
        2
    )
    
    
    #HANDS STUFF 
    if results.multi_hand_landmarks and results.multi_handedness:

        for hand_landmarks, handedness in zip(
            results.multi_hand_landmarks,
            results.multi_handedness
        ):
            label = handedness.classification[0].label
            states = get_finger_states(hand_landmarks)

            #lowkey not needed
            # mp_draw.draw_landmarks(
            #     frame,
            #     hand_landmarks,
            #     mp_hands.HAND_CONNECTIONS
            # )
            
            

            palm_x = 0
            palm_y = 0

            for pid in palm_ids:
                palm_x += hand_landmarks.landmark[pid].x
                palm_y += hand_landmarks.landmark[pid].y

            palm_x /= len(palm_ids)
            palm_y /= len(palm_ids)

            wx = int(palm_x * w)
            wy = int(palm_y * h)

            
            if label == "Left":
            
                

                control_center_x = w // 4
                control_center_y = h // 2

                if wx < box_width:

                    # Horizontal
                    if wx < control_center_x - deadzone_x:
                        horizontal = HorizontalState.LEFT

                    elif wx > control_center_x + deadzone_x:
                        horizontal = HorizontalState.RIGHT

                    else:
                        horizontal = HorizontalState.CENTER

                    # Vertical
                    if wy < control_center_y - deadzone_y:
                        vertical = VerticalState.UP

                    elif wy > control_center_y + deadzone_y:
                        vertical = VerticalState.DOWN

                    else:
                        vertical = VerticalState.CENTER
                else:
                    direction = "LEFT HAND OUT OF BOUNDS"
                    
                    #could comment these out if it causes stutter movement
                    horizontal = HorizontalState.CENTER
                    vertical = VerticalState.CENTER
                    
                #movement
                match horizontal:
                    case HorizontalState.LEFT:
                        if not a_pressed:
                            pyautogui.keyDown('a')
                            a_pressed = True

                        if d_pressed:
                            pyautogui.keyUp('d')
                            d_pressed = False

                    case HorizontalState.RIGHT:
                        if a_pressed:
                            pyautogui.keyUp('a')
                            a_pressed = False

                        if not d_pressed:
                            pyautogui.keyDown('d')
                            d_pressed = True

                    case HorizontalState.CENTER:
                        if a_pressed:
                            pyautogui.keyUp('a')
                            a_pressed = False

                        if d_pressed:
                            pyautogui.keyUp('d')
                            d_pressed = False
                match vertical:
                    case VerticalState.UP:
                        if not w_pressed:
                            pyautogui.keyDown('w')
                            w_pressed = True

                        if s_pressed:
                            pyautogui.keyUp('s')
                            s_pressed = False

                    case VerticalState.DOWN:
                        if w_pressed:
                            pyautogui.keyUp('w')
                            w_pressed = False

                        if not s_pressed:
                            pyautogui.keyDown('s')
                            s_pressed = True

                    case VerticalState.CENTER:
                        if w_pressed:
                            pyautogui.keyUp('w')
                            w_pressed = False

                        if s_pressed:
                            pyautogui.keyUp('s')
                            s_pressed = False
            
                #palms
                cv2.circle(frame, (wx, wy), 12, (0, 255, 255), cv2.FILLED)
                direction = f"{horizontal.name} | {vertical.name}"
                
                #left hand position
                cv2.putText(
                    frame,
                    direction,
                    (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    3
                )
                
                index_up = states[0]  # index finger

                if index_up and not shift_pressed:
                    pyautogui.keyDown('shift')
                    shift_pressed = True

                elif not index_up and shift_pressed:
                    pyautogui.keyUp('shift')
                    shift_pressed = False
            
                     
            if label == "Right":
                index_up = states[0]  # index finger

                if index_up and not j_pressed:
                    pyautogui.keyDown('j')
                    j_pressed = True

                elif not index_up and j_pressed:
                    pyautogui.keyUp('j')
                    j_pressed = False
                    
                
                index_up = states[1]  # middle finger for bombing is very funny cause u basically flipping the game off lol

                if index_up and not k_pressed:
                    pyautogui.keyDown('k')
                    k_pressed = True

                elif not index_up and k_pressed:
                    pyautogui.keyUp('k')
                    k_pressed = False
            
                
                    

            index_tip = hand_landmarks.landmark[8]

            x = int(index_tip.x * w)
            y = int(index_tip.y * h)

            #right hand & left hadn
            color = (0, 255, 0) if label == "Right" else (255, 0, 0)

            cv2.circle(frame, (x, y), 10, color, cv2.FILLED)
            
            # middle finger
            middle_tip = hand_landmarks.landmark[12]

            middle_x = int(middle_tip.x * w)
            middle_y = int(middle_tip.y * h)

            cv2.circle(
                frame,
                (middle_x, middle_y),
                10,
                (0, 255, 255),
                cv2.FILLED
            )
            
            


            

    cv2.imshow("Webcam Controller", frame)
    key = cv2.waitKey(1) & 0xFF

    if key in (ord("q"), ord("Q")):
        break

#release keys or u are lowkey cooked 
for key in ['w', 'a', 's', 'd', 'j','k', 'shift']:
    pyautogui.keyUp(key)



cap.release()
cv2.destroyAllWindows()
