import os
from ultralytics import YOLO
from configs import Config
from error import DetectionInitializationError, DetectionDetectError, DetectionCropError


class TEXT_DETECTION:
    image = None
    model = None
    result = None

    def __init__(self) -> None:
        """
        #### Initializes a YOLO object detector for use in detecting objects in images.

        Raises:
        - DetectionInitializationError: If the YOLO model cannot be loaded.

        Notes:
        - This function initializes a YOLO object detector by loading the model weights from a pre-trained model file. The path to the model file is specified in the `Config` object.
        - The function raises a `DetectionInitializationError` if the model fails to load, which could be due to a variety of reasons such as a missing or corrupted file, unsupported file format, or incorrect file path.
        - The initialized object detector can be used to detect objects in images by calling the `detect()` method of the object, which takes an image file or array as input and returns a list of detection results, each containing

        """
        try:
            self.model = YOLO(os.path.join(
                Config.ROOT_DIR.value, 'DETECTION', 'model', 'best.pt'))
        except:
            raise DetectionInitializationError()

    def detect(self, image, confidence=0.5) -> dict:
        """
        #### Detects objects in an image using the YOLO object detector.

        Arguments:
        - image: An image file or array to be processed.
        - confidence: The minimum confidence score threshold for detections to be considered. Default is 0.5.

        Returns:
        - A dictionary containing the following keys and values:
         - Config.IMAGE.value: A visualization of the image with detection results overlaid.
         - Config.CONF_LIST.value: A list of confidence scores for the detected objects, expressed as a percentage.

        Raises:
        - DetectionDetectError: If an error occurs during object detection.

        Notes:
        - This function takes an image file or array as input and processes it using the YOLO object detector that was initialized earlier. The detection results are returned in a dictionary that contains a visualization of the image with detection results overlaid, as well as a list of confidence scores for the detected objects.
        - The `confidence` argument can be used to control the sensitivity of the detector. A lower value will result in more detections being made, but at the cost of lower precision.
        - The function raises a `DetectionDetectError` if an error occurs during object detection, which could be due to a variety of reasons such as an invalid input image, memory allocation errors, or internal model errors.

        """
        try:
            self.image = image
            self.result = self.model(source=self.image, conf=confidence)
            result_plotted = self.result[0].plot()
            conf_list = self.result[0].boxes.conf.tolist()
            true_conf_list = [conf * 100 for conf in conf_list]
            return {Config.IMAGE.value: result_plotted, Config.CONF_LIST.value: true_conf_list}
        except:
            raise DetectionDetectError()

    def crop_image(self) -> dict:
        """
        #### Crops the detected objects from the input image and returns a dictionary containing the cropped images and their respective coordinates.

        Arguments:
        - None

        Returns:
        - A dictionary containing the following keys and values:
         - Config.CROP_IMG.value:  A list of PIL Image objects, each of which represents one of the detected objects in the input image.
         - Config.CROP_XYXY.value: A list of lists, each containing the four coordinates (x1, y1, x2, y2) of the bounding box for the corresponding cropped image.

        Raises:
        - DetectionCropError: If there is an error in the detection or cropping of objects from the input image.

        Notes:
        - The function assumes that the image and detection results are already loaded into the instance of the class before calling this function.
        - The function loops through each box in the detection results and extracts the xyxy coordinates to crop the corresponding region from the original image.
        - The function returns a dictionary containing two lists. The first list contains the cropped image objects and the second list contains the xyxy coordinates of each cropped image.
        - The function raises a `DetectionCropError` if there is an error in the detection or cropping of objects from the input image, which could be due to a variety of reasons such as an invalid input image, memory allocation errors, or internal model errors.

        """
        try:
            boxes = self.result[0].boxes
            cropped_img_list = []
            cropped_img_xy_list = []

            for box in boxes:
                x1, y1, x2, y2 = box[0].xyxy.tolist()[0][:4]
                cropped_img_xy_list.append([x1, y1, x2, y2])
                cropped_img = self.image.crop((x1, y1, x2, y2))
                cropped_img_list.append(cropped_img)

            return {Config.CROP_IMG.value: cropped_img_list, Config.CROP_XYXY.value: cropped_img_xy_list}
        except:
            raise DetectionCropError()
