import uuid
from typing import Callable, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .context import request_id_context, set_request_id


class RequestIDMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        header_name: str = "X-Request-ID",
        generator: Optional[Callable[[], str]] = None,
    ):
        super().__init__(app)
        self.header_name = header_name
        self.generator = generator or self._default_generator

    @staticmethod
    def _default_generator() -> str:
        return str(uuid.uuid4())

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        request_id = request.headers.get(self.header_name)
        if not request_id or not request_id.strip():
            request_id = self.generator()

        token = set_request_id(request_id)

        try:
            request.state.request_id = request_id
            response = await call_next(request)
            response.headers[self.header_name] = request_id
            return response
        finally:
            request_id_context.reset(token)
