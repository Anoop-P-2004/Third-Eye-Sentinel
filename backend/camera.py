import cv2
from detection import AccidentDetectionModel
import numpy as np

model = AccidentDetectionModel('backend\model.json', 'backend\model_weights.h5')
font = cv2.FONT_HERSHEY_SIMPLEX


def startapplication(path):
    video = cv2.VideoCapture(path)
    max_prob = 0
    best_frame = None
    best_pred="Non Accident"

    while True:
        ret, frame = video.read()
        if not ret:
            break
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        roi = cv2.resize(gray_frame, (250, 250))

        pred, prob = model.predict_accident(roi[np.newaxis, :, :])
        if pred == "Accident":
            current_prob = round(prob[0][0] * 100, 2)
            if current_prob > max_prob:
                max_prob = current_prob
                best_pred=pred
                best_frame = frame.copy()

    video.release()
    cv2.destroyAllWindows()
    if max_prob > 0.5:
        return best_pred, best_frame
    return None,None


if __name__ == '__main__':
    startapplication()