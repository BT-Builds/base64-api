# Base64 Encoder/Decoder API

Encode and decode Base64 strings with simple HTTP API calls. No libraries needed.

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check (no auth required) |
| `/encode` | POST | Encode text to Base64 |
| `/encode` | GET | Encode text to Base64 via `text` parameter |
| `/decode` | POST | Decode Base64 to text |
| `/decode` | GET | Decode Base64 to text via `text` parameter |

## Authentication

All endpoints except `/health` require API key via:
- Header: `X-API-Key: your-key`
- Query param: `?api_key=your-key`

Default demo key: `demo-key-change-in-production`

## Examples

```bash
# Encode (GET)
curl "https://<slug>.vercel.app/encode?text=hello&api_key=demo-key-change-in-production"

# Encode (POST)
curl -X POST "https://<slug>.vercel.app/encode" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key-change-in-production" \
  -d '{"text": "hello world"}'

# Decode (GET)
curl "https://<slug>.vercel.app/decode?text=aGVsbG8=&api_key=demo-key-change-in-production"

# Decode (POST)
curl -X POST "https://<slug>.vercel.app/decode" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key-change-in-production" \
  -d '{"text": "aGVsbG8gd29ybGQ="}'
```

## Response Format

```json
{
  "input": "original text",
  "output": "encoded/decoded result",
  "encoding": "base64"
}
```

## Pricing Suggestion

- $9/month per 10,000 requests
- List on RapidAPI or self-host for developers