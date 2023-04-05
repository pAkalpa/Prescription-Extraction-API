from io import BytesIO
import os
import json
from model import ResponseModel
from PIL import Image
from fastapi import FastAPI, Security, HTTPException, status, File, Depends
from fastapi.security import APIKeyHeader
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.security.api_key import APIKey
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from DETECTION.detection import TEXT_DETECTION
from RECOGNITION.recognition import TEXT_RECOGNITION
from configs import Config

load_dotenv(".env.development")
API_KEY: str = os.environ.get("API_KEY")
REDIRECT_URL: str = os.environ.get("REDIRECT_URL")
CORS_ORIGINS: str = os.environ.get("CORS_ORIGINS")

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

detection_model = TEXT_DETECTION()
recognition_model = TEXT_RECOGNITION()


app = FastAPI(title="Prescription Extractor", redoc_url=None)


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


@app.get("/")
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


@app.post("/detect", status_code=200)
async def add_post(api_key: APIKey = Depends(get_api_key), file: bytes = File(...)) -> ResponseModel:
    response = ResponseModel()
    try:
        input_image = Image.open(BytesIO(file)).convert("RGB")
        detected_dict = await detection_model.detect(input_image)
        response.confidences = await detected_dict[Config.CONF_LIST.value]
        resJson = jsonable_encoder(response)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=resJson
        )
    except:
        response.error = "INVALID MEDIA TYPE"
        resJson = jsonable_encoder(response)
        return JSONResponse(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            content=resJson
        )
