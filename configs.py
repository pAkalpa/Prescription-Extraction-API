from enum import Enum
import os


class Config(Enum):
    """
    #### Application Configurations.
    """
    IMAGE = "RESULT_IMAGE"
    CONF_LIST = "CONFIDENCE_LIST"
    CROP_IMG = "CROPPED_IMG_LIST"
    CROP_XYXY = "CROPPED_XYXY_LIST"
    ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__)))
