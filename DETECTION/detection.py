import os
from ultralytics import YOLO
from configs import Config


class TEXT_DETECTION:
    image = None
    model = None
    result = None

    def __init__(self):
        """
        #### Class constructor for initializing the YOLOv8 object.
        """
        self.model = YOLO(os.path.join(
            Config.ROOT_DIR.value, 'DETECTION', 'model', 'best.pt'))

    def detect(self, image, confidence=0.5):
        """
        #### A method to detect objects in an input image using the initialized object detector object.

        Arguments:
        - image: A PIL.Image object or a NumPy array that represents the input image to be detected.
        - confidence: A float indicating the minimum confidence threshold for detected objects. Defaults to 0.5.

        Returns:
        - A dictionary containing:
            - Config.IMAGE.value: A PIL.Image object of the input image with bounding boxes drawn around detected objects.
            - Config.CONF_LIST.value: A list of floats representing the confidence scores of the detected objects in percentage.
        """
        self.image = image
        self.result = self.model(source=self.image, conf=confidence)
        result_plotted = self.result[0].plot()
        conf_list = self.result[0].boxes.conf.tolist()
        true_conf_list = [conf * 100 for conf in conf_list]
        return {Config.IMAGE.value: result_plotted, Config.CONF_LIST.value: true_conf_list}

    def crop_image(self):
        """
        #### A method to crop the detected objects in the input image using the initialized object detector object.

        Returns:
        - A dictionary containing:
            - Config.CROP_IMG.value: A list of cropped PIL.Image objects representing the detected objects in the input image.
            - Config.CROP_XYXY.value: A list of lists representing the bounding box coordinates of the detected objects in the format of [x1, y1, x2, y2].
        """
        boxes = self.result[0].boxes
        cropped_img_list = []
        cropped_img_xy_list = []

        for box in boxes:
            x1, y1, x2, y2 = box[0].xyxy.tolist()[0][:4]
            cropped_img_xy_list.append([x1, y1, x2, y2])
            cropped_img = self.image.crop((x1, y1, x2, y2))
            cropped_img_list.append(cropped_img)

        return {Config.CROP_IMG.value: cropped_img_list, Config.CROP_XYXY.value: cropped_img_xy_list}
