import cv2
import mediapipe as mp
import numpy as np

# Инициализация MediaPipe
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# Константы
WIDTH, HEIGHT = 640, 480
ANIMAL_SIZE = 50
MASKS = ["mask1.png", "mask2.png", "mask3.png"]  # Список изображений масок
LOADED_MASKS = [cv2.imread(mask, cv2.IMREAD_UNCHANGED) for mask in MASKS]

mask_position = [WIDTH // 2, HEIGHT // 2]
mask_size = 200


def load_mask(mask_path):
    mask = cv2.imread(mask_path, cv2.IMREAD_UNCHANGED)
    if mask is None:
        print(f"Ошибка загрузки: {mask_path}")
        return None
    if mask.shape[-1] == 3:
        b, g, r = cv2.split(mask)
        alpha = np.ones(b.shape, dtype=b.dtype) * 255 
        mask = cv2.merge([b, g, r, alpha])
    return mask

LOADED_MASKS = [load_mask(mask) for mask in MASKS]
LOADED_MASKS = [m for m in LOADED_MASKS if m is not None] 
current_mask = LOADED_MASKS[0] if LOADED_MASKS else None

animal_pos = [WIDTH // 2, HEIGHT // 2]

def move_animal(hand_landmarks):
    global animal_pos
    index_finger = hand_landmarks[8]
    target_x = int(index_finger.x * WIDTH)
    target_y = int(index_finger.y * HEIGHT)
    animal_pos[0] += (target_x - animal_pos[0]) * 0.2
    animal_pos[1] += (target_y - animal_pos[1]) * 0.2

def update_mask_position(face_landmarks):
    global mask_position, mask_size
    left_eye = face_landmarks[33]  
    right_eye = face_landmarks[263]  
    nose = face_landmarks[1]  

    mask_x = int((left_eye.x + right_eye.x) / 2 * WIDTH)
    mask_y = int(nose.y * HEIGHT)

    eye_distance = abs(left_eye.x - right_eye.x) * WIDTH
    mask_size = int(eye_distance * 2.5)

    mask_position[0] += (mask_x - mask_position[0]) * 0.2
    mask_position[1] += (mask_y - mask_position[1]) * 0.2

cap = cv2.VideoCapture(0)
running = True
mask_index = 0

while running:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    face_results = face_mesh.process(rgb_frame)
    hand_results = hands.process(rgb_frame)

    # Обработка лица
    if face_results.multi_face_landmarks:
        for face_landmarks in face_results.multi_face_landmarks:
            mp_draw.draw_landmarks(frame, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS)
            update_mask_position(face_landmarks.landmark)

            if current_mask is not None:
                # Изменение размера маски
                mask_resized = cv2.resize(current_mask, (mask_size, mask_size))
                x_offset = int(mask_position[0] - mask_size / 2)
                y_offset = int(mask_position[1] - mask_size / 2)

                # Наложение маски с учетом прозрачности
                for c in range(3):
                    frame[y_offset:y_offset + mask_size, x_offset:x_offset + mask_size, c] = \
                        frame[y_offset:y_offset + mask_size, x_offset:x_offset + mask_size, c] * (1 - mask_resized[:, :, 3] / 255.0) + \
                        mask_resized[:, :, c] * (mask_resized[:, :, 3] / 255.0)

    # Обработка руки
    if hand_results.multi_hand_landmarks:
        for hand_landmarks in hand_results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            move_animal(hand_landmarks.landmark)

    # Отрисовка животного
    kitten = cv2.imread("kitten.png", cv2.IMREAD_UNCHANGED)
    if kitten is not None:
        kitten_resized = cv2.resize(kitten, (ANIMAL_SIZE, ANIMAL_SIZE))
        x, y = int(animal_pos[0]), int(animal_pos[1])
        frame[y:y + ANIMAL_SIZE, x:x + ANIMAL_SIZE] = kitten_resized[:, :, :3]

    cv2.imshow('Face Mask & Virtual Pet', frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        running = False
    elif key == ord('m'):
        mask_index = (mask_index + 1) % len(LOADED_MASKS)
        current_mask = LOADED_MASKS[mask_index]

cap.release()
cv2.destroyAllWindows()


# pip install mediapipe
# pip install opencv-python