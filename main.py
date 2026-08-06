import logging
from datetime import date
from pathlib import Path as FilePath
from time import perf_counter

from fastapi import FastAPI, HTTPException, Path, Query, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from typing import Annotated

app = FastAPI()

LOG_DIR = FilePath("logs")
LOG_FILE = LOG_DIR / "application.log"
APP_LOGGER = logging.getLogger("book_api")


def setup_logging() -> None:
    LOG_DIR.mkdir(exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    file_handler: logging.FileHandler | None = None

    file_handler_exists = any(
        isinstance(handler, logging.FileHandler)
        and FilePath(getattr(handler, "baseFilename", "")).resolve() == LOG_FILE.resolve()
        for handler in root_logger.handlers
    )

    if not file_handler_exists:
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        root_logger.addHandler(file_handler)

    if file_handler is None:
        for handler in root_logger.handlers:
            if isinstance(handler, logging.FileHandler) and FilePath(
                getattr(handler, "baseFilename", "")
            ).resolve() == LOG_FILE.resolve():
                file_handler = handler
                break

    if file_handler is not None:
        for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.INFO)
            if not any(
                isinstance(handler, logging.FileHandler)
                and FilePath(getattr(handler, "baseFilename", "")).resolve()
                == LOG_FILE.resolve()
                for handler in logger.handlers
            ):
                logger.addHandler(file_handler)


@app.on_event("startup")
def configure_application_logging() -> None:
    setup_logging()
    APP_LOGGER.info("Application logging configured")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        APP_LOGGER.exception(
            "Unhandled error while processing %s %s",
            request.method,
            request.url.path,
        )
        raise

    elapsed_ms = (perf_counter() - start_time) * 1000
    APP_LOGGER.info(
        "%s %s -> %s in %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.get("/")
def read_root():
    return {"Hello": "Chijiuba Victory"}


@app.get("/logs/{day}", response_class=PlainTextResponse)
def read_logs_for_day(day: date):
    if not LOG_FILE.exists():
        raise HTTPException(status_code=404, detail="No logs have been recorded yet")

    day_prefix = day.isoformat()
    matching_lines: list[str] = []

    with LOG_FILE.open("r", encoding="utf-8") as log_file:
        for line in log_file:
            if line.startswith(day_prefix):
                matching_lines.append(line.rstrip("\n"))

    if not matching_lines:
        raise HTTPException(status_code=404, detail=f"No logs found for {day_prefix}")

    return "\n".join(matching_lines)


@app.get("/items/")
async def read_items(q: Annotated[list[str] | None, Query()] = None):
    query_items = {"q": q}
    return query_items


@app.get("/items/{item_id}")
async def read_item(item_id: Annotated[int, Path(max_length=50, min_length=3, title="Item ID")], q: Annotated[str | None, Query(max_length=50, min_length=3)] = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.model_dump()}