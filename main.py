from io import BytesIO
import os
import json
import base64
import threading
from model import ResponseModel
from PIL import Image
from fastapi import FastAPI, Security, HTTPException, status, File, Depends
from fastapi.security import APIKeyHeader
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.security.api_key import APIKey
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv
from DETECTION.detection import TEXT_DETECTION
from RECOGNITION.recognition import TEXT_RECOGNITION
from FIREBASE.firebaseIO import FirebaseIO
from configs import Config
from error import *

load_dotenv(".env.development")
API_KEY: str = os.environ.get(str(Config.API_KEY.name))
REDIRECT_URL: str = os.environ.get(str(Config.REDIRECT_URL.name))
CORS_ORIGINS: str = os.environ.get(str(Config.CORS_ORIGINS.name))
FIREBASE_DATABASE_URL: str = os.environ.get(
    str(Config.FIREBASE_DATABASE_URL.name))
FIREBASE_STORAGE_BUCKET_URL: str = os.environ.get(
    str(Config.FIREBASE_STORAGE_BUCKET_URL.name))
FIREBASE_KEY_ENCODED: str = os.environ.get(str(Config.FIREBASE_KEY.name))
FIREBASE_KEY_DECODED = base64.b64decode(FIREBASE_KEY_ENCODED).decode('UTF-8')
FIREBASE_KEY_JSON = json.loads(FIREBASE_KEY_DECODED)
DETECT_CONFIDENCE: float = float(
    os.environ.get(str(Config.DETECT_CONFIDENCE.name)))

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

detection_model = TEXT_DETECTION()
recognition_model = TEXT_RECOGNITION()
fb = FirebaseIO(FIREBASE_KEY_JSON, FIREBASE_DATABASE_URL,
                FIREBASE_STORAGE_BUCKET_URL)

app = FastAPI(redoc_url=None, docs_url=None)


if CORS_ORIGINS is not None:
    try:
        origins = json.loads(CORS_ORIGINS)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    except:
        print("Invalid CORS_ORIGINS ENV Value")


async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Prescription Extractor",
        version="1.0.0",
        description="Python based API for extracting prescription information from images",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://res.cloudinary.com/pasindua/image/upload/v1681017394/api_assets/android-chrome-512x512_jrbyvw.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/", include_in_schema=False)
def read_root():
    if REDIRECT_URL is None or REDIRECT_URL == "":
        html_content = """
        <html>
            <head>
                <title>Prescription Extractor</title>
            </head>
            <body>
                <h1>
                    <a id="link">Go to Swagger Docs</a>
                </h1>
            </body>
            <script>
                document.getElementById("link").href = window.location.href + "docs";
            </script>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=200)
    else:
        return RedirectResponse(REDIRECT_URL)


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Prescription Extractor API", swagger_favicon_url="https://res.cloudinary.com/pasindua/image/upload/v1681017394/api_assets/favicon_y7jctk.ico")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return RedirectResponse("https://res.cloudinary.com/pasindua/image/upload/v1681017394/api_assets/favicon_y7jctk.ico")


@app.post("/detect_img", status_code=200)
async def add_post(api_key: APIKey = Depends(get_api_key), file: bytes = File(...)) -> ResponseModel:
    response = ResponseModel()
    try:
        try:
            input_image = Image.open(BytesIO(file)).convert("RGB")
        except:
            raise FileReadError()
        detected_dict = detection_model.detect(input_image, DETECT_CONFIDENCE)
        crop_dict = detection_model.crop_image()
        url_and_name = fb.uploadImage(detected_dict[Config.IMAGE.value])
        documentId = fb.createDocument(url_and_name[0], url_and_name[1])
        conf_list = detected_dict[Config.CONF_LIST.value]

        # Create Thread for background process
        thread = threading.Thread(
            target=runRecognizerInBackground, args=(documentId, crop_dict, conf_list,), daemon=True)
        thread.start()

        # Create Response
        response.documentID = documentId
        response.imageURL = url_and_name[0]
        response.boxes = crop_dict[Config.CROP_XYXY.value]
        response.confidences = conf_list
        resJson = jsonable_encoder(response)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=resJson
        )
    except Exception as e:
        errorMessage = ""
        httpStatus = None

        if isinstance(e, FileReadError):
            errorMessage = e.message
            httpStatus = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        elif isinstance(e, (FirebaseInitializationError, FirebaseCreateDocumentError, FirebaseUpdateDocumentError, FirebaseUploadError, DetectionInitializationError, DetectionDetectError, DetectionCropError, RecognitionInitializationError, RecognitionRecognizeError)):
            errorMessage = e.message
            httpStatus = status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            errorMessage = "Unknown Error"
            httpStatus = status.HTTP_500_INTERNAL_SERVER_ERROR

        response.error = errorMessage
        resJson = jsonable_encoder(response)
        return JSONResponse(
            status_code=httpStatus,
            content=resJson
        )


def runRecognizerInBackground(documentId: str, crop_dict: dict, conf_list: list) -> None:
    """
    #### Runs an OCR recognizer on a set of image crops in the background and updates a Firebase Firestore document with the recognition results.

    Arguments:
    - documentId (str): The ID of the Firestore document to update with the recognition results.
    - crop_dict (dict): A dictionary containing image crops and their corresponding bounding box coordinates, as returned by an object detection model.
    - conf_list (list[float]): A list of confidence scores for the detected objects.

    Returns:
        None.

    Notes:
    - This function runs an OCR recognizer on each image crop in the input dictionary in the background, without blocking the main thread. The recognition results are stored in a list, which is then passed to the FirebaseClient.updateDocument() method along with the confidence scores and bounding box coordinates.
    - The OCR recognizer is assumed to be defined in a separate module or class and imported as `recognition_model`. The recognizer should take a NumPy array representing an image as input and return a string representing the recognized text.
    - The input `crop_dict` should be a dictionary with keys 'CROP_IMG' and 'CROP_XYXY', corresponding to the image crops and their bounding box coordinates, respectively. The image crops should be provided as a list of NumPy arrays, and the coordinates should be provided as a list of lists, in the format [[x1, y1, x2, y2], [x1, y1, x2, y2], ...]. The `conf_list` should be a list of confidence scores for the detected objects, in the same order as the image crops.
    - The function assumes that the FirebaseClient instance is defined in the global scope as `fb`, and that the updateDocument() method is available on the instance.
    - This function does not return any values, but updates the specified Firestore document with the recognition results.
    """
    text_list = []
    for image in crop_dict[Config.CROP_IMG.value]:
        recognized_text = recognition_model.recognize(image)
        text_list.append(recognized_text)
        fb.updateDocument(documentId, text_list, conf_list,
                          crop_dict[Config.CROP_XYXY.value])
