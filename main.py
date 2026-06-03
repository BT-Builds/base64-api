import base64
import re
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from mangum import Mangum

app = FastAPI(
    title="Base64 API",
    description="Encode and decode Base64 data via simple HTTP endpoints",
    version="1.0.0"
)

handler = Mangum(app)

# Simple API key auth
VALID_API_KEYS = ["free-demo-key", "demo-key", "test-key"]  # Add your keys here

def verify_api_key(x_api_key: str = None):
    if not x_api_key or x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key

# Rate limiting (simple in-memory)
rate_limit_store = {}

def rate_limit(api_key: str = Depends(verify_api_key)):
    from datetime import datetime, timedelta
    now = datetime.now()
    key_calls = rate_limit_store.get(api_key, [])
    # Keep only last minute's calls
    key_calls = [t for t in key_calls if now - t < timedelta(minutes=1)]
    if len(key_calls) > 60:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    key_calls.append(now)
    rate_limit_store[api_key] = key_calls
    return api_key

class EncodeRequest(BaseModel):
    text: str
    encoding: str = "utf-8"

class DecodeRequest(BaseModel):
    base64: str
    encoding: str = "utf-8"

class EncodeResponse(BaseModel):
    input: str
    output: str
    charset: str

class DecodeResponse(BaseModel):
    input: str
    output: str
    charset: str

class ErrorResponse(BaseModel):
    error: str
    detail: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "base64-api"}

@app.post("/encode", dependencies=[Depends(rate_limit)])
def encode(req: EncodeRequest):
    try:
        encoded = base64.b64encode(req.text.encode(req.encoding)).decode('utf-8')
        return EncodeResponse(input=req.text, output=encoded, charset=req.encoding)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Encoding failed: {str(e)}")

@app.post("/decode", dependencies=[Depends(rate_limit)])
def decode(req: DecodeRequest):
    try:
        # Add padding if needed
        padding = 4 - len(req.base64) % 4
        if padding != 4:
            req.base64 += '=' * padding
        decoded = base64.b64decode(req.base64).decode(req.encoding)
        return DecodeResponse(input=req.base64, output=decoded, charset=req.encoding)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Decoding failed: {str(e)}")

@app.get("/", include_in_schema=False)
def root():
    return {"message": "Base64 API - Use /encode and /decode endpoints with POST"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)