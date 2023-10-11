import numpy as np
import cv2
import mediapipe as mp

# import matplotlib.pyplot as plt


class HandTracker:
    def __init__(self, mode=False, max_hands=5, detection_con=0.5, model_complexity=1, track_con=0.5):
        self.mode = mode
        self.maxHands = max_hands
        self.detectionCon = detection_con
        self.modelComplex = model_complexity
        self.trackCon = track_con
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplex,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

        self.results = None

    def hands_finder(self, image, draw=True):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(image_rgb)

        if draw:
            mhl = self.results.multi_hand_landmarks  # noqa
            if mhl:
                for handLms in mhl:
                    self.mpDraw.draw_landmarks(image, handLms, self.mpHands.HAND_CONNECTIONS)

        return image

    def position_finder(self, image, hand_label=None, draw=True):
        all_lmlist = []

        image = self.hands_finder(image)

        if self.results.multi_hand_landmarks:
            num_hands = len(self.results.multi_hand_landmarks)
            for hand_num in reversed(range(num_hands)):
                lmlist, label = self.get_fingers_states(image, hand_num, draw)
                if hand_label is not None:
                    if label == hand_label:
                        all_lmlist.append(lmlist)
                else:
                    all_lmlist.append(lmlist)

        return all_lmlist

    def get_fingers_states(self, image, hand_num, draw=True):
        lmlist = []
        h, w, c = image.shape
        hand = self.results.multi_hand_landmarks[hand_num]
        hand_world = self.results.multi_hand_world_landmarks[hand_num]
        classification = self.results.multi_handedness[hand_num]
        label = classification.classification[0].label

        fingers_dict = {"thumb": [4, 3, 2, 1, 0],
                        "index": [8, 7, 6, 5, 0],
                        "middle": [12, 11, 10, 9, 0],
                        "ring": [16, 15, 14, 13, 0],
                        "pinky": [20, 19, 18, 17, 0]}

        fingers_range = {"thumb": [320, 250],
                         "index": [300, 130],
                         "middle": [315, 130],
                         "ring": [315, 130],
                         "pinky": [300, 130]}

        for key in fingers_dict.keys():
            angle = self.get_finger_angle(hand_world.landmark, fingers_dict[key])
            radius = 5

            lm = hand.landmark[fingers_dict[key][0]]
            cx, cy = int(lm.x * w), int(lm.y * h)

            # Transform angles to percentage for each finger.
            percentage = 1 - ((angle - fingers_range[key][1]) / (fingers_range[key][0] - fingers_range[key][1]))
            if percentage < 0:
                percentage = 0
            elif percentage > 1:
                percentage = 1

            lmlist.append([key, angle, percentage])

            if draw:
                if label == "Right":
                    color = (255, 0, 0)
                elif label == "Left":
                    color = (0, 0, 255)
                else:
                    color = (255, 0, 255)

                if angle is not None:
                    cv2.putText(image, format(percentage, ".2f"), (cx + 5, cy),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA)

                # Print ID hand
                lm = hand.landmark[0]
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.putText(image, str(hand_num), (cx + 5, cy),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA)

                cv2.circle(image, (cx, cy), radius, color, cv2.FILLED)

        return lmlist, label

    def get_finger_angle(self, hand_landmarks, finger_indexes):

        finger_angle = 0
        for i in range(len(finger_indexes)-2):
            end_id_landmark = finger_indexes[i]
            joint_id_landmark = finger_indexes[i+1]
            start_id_landmark = finger_indexes[i+2]

            end = np.array([hand_landmarks[end_id_landmark].x,
                            hand_landmarks[end_id_landmark].y,
                            hand_landmarks[end_id_landmark].z])
            joint = np.array([hand_landmarks[joint_id_landmark].x,
                              hand_landmarks[joint_id_landmark].y,
                              hand_landmarks[joint_id_landmark].z])
            start = np.array([hand_landmarks[start_id_landmark].x,
                              hand_landmarks[start_id_landmark].y,
                              hand_landmarks[start_id_landmark].z])

            angle_joint = self.angle_between(end - joint, start - joint)
            finger_angle += angle_joint

        return (np.rad2deg(finger_angle) + 180) % 360

    @staticmethod
    def distance_org(coords, org):
        return np.sqrt(np.sum(np.square(coords - org)))

    @staticmethod
    def unit_vector(vector):
        """ Returns the unit vector of the vector.  """
        return vector / np.linalg.norm(vector)

    def angle_between(self, v1, v2):
        """ Returns the angle in radians between vectors 'v1' and 'v2'::

                > angle_between((1, 0, 0), (0, 1, 0))
                1.5707963267948966
                > angle_between((1, 0, 0), (1, 0, 0))
                0.0
                > angle_between((1, 0, 0), (-1, 0, 0))
                3.141592653589793
        """
        v1_u = self.unit_vector(v1)
        v2_u = self.unit_vector(v2)
        return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

    def snapshot_capture(self, debug=True):
        cap = cv2.VideoCapture(0)
        success, image = cap.read()
        image = cv2.flip(image, 1)
        lm_list = self.position_finder(image, hand_label="Right")

        if debug:
            cv2.imshow("Video", image)
            cv2.waitKey(500)

        return lm_list


def main_video():
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()

    i = 0

    while True:
        success, image = cap.read()

        image = cv2.flip(image, 1)
        lm_list = tracker.position_finder(image, hand_label="Right")

        if len(lm_list) != 0:
            # print(lm_list[0][0][2], lm_list[0][1][2], lm_list[0][2][2], lm_list[0][3][2], lm_list[0][4][2])
            print(lm_list[0][0][1])

            # plt.scatter(i, lm_list[0][0][2], c="b")
            # plt.scatter(i, lm_list[0][1][2], c="g")
            # plt.scatter(i, lm_list[0][2][2], c="r")
            # plt.scatter(i, lm_list[0][3][2], c="y")
            # plt.scatter(i, lm_list[0][4][2], c="k")
            # plt.pause(0.0005)

        i += 1

        cv2.imshow("Video", image)
        cv2.waitKey(1)


if __name__ == "__main__":
    main_video()
    # HandTracker().snapshot_capture()
