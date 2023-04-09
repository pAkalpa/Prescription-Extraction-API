from enum import Enum, auto
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
    FIREBASE_KEY = auto()
    FIREBASE_DATABASE_URL = "databaseURL"
    FIREBASE_STORAGE_BUCKET_URL = "storageBucket"
    FIREBASE_COLL_STORE_NAME = "Predictions"
    API_KEY = auto()
    REDIRECT_URL = auto()
    CORS_ORIGINS = auto()
    TEMP_IMG = "temp"
    SENTRY_DSN = auto()
