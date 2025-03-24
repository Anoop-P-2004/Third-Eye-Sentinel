import numpy as np
import tensorflow as tf
from tensorflow.keras.models import model_from_json
from lime import lime_image
import cv2
from skimage.segmentation import mark_boundaries
import matplotlib.pyplot as plt

class LIMEExplainer:
    def __init__(self, frame, model_json_path="backend/model.json", model_weights_path="backend/model_weights.h5"):
        self.frame = frame
        self.model = self.load_model(model_json_path, model_weights_path)
        self.image = self.preprocess_frame()
        self.explainer = lime_image.LimeImageExplainer()

    def load_model(self, model_json_path, model_weights_path):
        with open(model_json_path, "r") as file:
            model_json = file.read()
        model = model_from_json(model_json)
        model.load_weights(model_weights_path)
        return model

    def preprocess_frame(self, img_size=(250, 250)):
        frame_resized = cv2.resize(self.frame, img_size)
        return np.expand_dims(frame_resized, axis=0)

    def predict_fn(self, images):
        images = np.array(images)
        return self.model.predict(images)

    def explain(self):
        explanation = self.explainer.explain_instance(
            self.image[0], self.predict_fn, top_labels=1, hide_color=0, num_samples=500,batch_size=20
        )
        temp, mask = explanation.get_image_and_mask(
            explanation.top_labels[0], positive_only=True, num_features=5, hide_rest=False
        )
        fig, ax = plt.subplots()
        ax.imshow(mark_boundaries(temp, mask))
        ax.set_title("LIME Explanation")
        ax.axis("off")
        return fig
