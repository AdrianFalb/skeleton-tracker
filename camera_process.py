import cv2
import mediapipe as mp
import numpy as np
import math
import threading
from enum import Enum

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands

all_landmarks = np.zeros((75, 3), dtype=float)

class JointNames(Enum):
    left_wrist = 0
    left_thumb_cmc = 1
    left_thumb_mcp = 2
    left_thumb_ip = 3
    left_thumb_tip = 4
    left_index_mcp = 5
    left_index_pip = 6
    left_index_dip = 7
    left_index_tip = 8
    left_middle_mcp = 9
    left_middle_pip = 10
    left_middle_dip = 11
    left_middle_tip = 12
    left_ring_mcp = 13
    left_ring_pip = 14
    left_ring_dip = 15
    left_ring_tip = 16
    left_pinky_mcp = 17
    left_pinky_pip = 18
    left_pinky_dip = 19
    left_pinky_tip = 20

    right_wrist = 21
    right_thumb_cmc = 22
    right_thumb_mcp = 23
    right_thumb_ip = 24
    right_thumb_tip = 25
    right_index_mcp = 26
    right_index_pip = 27
    right_index_dip = 28
    right_index_tip = 29
    right_middle_mcp = 30
    right_middle_pip = 31
    right_middle_dip = 32
    right_middle_tip = 33
    right_ring_mcp = 34
    right_ring_pip = 35
    right_ring_dip = 36
    right_ring_tip = 37
    right_pinky_mcp = 38
    right_pinky_pip = 39
    right_pinky_dip = 40
    right_pinky_tip = 41

    nose = 42
    left_eye_in = 43
    left_eye = 44
    left_eye_out = 45
    right_eye_in = 46
    right_eye = 47
    right_eye_out = 48
    left_ear = 49
    right_ear = 50
    mouth_left = 51
    mouth_right = 52
    left_shoulder = 53
    right_shoulder = 54
    left_elbow = 55
    right_elbow = 56
    left_wrist_glob = 57
    right_wrist_glob = 58
    left_pinky = 59
    right_pinky = 60
    left_index = 61
    right_index = 62
    left_thumb = 63
    right_thumb = 64
    left_hip = 65
    right_hip = 66
    left_knee = 67
    right_knee = 68
    left_ankle = 69
    right_ankle = 70
    left_heel = 71
    right_heel = 72
    left_foot_index = 73
    right_foot_index = 74


def fill_left_hand(landmarks):
    for r in range(0, 21):
        all_landmarks[r][0] = landmarks.landmark[r].x
        all_landmarks[r][1] = landmarks.landmark[r].y
        all_landmarks[r][2] = landmarks.landmark[r].z
        # if r == 8:
        # print(landmarks.landmark[r].x, " ", landmarks.landmark[r].y, " ", landmarks.landmark[r].z)


def fill_right_hand(landmarks):
    for r in range(0, 21):
        all_landmarks[r + 21][0] = landmarks.landmark[r].x
        all_landmarks[r + 21][1] = landmarks.landmark[r].y
        all_landmarks[r + 21][2] = landmarks.landmark[r].z


def fill_pose(landmarks):
    for pose_point, r in zip(landmarks.landmark, range(0, 33)):
        if pose_point.visibility > 0.7:
            all_landmarks[r + 42][0] = pose_point.x
            all_landmarks[r + 42][1] = pose_point.y
            all_landmarks[r + 42][2] = pose_point.z


def distance_between_joints(j1, j2):
    # Define the two points
    p1 = np.array([all_landmarks[j1][0], all_landmarks[j1][1]])
    p2 = np.array([all_landmarks[j2][0], all_landmarks[j2][1]])

    # Calculate the Euclidean distance between the two points
    return np.linalg.norm(p1 - p2)


def angle_between_joints(j1, j2, j3):
    # Define the three points
    p1 = np.array([all_landmarks[j1][0], all_landmarks[j1][1]])
    p2 = np.array([all_landmarks[j2][0], all_landmarks[j2][1]])
    p3 = np.array([all_landmarks[j3][0], all_landmarks[j3][1]])

    if p1[0] == 0 or p1[1] == 0:
        return 0
    elif p2[0] == 0 or p2[1] == 0:
        return 0
    elif p3[0] == 0 or p3[1] == 0:
        return 0

    # Calculate the two vectors formed by the three points
    v1 = p1 - p2
    v2 = p3 - p2

    # Calculate the dot product of the two vectors
    dot_product = np.dot(v1, v2)

    # Calculate the magnitudes (lengths) of the two vectors
    magnitude1 = np.linalg.norm(v1)
    magnitude2 = np.linalg.norm(v2)

    if (magnitude1 * magnitude2) != 0:
        cosine_angle = dot_product / (magnitude1 * magnitude2)
        return math.degrees(math.acos(cosine_angle))
    else:
        return 0


