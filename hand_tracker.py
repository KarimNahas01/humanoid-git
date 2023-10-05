import numpy as np
import cv2
import mediapipe as mp


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

    def position_finder(self, image, hand_num=None, draw=True):
        lmlist = []

        if self.results.multi_hand_landmarks:
            num_hands = len(self.results.multi_hand_landmarks)
            if hand_num is None:
                for hand_num in range(0, num_hands):
                    lmlist = self.get_fingers_states(image, hand_num, draw)

        return lmlist

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

        fingers_range = {"thumb": [340, 225],
                         "index": [300, 130],
                         "middle": [315, 130],
                         "ring": [315, 130],
                         "pinky": [300, 130]}

        for key in fingers_dict.keys():
            angle = self.get_finger_angle(hand_world.landmark, fingers_dict[key])
            radius = 5

            lm = hand.landmark[fingers_dict[key][0]]
            cx, cy = int(lm.x * w), int(lm.y * h)

            # TODO transform angles to percentage for each finger.
            # TODO Get range of max and min angle to do the scaling transformation

            lmlist.append([key, angle])

            if draw:
                if label == "Right":
                    color = (255, 0, 0)
                elif label == "Left":
                    color = (0, 0, 255)
                else:
                    color = (255, 0, 255)

                if angle is not None:
                    cv2.putText(image, format(angle, ".2f"), (cx + 5, cy),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA)
                cv2.circle(image, (cx, cy), radius, color, cv2.FILLED)

        return lmlist

    @staticmethod
    def get_finger_angle(hand_landmarks, finger_indexes):

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

            angle_joint = angle_between(end - joint, start - joint)
            finger_angle += angle_joint

        return (np.rad2deg(finger_angle) + 180) % 360

    @staticmethod
    def distance_org(coords, org):
        return np.sqrt(np.sum(np.square(coords - org)))


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)


def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            > angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            > angle_between((1, 0, 0), (1, 0, 0))
            0.0
            > angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def main():
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()

    while True:
        success, image = cap.read()
        image = cv2.flip(image, 1)
        image = tracker.hands_finder(image)
        lmList = tracker.position_finder(image)
        if len(lmList) != 0:
            print(lmList)

        cv2.imshow("Video", image)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
