import base64
import os
from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from mangum import Mangum

app = FastAPI(
    title="Base64 Encoder/Decoder API",
    description="Encode and decode Base64 strings with simple HTTP API calls",
    version="1.0.0"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# API key auth
API_KEY = os.getenv("API_KEY", "demo-key-change-in-production")

def verify_api_key(request: Request):
    """Verify API key from header or query parameter."""
    key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
    if not key or key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return key

# Models
class EncodeRequest(BaseModel):
    text: str = Field(..., description="Text to encode to Base64")

class DecodeRequest(BaseModel):
    text: str = Field(..., description="Base64 string to decode")

class EncodeResponse(BaseModel):
    input: str
    output: str
    encoding: str = "base64"

class DecodeResponse(BaseModel):
    input: str
    output: str
    encoding: str = "base64"

# Endpoints
@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/encode", response_model=EncodeResponse)
async def encode(request: Request, body: EncodeRequest, api_key: str = Depends(verify_api_key)):
    """Encode text to Base64."""
    try:
        encoded = base64.b64encode(body.text.encode("utf-8")).decode("utf-8")
        return EncodeResponse(input=body.text, output=encoded)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/decode", response_model=DecodeResponse)
async def decode(request: Request, body: DecodeRequest, api_key: str = Depends(verify_api_key)):
    """Decode Base64 string to text."""
    try:
        text = body.text
        padding = 4 - len(text) % 4
        if padding != 4:
            text += "=" * padding
        decoded = base64.b64decode(text).decode("utf-8")
        return DecodeResponse(input=text, output=decoded)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Base64 input: {str(e)}")

@app.get("/encode")
async def encode_get(request: Request, text: str, api_key: str = Depends(verify_api_key)):
    """Encode text to Base64 via GET."""
    try:
        encoded = base64.b64encode(text.encode("utf-8")).decode("utf-8")
        return EncodeResponse(input=text, output=encoded)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/decode")
async def decode_get(request: Request, text: str, api_key: str = Depends(verify_api_key)):
    """Decode Base64 string to text via GET."""
    try:
        padding = 4 - len(text) % 4
        if padding != 4:
            text += "=" * padding
        decoded = base64.b64decode(text).decode("utf-8")
        return DecodeResponse(input=text, output=decoded)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Base64 input: {str(e)}")

# Handler for Vercel
handler = Mangum(app)