def gesture_forward():
    upper_limit = 45
    lower_limit = 18

    left_arm_angle = angle_between_joints(JointNames.left_shoulder.value, JointNames.left_elbow.value,
                                          JointNames.left_wrist_glob.value)

    right_arm_angle = angle_between_joints(JointNames.right_shoulder.value, JointNames.right_elbow.value,
                                           JointNames.right_wrist_glob.value)

    if (gesture_level(JointNames.left_hip.value, JointNames.left_shoulder.value, JointNames.left_elbow.value) == 1) \
            and (gesture_level(JointNames.right_hip.value, JointNames.right_shoulder.value,
                               JointNames.right_elbow.value) == 1):
        if ((left_arm_angle > lower_limit) and (left_arm_angle < upper_limit)) \
                and ((right_arm_angle > lower_limit) and (right_arm_angle < upper_limit)):
            return "FORWARD"
        else:
            return "NULL"
    else:
        return "NULL"


def gesture_backwards():
    upper_limit = 180
    lower_limit = 155

    left_arm_angle = angle_between_joints(JointNames.left_shoulder.value, JointNames.left_elbow.value,
                                          JointNames.left_wrist_glob.value)

    right_arm_angle = angle_between_joints(JointNames.right_shoulder.value, JointNames.right_elbow.value,
                                           JointNames.right_wrist_glob.value)

    if (gesture_level(JointNames.left_hip.value, JointNames.left_shoulder.value, JointNames.left_elbow.value) == 2) \
            and (gesture_level(JointNames.right_hip.value, JointNames.right_shoulder.value,
                               JointNames.right_elbow.value) == 2):
        if ((left_arm_angle > lower_limit) and (left_arm_angle < upper_limit)) and (
                (right_arm_angle > lower_limit) and (right_arm_angle < upper_limit)):
            return "BACKWARD"
        else:
            return "NULL"
    else:
        return "NULL"


def gesture_right():
    right_upper_limit = 45
    right_lower_limit = 18

    left_upper_limit = 180
    left_lower_limit = 155

    left_arm_angle = angle_between_joints(JointNames.left_shoulder.value, JointNames.left_elbow.value,
                                          JointNames.left_wrist_glob.value)

    right_arm_angle = angle_between_joints(JointNames.right_shoulder.value, JointNames.right_elbow.value,
                                           JointNames.right_wrist_glob.value)

    if (gesture_level(JointNames.left_hip.value, JointNames.left_shoulder.value, JointNames.left_elbow.value) == 2) \
            and (gesture_level(JointNames.right_hip.value, JointNames.right_shoulder.value,
                               JointNames.right_elbow.value) == 1):
        if ((left_arm_angle > left_lower_limit) and (left_arm_angle < left_upper_limit)) and (
                (right_arm_angle > right_lower_limit) and (right_arm_angle < right_upper_limit)):
            return "RIGHT"
        else:
            return "NULL"
    else:
        return "NULL"


def gesture_left():
    left_upper_limit = 45
    left_lower_limit = 18

    right_upper_limit = 180
    right_lower_limit = 155

    left_arm_angle = angle_between_joints(JointNames.left_shoulder.value, JointNames.left_elbow.value,
                                          JointNames.left_wrist_glob.value)

    right_arm_angle = angle_between_joints(JointNames.right_shoulder.value, JointNames.right_elbow.value,
                                           JointNames.right_wrist_glob.value)

    if (gesture_level(JointNames.left_hip.value, JointNames.left_shoulder.value, JointNames.left_elbow.value) == 1) \
            and (gesture_level(JointNames.right_hip.value, JointNames.right_shoulder.value,
                               JointNames.right_elbow.value) == 2):
        if ((left_arm_angle > left_lower_limit) and (left_arm_angle < left_upper_limit)) and (
                (right_arm_angle > right_lower_limit) and (right_arm_angle < right_upper_limit)):
            return "LEFT"
        else:
            return "NULL"
    else:
        return "NULL"


