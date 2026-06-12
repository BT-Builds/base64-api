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
# === BT Builds Standard Middleware (auto-injected) ===
from fastapi.middleware.cors import CORSMiddleware as _BTCors
app.add_middleware(_BTCors, allow_origins=["*"], allow_methods=["*"],
    allow_headers=["*"], expose_headers=["X-RateLimit-Limit","X-RateLimit-Remaining","X-RateLimit-Reset"])

@app.middleware("http")
async def _bt_add_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Powered-By"] = "btbuilds"
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


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

# === Bulk request/response models ===
class BulkEncodeItem(BaseModel):
    text: str
    encoding: str = "utf-8"

class BulkDecodeItem(BaseModel):
    base64: str
    encoding: str = "utf-8"

class BulkEncodeRequest(BaseModel):
    items: list[BulkEncodeItem]

class BulkDecodeRequest(BaseModel):
    items: list[BulkDecodeItem]

class BulkResult(BaseModel):
    input: str
    output: str | None = None
    error: str | None = None

class BulkEncodeResponse(BaseModel):
    results: list[BulkResult]
    total: int
    successful: int

class BulkDecodeResponse(BaseModel):
    results: list[BulkResult]
    total: int
    successful: int

# === Helper functions ===
def encode_single(text: str, encoding: str = "utf-8") -> tuple[str, str | None]:
    """Encode text to base64. Returns (output, error) tuple."""
    try:
        encoded = base64.b64encode(text.encode(encoding)).decode('utf-8')
        return encoded, None
    except Exception as e:
        return "", f"Encoding failed: {str(e)}"

def decode_single(base64_str: str, encoding: str = "utf-8") -> tuple[str, str | None]:
    """Decode base64 to text. Returns (output, error) tuple."""
    try:
        # Add padding if needed
        padding = 4 - len(base64_str) % 4
        if padding != 4:
            base64_str += '=' * padding
        decoded = base64.b64decode(base64_str).decode(encoding)
        return decoded, None
    except Exception as e:
        return "", f"Decoding failed: {str(e)}"

@app.get("/health")
def health():
    return {"status": "ok", "service": "base64-api"}

@app.post("/encode", dependencies=[Depends(rate_limit)])
def encode(req: EncodeRequest):
    output, error = encode_single(req.text, req.encoding)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return EncodeResponse(input=req.text, output=output, charset=req.encoding)

@app.post("/decode", dependencies=[Depends(rate_limit)])
def decode(req: DecodeRequest):
    output, error = decode_single(req.base64, req.encoding)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return DecodeResponse(input=req.base64, output=output, charset=req.encoding)

@app.post("/bulk/encode", dependencies=[Depends(rate_limit)])
def bulk_encode(req: BulkEncodeRequest):
    if len(req.items) > 1000:
        raise HTTPException(status_code=400, detail="Maximum 1000 items per request")

    results = []
    successful = 0
    for item in req.items:
        output, error = encode_single(item.text, item.encoding)
        if error:
            results.append(BulkResult(input=item.text, error=error))
        else:
            results.append(BulkResult(input=item.text, output=output))
            successful += 1

    return BulkEncodeResponse(results=results, total=len(req.items), successful=successful)

@app.post("/bulk/decode", dependencies=[Depends(rate_limit)])
def bulk_decode(req: BulkDecodeRequest):
    if len(req.items) > 1000:
        raise HTTPException(status_code=400, detail="Maximum 1000 items per request")

    results = []
    successful = 0
    for item in req.items:
        output, error = decode_single(item.base64, item.encoding)
        if error:
            results.append(BulkResult(input=item.base64, error=error))
        else:
            results.append(BulkResult(input=item.base64, output=output))
            successful += 1

    return BulkDecodeResponse(results=results, total=len(req.items), successful=successful)

@app.get("/", include_in_schema=False)
def root():
    return {"message": "Base64 API - Use /encode and /decode endpoints with POST"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)