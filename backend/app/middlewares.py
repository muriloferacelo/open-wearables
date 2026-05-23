from collections.abc import Callable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


class OptionsMiddleware:
    """Pure ASGI middleware that short-circuits OPTIONS requests before FastAPI
    validation runs.  BaseHTTPMiddleware is a high-level wrapper that sits
    *inside* the Starlette/FastAPI routing layer, so validation errors are
    raised before it can intercept them.  Wrapping the app at the raw ASGI
    level guarantees the check happens first."""

    def __init__(self, app: Callable) -> None:
        self.app = app

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        if scope["type"] == "http" and scope.get("method") == "OPTIONS":
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [],
                }
            )
            await send({"type": "http.response.body", "body": b""})
            return
        await self.app(scope, receive, send)


def add_cors_middleware(app: FastAPI) -> None:
    cors_origins = [str(origin).rstrip("/") for origin in settings.cors_origins]
    if settings.cors_allow_all:
        cors_origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