def gesture_stop():
    gesture_level_right = gesture_level(JointNames.right_hip.value, JointNames.right_shoulder.value,
                                        JointNames.right_elbow.value)

    gesture_level_left = gesture_level(JointNames.left_hip.value, JointNames.left_shoulder.value,
                                       JointNames.left_elbow.value)

    d = distance_between_joints(JointNames.left_wrist_glob.value, JointNames.right_wrist_glob.value)

    if (gesture_level_left == 1) and (gesture_level_right == 1):
        if d < 0.04:
            return "STOP"
        else:
            return "NULL"
    else:
        return "NULL"


def gesture_level(j1, j2, j3):
    a = angle_between_joints(j1, j2, j3)

    if (a > 0) and (a <= 45):
        return 1
    elif (a > 45) and (a <= 100):
        return 2
    elif (a > 130) and (a <= 180):
        return 3
    else:
        return -1


def gesture_robot_select():
    left_arm_angle = angle_between_joints(JointNames.left_shoulder.value, JointNames.left_elbow.value,
                                          JointNames.left_wrist_glob.value)

    d = distance_between_joints(JointNames.right_wrist_glob.value, JointNames.right_shoulder.value)
    ref_d = distance_between_joints(JointNames.left_shoulder.value, JointNames.left_elbow.value)

    if gesture_level(JointNames.left_hip.value, JointNames.left_shoulder.value, JointNames.left_elbow.value) == 3:
        if (gesture_level(JointNames.right_hip.value, JointNames.right_shoulder.value,
                          JointNames.right_elbow.value) == 1) \
                or (gesture_level(JointNames.right_hip.value, JointNames.right_shoulder.value,
                                  JointNames.right_elbow.value) == 2):
            if (left_arm_angle > 160) and (left_arm_angle < 180) and (d < (ref_d / 2.1)):
                return "WAKE_UP"
            else:
                return "NULL"
        else:
            return "NULL"
    else:
        return "NULL"


def gesture_robot_mode_select():
    shoulder_right_x = all_landmarks[JointNames.right_shoulder.value][0]
    shoulder_left_x = all_landmarks[JointNames.left_shoulder.value][0]
    wrist_left_x = all_landmarks[JointNames.left_wrist_glob.value][0]
    wrist_right_x = all_landmarks[JointNames.right_wrist_glob.value][0]

    shoulder_right_y = all_landmarks[JointNames.right_shoulder.value][1]
    shoulder_left_y = all_landmarks[JointNames.left_shoulder.value][1]
    wrist_left_y = all_landmarks[JointNames.left_wrist_glob.value][1]
    wrist_right_y = all_landmarks[JointNames.right_wrist_glob.value][1]

    if (0 < np.absolute(shoulder_right_x - wrist_left_x) < 0.05) and (
            0 < np.absolute(shoulder_right_y - wrist_left_y) < 0.02):
        return "FOLLOW_MODE"
    elif (0 < np.absolute(shoulder_left_x - wrist_right_x) < 0.05) and (
            0 < np.absolute(shoulder_left_y - wrist_right_y) < 0.02):
        return "CONTROL_MODE"
    else:
        return "NULL"


def gesture_follow_mode_bands():
    global all_landmarks

    point_x = 0
    point_y = 0

    point_x = (all_landmarks[JointNames.right_shoulder.value][0] + all_landmarks[JointNames.left_shoulder.value][0]) / 2
    point_y = (all_landmarks[JointNames.right_shoulder.value][1])

    # IMAGE je flipped takze tieto polia budu naopak nez co je intuitivne
    # ========================================================================
    # Policka 1, 2, 3
    if (point_y > 0) and (point_y < 0.3):  # y-ova suradnica

        if (point_x > 0.0) and (point_x < 0.3):  # x-ova suradnica
            return "FOLLOW_BACKWARD_LEFT"
        elif (point_x >= 0.3) and (point_x < 0.7):  # x-ova suradnica
            return "FOLLOW_BACKWARD"
        elif (point_x >= 0.7) and (point_x < 1.0):  # x-ova suradnica
            return "FOLLOW_BACKWARD_RIGHT"
        else:
            return "NULL"
    # ========================================================================
    # Policka 4, 5, 6
    elif (point_y >= 0.3) and (point_y <= 0.6):  # y-ova suradnica

        if (point_x > 0.0) and (point_x < 0.3):  # x-ova suradnica
            return "FOLLOW_LEFT"
        elif (point_x >= 0.3) and (point_x < 0.7):  # x-ova suradnica
            return "NULL"
        elif (point_x >= 0.7) and (point_x < 1.0):  # x-ova suradnica
            return "FOLLOW_RIGHT"
        else:
            return "NULL"
    # ========================================================================
    # Policka 7, 8, 9
    elif (point_y > 0.6) and (point_y < 1.0):  # y-ova suradnica

        if (point_x > 0.0) and (point_x < 0.3):  # x-ova suradnica
            return "FOLLOW_FORWARD_LEFT"
        elif (point_x >= 0.3) and (point_x < 0.7):  # x-ova suradnica
            if (point_y > 0.6) and (point_y < 0.8):
                return "FOLLOW_FORWARD"
            elif (point_y >= 0.8) and (point_y < 1):
                return "FOLLOW_FORWARD_FAR"
            else:
                return "NULL"
        elif (point_x >= 0.7) and (point_x < 1.0):  # x-ova suradnica
            return "FOLLOW_FORWARD_RIGHT"
        else:
            return "NULL"
    else:
        return "NULL"


