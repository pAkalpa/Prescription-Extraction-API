import cv2
import time
import firebase_admin
from configs import Config
from firebase_admin import credentials, firestore, storage


class FirebaseIO:
    db = None
    bucket = None
    collection_ref = None

    def __init__(self, FIREBASE_KEY_JSON, FIREBASE_DATABASE_URL, FIREBASE_STORAGE_BUCKET_URL) -> None:
        """
        #### Initializes a new instance of the FirebaseClient class.

        Arguments:
        - FIREBASE_KEY_JSON (str): The path to the Firebase service account key JSON file.
        - FIREBASE_DATABASE_URL (str): The URL of the Firebase Realtime Database instance to use.
        - FIREBASE_STORAGE_BUCKET_URL (str): The URL of the Firebase Cloud Storage bucket to use.

        Returns:
        None.

        Notes:
        - This function initializes a new Firebase app instance with the provided service account key, database URL, and storage bucket URL. It also sets up a Firestore client instance and a Cloud Storage bucket instance for further use. The app instance and its associated resources can be accessed via the instance properties 'db', 'bucket', and 'collection_ref'.
        - This function should be called only once per application instance, typically at startup. Subsequent calls to this function will result in undefined behavior.

        """
        fb_cred = credentials.Certificate(FIREBASE_KEY_JSON)
        firebase_admin.initialize_app(fb_cred, {
            Config.FIREBASE_DATABASE_URL.value: FIREBASE_DATABASE_URL,
            Config.FIREBASE_STORAGE_BUCKET_URL.value: FIREBASE_STORAGE_BUCKET_URL
        })
        self.db = firestore.client()
        self.bucket = storage.bucket()
        self.collection_ref = self.db.collection(
            Config.FIREBASE_COLL_STORE_NAME.value)

    def createDocument(self, IMAGE_URL: str, IMAGE_NAME: str) -> str:
        DATA = {
            "IMAGE_NAME": IMAGE_NAME,
            "IMAGE_URL": IMAGE_URL,
            "DETECT_LIST": [],
            "CONFIDENCE_LIST": [],
            "BOX_LIST": {}
        }
        _, doc_ref = self.collection_ref.add(DATA)
        return doc_ref.id

    def updateDocument(self, documentId: str, DETECT_LIST=[], CONFIDENCE_LIST=[], XYXY_LIST=[]):
        """
        #### Updates a document in the Firebase Firestore collection with the specified data.

        Arguments:
        - documentId (str): The ID of the document to update.
        - DETECT_LIST (list[str], optional): A list of detection labels to store in the document.
        - CONFIDENCE_LIST (list[float], optional): A list of detection confidence scores to store in the document.
        - XYXY_LIST (list[list[float]], optional): A list of bounding box coordinates to store in the document, in the format [[x1, y1, x2, y2], [x1, y1, x2, y2], ...]. Defaults to an empty list.

        Returns:
            None.

        Notes:
        - This function updates an existing document in the Firestore collection associated with the FirebaseClient instance. The document is identified by its ID, which must be a non-empty string.
        - The function constructs a data dictionary from the input arguments, with keys 'DETECT_LIST', 'CONFIDENCE_LIST', and 'BOX_LIST', corresponding to the input lists. The 'BOX_LIST' key maps to a nested dictionary that contains the bounding box coordinates, with keys 'box1', 'box2', and so on. The coordinates themselves are stored as dictionaries with keys 'x1', 'y1', 'x2', and 'y2'.
        - Any arguments that are not specified will not be included in the updated document, leaving their previous values intact. If no arguments are specified, the document will not be modified.
        - This function assumes that the FirebaseClient instance has been properly initialized with a valid Firebase app and Firestore client.
        """
        sub_keys = ['x1', 'y1', 'x2', 'y2']
        box_data = {}
        for i, sub_list in enumerate(XYXY_LIST):
            sub_dict = {}
            for j, value in enumerate(sub_list):
                sub_dict[sub_keys[j]] = value
            box_data[f"box{i + 1}"] = sub_dict

        DATA = {
            "DETECT_LIST": DETECT_LIST,
            "CONFIDENCE_LIST": CONFIDENCE_LIST,
            "BOX_LIST": box_data
        }
        doc_ref = self.collection_ref.document(documentId)
        doc_ref.update(DATA)

    def uploadImage(self, image) -> tuple:
        """
        #### Uploads an image to a Firebase Cloud Storage bucket associated with the FirebaseClient instance.

        Arguments:
        - image (numpy.ndarray): A NumPy array representing the image to upload.

        Returns:
        - A tuple containing the public URL and file name of the uploaded image.

        Notes:
        - This function takes a NumPy array representing an image and saves it to a temporary file in JPEG format. The file is then uploaded to a Cloud Storage bucket associated with the FirebaseClient instance. The uploaded file is given a unique file name based on the current date and time.
        - The function returns a tuple containing the public URL of the uploaded file and its file name. The public URL can be used to access the file via HTTP or HTTPS.
        - This function assumes that the FirebaseClient instance has been properly initialized with a valid Firebase app and Cloud Storage bucket instance.
        """
        saveImgName = "{}.jpg".format(Config.TEMP_IMG.value)
        cv2.imwrite(saveImgName, image)
        fileName = time.strftime("%Y%m%d-%H%M%S")
        blob = self.bucket.blob(
            "{}/{}.jpg".format(Config.FIREBASE_COLL_STORE_NAME.value, fileName))
        blob.upload_from_filename(saveImgName)
        blob.make_public()
        return (blob.public_url, fileName)
