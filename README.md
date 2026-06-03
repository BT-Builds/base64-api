# Base64 API

Encode and decode Base64 data via simple HTTP endpoints.

## Endpoints

### GET /health
Health check endpoint (no auth required)
```bash
curl https://base64-api.vercel.app/health
```

### POST /encode
Encode text to Base64

**Headers:** `X-API-Key: free-demo-key`

**Body:**
```json
{
  "text": "Hello World",
  "encoding": "utf-8"
}
```

**cURL:**
```bash
curl -X POST https://base64-api-three.vercel.app/encode \
  -H "Content-Type: application/json" \
  -H "X-API-Key: free-demo-key" \
  -d '{"text":"Hello World"}'
```

### POST /decode
Decode Base64 to text

**Headers:** `X-API-Key: free-demo-key`

**Body:**
```json
{
  "base64": "SGVsbG8gV29ybGQ=",
  "encoding": "utf-8"
}
```

**cURL:**
```bash
curl -X POST https://base64-api-three.vercel.app/decode \
  -H "Content-Type: application/json" \
  -H "X-API-Key: free-demo-key" \
  -d '{"base64":"SGVsbG8gV29ybGQ="}'
```

## Authentication
All endpoints except /health require `X-API-Key` header. Default test key: `free-demo-key`

## Rate Limiting
60 requests per minute per API key.

## Use Cases
- Convert API payloads to Base64
- Decode configuration values
- Process authentication tokens
- Handle file uploads in APIs