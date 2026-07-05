# UAMP API Documentation

## Overview

UAMP exposes a RESTful API with JSON payloads and a real-time WebSocket API for context synchronization.

### Base URL

```
http://localhost:8080/api/v1
```

### Authentication

All endpoints require an API key in the header:
```
Authorization: Bearer <your-api-key>
```

---

## Context API

### Create Context
```http
POST /api/v1/context
```

**Request Body:**
```json
{
  "id": "uuid-v4",
  "tool": "claude-code",
  "content": "Context content here",
  "metadata": {
    "project": "my-project",
    "timestamp": 1712345678000,
    "tags": ["typescript", "api"],
    "importance": 70
  },
  "relationships": {
    "parents": [],
    "children": [],
    "references": []
  }
}
```

**Response:** 201 Created
```json
{
  "success": true,
  "data": { /* MemoryNode */ },
  "timestamp": 1712345678000
}
```

### Get Context
```http
GET /api/v1/context/:id
```

**Response:** 200 OK

### Update Context
```http
PUT /api/v1/context/:id
```

**Request Body:** Partial context fields

### Delete Context
```http
DELETE /api/v1/context/:id
```

### List Contexts
```http
GET /api/v1/context?tool=claude-code&limit=50&offset=0
```

---

## Search API

### Semantic Search
```http
POST /api/v1/search/semantic
```

**Request Body:**
```json
{
  "query": "How to implement authentication",
  "limit": 10,
  "tool": "claude-code"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "query": "How to implement authentication",
    "results": [
      {
        "id": "uuid",
        "tool": "claude-code",
        "content": "Context preview...",
        "metadata": {},
        "similarity": 0.85
      }
    ],
    "count": 1
  }
}
```

### Temporal Search
```http
POST /api/v1/search/temporal
```

**Request Body:**
```json
{
  "startTime": 1710000000000,
  "endTime": 1710086400000,
  "tool": "cursor"
}
```

---

## Sync API

### Push Context
```http
POST /api/v1/sync/push
```

**Request Body:**
```json
{
  "context": { /* Full Context object */ }
}
```

### Pull Context
```http
POST /api/v1/sync/pull
```

**Request Body:**
```json
{
  "tool": "cursor",
  "query": "authentication implementation"
}
```

### Get Sync Status
```http
GET /api/v1/sync/status/:tool
```

### Resolve Conflicts
```http
POST /api/v1/sync/resolve
```

**Request Body:**
```json
{
  "contexts": [/* Array of conflicting Contexts */]
}
```

---

## Plugin API

### List Plugins
```http
GET /api/v1/plugins
```

### Get Plugin Details
```http
GET /api/v1/plugins/:name
```

### Reload Plugin
```http
POST /api/v1/plugins/:name/reload
```

---

## WebSocket API

### Connection
```
ws://localhost:8081
```

### Events

#### Client → Server
```json
{
  "type": "subscribe",
  "tool": "claude-code"
}
```

#### Server → Client
```json
{
  "type": "context_synced",
  "tool": "claude-code",
  "data": {
    "contextId": "uuid",
    "context": {},
    "metadata": {}
  },
  "timestamp": 1712345678000
}
```

### Error Events
```json
{
  "type": "error",
  "message": "Error description",
  "timestamp": 1712345678000
}
```

---

## Error Codes

| Status | Code | Description |
|--------|------|-------------|
| 400 | BAD_REQUEST | Invalid request body or parameters |
| 401 | UNAUTHORIZED | Invalid or missing API key |
| 404 | NOT_FOUND | Resource not found |
| 429 | RATE_LIMITED | Too many requests |
| 500 | INTERNAL_ERROR | Server error |

---

## Rate Limiting

- Default: 100 requests per minute
- Headers: `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Pagination

- Standard query params: `limit` (default 50, max 100), `offset` (default 0)
- Response includes total count when applicable

## Versioning

Current API version: `v1`. Breaking changes will be introduced in new versions while maintaining backward compatibility for at least 6 months.