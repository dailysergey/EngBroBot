from imageai.Detection import ObjectDetection
import os  


class ImageObjects:
    def __init__(self):
        self.execution_path = os.getcwd()
        self.model_path = os.path.join(self.execution_path,"src","objectDetection","model")
        self.input_image_path = os.path.join(self.execution_path,"src""objectDetection","input")
        self.output_image_path = os.path.join(self.execution_path,"src","objectDetection","output")
        self.detector = ObjectDetection()
        self.detector.setModelTypeAsRetinaNet()
        self.detector.setModelPath(os.path.join(
            self.model_path, "resnet50_coco_best_v2.0.1.h5"))
        self.detector.loadModel()

    def detect(self, imageName):
        imageNew = imageName.split('.')[0]+"_new.jpg"
        self.detector.detectObjectsFromImage(input_image=os.path.join(
            self.input_image_path, imageName), output_image_path=os.path.join(self.output_image_path, imageNew))
        #TODO delete result images
        return imageNew