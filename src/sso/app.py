import importlib
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import NewType

from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from sso.exceptions import ServiceError
from sso.settings import SQLALCHEMY_DATABASE_URL

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Start FastAPI and dynamically load endpoint modules."""
    python_files = list((Path(__file__).parent / "endpoints").glob("*.py"))
    for file in python_files:
        importlib.import_module(f"sso.endpoints.{file.stem}")
    logger.warning(f"Note:     Loaded {len(python_files)} endpoints")
    yield


ServiceErrorSubclass = NewType("ServiceErrorSubclass", ServiceError)


async def unicorn_exception_handler(request: Request,
                                    exc: ServiceErrorSubclass) -> JSONResponse:
    """Handle ServiceError exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": str(exc)},
    )


app = FastAPI(
    exception_handlers={ServiceError: unicorn_exception_handler},
    lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"])
app.add_middleware(DBSessionMiddleware, db_url=SQLALCHEMY_DATABASE_URL)
app.add_middleware(GZipMiddleware, minimum_size=1000)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
