import os
import json
import secrets
from fastapi import FastAPI, Security, HTTPException, status
from fastapi.security import APIKeyHeader
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv(".env.development")
API_KEY: str = os.environ.get("API_KEY")
REDIRECT_URL: str = os.environ.get("REDIRECT_URL")
CORS_ORIGINS: str = os.environ.get("CORS_ORIGINS")

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


def api_key_auth(api_key: str = Security(api_key_header)):
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key"
        )
    else:
        try:
            if API_KEY is None or API_KEY == "":
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Server Auth Func Failed(contact admin)"
                )
            is_correct_apikey = secrets.compare_digest(
                str.encode(api_key), str.encode(API_KEY))
            if not is_correct_apikey:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Forbidden"
                )
        except:
            print("Invalid API_KEY ENV Value")


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


@app.get("/")
def read_root():
    print(REDIRECT_URL)
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


@app.get("/test")
def add_post(api_key: str = Security(api_key_auth)) -> dict:
    return {
        "data": "You used a valid API key."
    }
