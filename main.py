import cv2
import mediapipe as mp
import time
import pyautogui
from enum import Enum

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

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
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 60) #mine is capped at around 40 but you might have a better webcam

def get_finger_states(hand):
    tips = [8, 12, 16, 20]
    fingers = []

    for tip in tips:
        if hand.landmark[tip].y < hand.landmark[tip - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers
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
    
    action = "k HELD" if k_pressed else "k RELEASED"

    cv2.putText(
        frame,
        action,
        (int(w * 0.57), int(h * 0.7)),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 0),
        2
    )
    action = "J HELD" if j_pressed else "J RELEASED"

    cv2.putText(
        frame,
        action,
        (int(w * 0.57), int(h * 0.5)),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 0),
        2
    )
    
    action = "shift HELD" if shift_pressed else "shift RELEASED"
    
    cv2.putText(
        frame,
        action,
        (int(w * 0.57), int(h * 0.3)),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 0),
        2
    )

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb)
    
    control_width = w // 2

    cv2.line(
        frame,
        (control_width, 0),
        (control_width, h),
        (0, 255, 255),
        3
    )
    
    #vertical lines
    cv2.line(frame, (control_width // 3, 0),
         (control_width // 3, h),
         (100, 100, 100), 2)

    cv2.line(frame, (2 * control_width // 3, 0),
         (2 * control_width // 3, h),
         (100, 100, 100), 2)

    #horizontal lines
    cv2.line(frame, (0, h // 3), (control_width, h // 3), (100, 100, 100), 2)
    cv2.line(frame, (0, 2 * h // 3), (control_width, 2 * h // 3), (100, 100, 100), 2)
    if results.multi_hand_landmarks and results.multi_handedness:

        for hand_landmarks, handedness in zip(
            results.multi_hand_landmarks,
            results.multi_handedness
        ):
            label = handedness.classification[0].label
            states = get_finger_states(hand_landmarks)

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )
            
            palm_ids = [0, 5, 9, 13, 17]

            palm_x = 0
            palm_y = 0

            for pid in palm_ids:
                palm_x += hand_landmarks.landmark[pid].x
                palm_y += hand_landmarks.landmark[pid].y

            palm_x /= len(palm_ids)
            palm_y /= len(palm_ids)

            wx = int(palm_x * w)
            wy = int(palm_y * h)

            control_width = w // 2  # left half of screen

            
            
            if label == "Left":
            
                

                if wx < control_width:

                    #x pos
                    if wx < control_width // 3:
                        horizontal = HorizontalState.LEFT
                        

                    elif wx > 2 * control_width // 3:
                        horizontal = HorizontalState.RIGHT
                        
                    else:
                        horizontal = HorizontalState.CENTER


                    # y pos
                    if wy < h // 3:
                        vertical = VerticalState.UP

                    elif wy > 2 * h // 3:
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
                    
            else:
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

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
    if cv2.waitKey(1) & 0xFF == ord("Q"):
            break

#release keys or u are lowkey cooked 
for key in ['w', 'a', 's', 'd', 'j','k', 'shift']:
    pyautogui.keyUp(key)



cap.release()
cv2.destroyAllWindows()