def process_camera_data(image, udp_server, robot_ip_address):
    global all_landmarks
    image_height = image.shape[0]
    image_width = image.shape[1]
    image_channels = image.shape[2]

    with mp_pose.Pose(
            min_detection_confidence=0.9,
            min_tracking_confidence=0.9) as pose:  # , \
        # mp_hands.Hands(
        #     model_complexity=0,
        #     min_detection_confidence=0.5,
        #     min_tracking_confidence=0.5) as hands:

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        # results_h = hands.process(image)

        # Draw the pose annotation on the image
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Kreslenie tela
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

        all_landmarks = np.zeros((75, 3), dtype=float)  # vynulovanie
        if results.pose_landmarks:
            fill_pose(results.pose_landmarks)

        # if results_h.multi_hand_landmarks:
        #
        #     for hand_landmarks, hand_sides in zip(results_h.multi_hand_landmarks, results_h.multi_handedness):
        #         mp_drawing.draw_landmarks(
        #             image,
        #             hand_landmarks,
        #             mp_hands.HAND_CONNECTIONS,
        #             mp_drawing_styles.get_default_hand_landmarks_style(),
        #             mp_drawing_styles.get_default_hand_connections_style())
        #         if hand_sides.classification[0].label == "Right":
        #             fill_left_hand(hand_landmarks)
        #         else:
        #             fill_right_hand(hand_landmarks)

        robot = "ROBOT:" + robot_ip_address
        command = "COMMAND:"
        follow_command = "FOLLOW_COMMAND:"

        # Control Mode
        if gesture_stop() == "STOP":
            command = command + "STOP"
        elif gesture_robot_select() == "WAKE_UP":
            command = command + "WAKE_UP"
        elif gesture_forward() == "FORWARD":
            command = command + "FORWARD"
        elif gesture_backwards() == "BACKWARD":
            command = command + "BACKWARD"
        elif gesture_left() == "LEFT":
            command = command + "LEFT"
        elif gesture_right() == "RIGHT":
            command = command + "RIGHT"
        elif robot_mode := gesture_robot_mode_select():
            command = command + robot_mode
        else:
            command = command + "NULL"

        # Follow Mode
        if follow_mode_command := gesture_follow_mode_bands():
            follow_command = follow_command + follow_mode_command
        else:
            follow_command = follow_command + "NULL"

        # Draw Lines into the camera frame
        cv2.line(image, (int(image_width * 0.3), 0), (int(image_width * 0.3), image_height), (255, 255, 255))  # toto je vpravo
        cv2.line(image, (int(image_width * 0.7), 0), (int(image_width * 0.7), image_height), (255, 255, 255))  # toto je vlavo
        cv2.line(image, (0, int(image_height * 0.3)), (image_width, int(image_height * 0.3)), (255, 255, 255))  # toto je hore
        cv2.line(image, (0, int(image_height * 0.6)), (image_width, int(image_height * 0.6)), (255, 255, 255))  # toto je dole
        cv2.line(image, (int(image_width * 0.3), int(image_height * 0.8)), (int(image_width * 0.7), int(image_height * 0.8)), (255, 255, 255)) # toto deli dolne stredne pasmo na polovicu

        if (command != "COMMAND:NULL") or (follow_command != "FOLLOW_COMMAND:NULL"):
            message = robot + ";" + command + ";" + follow_command
            udp_server.set_data(bytes(message.encode("utf-8")))
            print(udp_server.get_data())
            udp_server.send_message()

        return image
