# Book API (FastAPI)

A lightweight FastAPI project that demonstrates:

- Basic REST-style endpoints
- Path and query parameter validation with `Annotated`
- Pydantic request body modeling
- Automatic request/response logging to a local file
- A dedicated endpoint to retrieve logs for a specific day

This project is suitable as a learning scaffold for FastAPI fundamentals and as a starter pattern for adding operational logging to small services.

## What This Application Does

The application exposes endpoints for:

- Returning a simple root message
- Reading item query inputs
- Fetching a single item by ID with optional query parameters
- Creating and updating item payloads
- Reading application logs by calendar day

At startup, it configures logging so both app-level logs and Uvicorn logs are written to:

- `logs/application.log`

Each HTTP request is logged with:

- HTTP method
- URL path
- Response status code
- Request duration in milliseconds

Unhandled exceptions in request handling are also logged with stack traces.

## Tech Stack

- Python 3.13
- FastAPI
- Uvicorn (`standard` extras)
- Pydantic
- Pipenv for dependency management

## Project Structure

```text
book-api/
  main.py
  Pipfile
  README.md
  logs/
    application.log   # created automatically after startup/first logs
```

## Installation and Setup

### 1. Install dependencies

```bash
pipenv install
```

### 2. Run the API server

```bash
pipenv run uvicorn main:app --reload
```

By default, the server runs at:

- `http://127.0.0.1:8000`

### 3. Open interactive docs

FastAPI automatically generates API docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Data Model

### `Item`

The request body for create/update item endpoints:

- `name: str` (required)
- `description: str | None` (optional)
- `price: float` (required)
- `tax: float | None` (optional)

When `tax` is provided during item creation, the API includes `price_with_tax` in the response.

## API Endpoints

### 1) Root

- **Method:** `GET`
- **Path:** `/`
- **Purpose:** Basic health-style greeting endpoint.

Example response:

```json
{
  "Hello": "Chijiuba Victory"
}
```

### 2) Read Items Query

- **Method:** `GET`
- **Path:** `/items/`
- **Purpose:** Returns query list values received via `q`.

Query parameter:

- `q: list[str] | None` (optional, repeatable)

Example:

`GET /items/?q=book&q=python`

Example response:

```json
{
  "q": ["book", "python"]
}
```

### 3) Read Single Item

- **Method:** `GET`
- **Path:** `/items/{item_id}`
- **Purpose:** Returns item details for an `item_id` with optional query and response shape control.

Parameters:

- `item_id` (path, integer)
- `q` (query, optional string)
- `short` (query, optional boolean, default `false`)

Behavior:

- If `q` is provided, it is included in the response.
- If `short=false`, a long description is included.
- If `short=true`, description is omitted.

Example:

`GET /items/123?q=sample&short=false`

### 4) Create Item

- **Method:** `POST`
- **Path:** `/items/`
- **Purpose:** Accepts an `Item` body and returns it, adding `price_with_tax` when tax is present.

Example request body:

```json
{
  "name": "FastAPI Book",
  "description": "Backend guide",
  "price": 29.99,
  "tax": 2.5
}
```

Example response:

```json
{
  "name": "FastAPI Book",
  "description": "Backend guide",
  "price": 29.99,
  "tax": 2.5,
  "price_with_tax": 32.49
}
```

### 5) Update Item

- **Method:** `PUT`
- **Path:** `/items/{item_id}`
- **Purpose:** Returns merged response containing `item_id` and updated `Item` payload.

Example:

`PUT /items/123`

### 6) Get Logs by Day

- **Method:** `GET`
- **Path:** `/logs/{day}`
- **Response type:** `text/plain`
- **Purpose:** Returns all log lines for the supplied date.

Path parameter:

- `day` in ISO date format: `YYYY-MM-DD`

Example:

`GET /logs/2026-08-06`

Success behavior:

- Returns newline-separated log entries from `logs/application.log` whose timestamp starts with the requested date.

Error behavior:

- `404` if no log file exists yet
- `404` if log file exists but contains no lines for that date

## Logging Details

Logging is configured on startup and writes to:

- `logs/application.log`

Log format:

```text
YYYY-MM-DD HH:MM:SS,mmm | LEVEL | LOGGER_NAME | MESSAGE
```

What gets logged:

- Application startup message
- Per-request access log from middleware (`METHOD PATH -> STATUS in N ms`)
- Uvicorn runtime/access logs
- Unhandled exceptions in request processing

## Validation and Notes

- FastAPI/Pydantic perform request parsing and validation automatically.
- Date validation for `/logs/{day}` is strict (`YYYY-MM-DD`), handled by FastAPI using Python `date` typing.
- If you run with `--reload`, code changes are picked up automatically.

## Example cURL Commands

```bash
curl http://127.0.0.1:8000/
curl "http://127.0.0.1:8000/items/?q=book&q=python"
curl "http://127.0.0.1:8000/items/123?q=example&short=true"
```

```bash
curl -X POST http://127.0.0.1:8000/items/ \
  -H "Content-Type: application/json" \
  -d '{"name":"FastAPI Book","price":29.99,"tax":2.5}'
```

```bash
curl -X PUT http://127.0.0.1:8000/items/123 \
  -H "Content-Type: application/json" \
  -d '{"name":"Updated Book","price":39.99}'
```

```bash
curl http://127.0.0.1:8000/logs/2026-08-06
```

## Future Improvements (Optional)

- Add persistent storage (SQLite/PostgreSQL)
- Add unit and integration tests with `pytest`
- Add log rotation (daily/size-based)
- Return paginated logs or JSON log query support
- Add authentication/authorization for log access

## License

No license file is currently included. Add one if you plan to distribute this project.
