from fastapi import Request, Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)  # noqa
import asyncio


class GlobalTimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, timeout=0.5):
        super().__init__(app)
        self.timeout = timeout

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            response = await asyncio.wait_for(
                call_next(request), timeout=self.timeout
            )  # noqa
            return response
        except asyncio.TimeoutError:
            return Response(
                f"Server timeout of {self.timeout} seconds expired",
                status_code=500,  # noqa
            )
