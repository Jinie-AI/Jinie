# API & Communication Reference

This document outlines the API contracts and communication methods between the frontend user interface and the local Python backend services.

## Overview
Communication between the frontend container and the backend service is established over localhost endpoints. The standard interface uses **REST APIs** for request-response flows and **WebSockets** for streaming/push events.

---

## REST Endpoints

### 1. System Health Check
Check if the local Python backend server is running and healthy.

- **URL:** `/api/health`
- **Method:** `GET`
- **Headers:** None
- **Response:**
  - **Status Code:** `200 OK`
  - **Body (JSON):**
    ```json
    {
      "status": "healthy",
      "version": "1.0.0",
      "timestamp": "2026-06-16T13:54:00Z"
    }
    ```

### 2. Run Task Execution
Trigger a backend process or run automation.

- **URL:** `/api/execute`
- **Method:** `POST`
- **Headers:**
  - `Content-Type: application/json`
- **Request Body (JSON):**
  ```json
  {
    "task_id": "unique-task-string",
    "parameters": {
      "mode": "default",
      "options": {}
    }
  }
  ```
- **Response:**
  - **Status Code:** `202 Accepted`
  - **Body (JSON):**
    ```json
    {
      "status": "started",
      "job_id": "job-uuid-12345"
    }
    ```

---

## WebSocket Channels

For live progress tracking and stdout/stderr streaming, the frontend subscribes to WebSocket channels.

### WebSocket Connection
- **URL:** `ws://127.0.0.1:8000/ws/events`

### Event Payloads
Every WebSocket event payload follows the structure below:
```json
{
  "event": "task_progress",
  "job_id": "job-uuid-12345",
  "data": {
    "percentage": 45,
    "log_message": "Processing code block references..."
  }
}
```
