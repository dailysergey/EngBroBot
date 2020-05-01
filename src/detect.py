import os
import cv2
import cvlib as cv
from cvlib.object_detection import draw_bbox
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class ImageObjects:
    def __init__(self):
        self.execution_path = os.getcwd()
        self.model_path = os.path.join(
            self.execution_path, "src", "objectDetection", "model")
        self.input_image_path = os.path.join(
            self.execution_path, "src", "objectDetection", "input")
        self.output_image_path = os.path.join(
            self.execution_path, "src", "objectDetection", "output")
        logging.info("[ImageObjects]:Constructor for ImageObjects created.")

    def detect(self, imageName):
        logging.info("[Detect]: get name for image: {}".format(imageName))
        imageNew = imageName.split('.')[0]+"_new.jpg"
        input_image = cv2.imread(os.path.join(
            self.input_image_path, imageName))
        bbox, label, conf = cv.detect_common_objects(
            input_image, confidence=0.25)
        output_image = draw_bbox(input_image, bbox, label, conf)
        logging.info("[Detect]: object detection completed")
        imageRecognized = os.path.join(
            self.output_image_path, imageNew)
        # save output
        cv2.imwrite(imageRecognized, output_image)
        logging.info(
            "[Detect]: object detection image saved: {}".format(imageName))
        logging.info("[Detect]: result directory : {}".format(imageRecognized))
        return imageRecognized
