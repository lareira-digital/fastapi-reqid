"""
Decorators for injecting HTTP clients with request ID.

Each decorator creates an HTTP client/session with the request ID
and stores it in request.state for easy access.
"""

import functools

from .context import get_request_id


def inject_httpx_requestid(func):
    """
    Inject httpx client with request ID into request.state.

    Access via: request.state.httpx_client

    Example:
        @app.get("/external")
        @inject_httpx_requestid
        async def call_external(request: Request):
            client = request.state.httpx_client
            response = await client.get("https://api.example.com")
            return response.json()
    """

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            import httpx
        except ImportError:
            raise ImportError("httpx not installed. Install with: pip install httpx")

        # Get request from kwargs
        request = kwargs.get("request")
        if not request:
            # Try to find it in args
            for arg in args:
                if hasattr(arg, "state"):
                    request = arg
                    break

        request_id = get_request_id()
        headers = {"X-Request-ID": request_id} if request_id else {}

        # Create client and store in request.state
        client = httpx.AsyncClient(headers=headers)
        if request:
            request.state.httpx_client = client

        try:
            return await func(*args, **kwargs)
        finally:
            await client.aclose()

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            import httpx
        except ImportError:
            raise ImportError("httpx not installed. Install with: pip install httpx")

        # Get request from kwargs
        request = kwargs.get("request")
        if not request:
            for arg in args:
                if hasattr(arg, "state"):
                    request = arg
                    break

        request_id = get_request_id()
        headers = {"X-Request-ID": request_id} if request_id else {}

        # Create client and store in request.state
        client = httpx.Client(headers=headers)
        if request:
            request.state.httpx_client = client

        try:
            return func(*args, **kwargs)
        finally:
            client.close()

    if functools.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


def inject_aiohttp_requestid(func):
    """
    Inject aiohttp session with request ID into request.state.

    Access via: request.state.aiohttp_session

    Example:
        @app.get("/external")
        @inject_aiohttp_requestid
        async def call_external(request: Request):
            session = request.state.aiohttp_session
            async with session.get("https://api.example.com") as resp:
                return await resp.json()
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            import aiohttp
        except ImportError:
            raise ImportError(
                "aiohttp not installed. Install with: pip install aiohttp"
            )

        # Get request from kwargs
        request = kwargs.get("request")
        if not request:
            for arg in args:
                if hasattr(arg, "state"):
                    request = arg
                    break

        request_id = get_request_id()
        headers = {"X-Request-ID": request_id} if request_id else {}

        # Create session and store in request.state
        session = aiohttp.ClientSession(headers=headers)
        if request:
            request.state.aiohttp_session = session

        try:
            return await func(*args, **kwargs)
        finally:
            await session.close()

    return wrapper


def inject_requests_requestid(func):
    """
    Inject requests session with request ID into request.state.

    Access via: request.state.requests_session

    Example:
        @app.get("/external")
        @inject_requests_requestid
        def call_external(request: Request):
            session = request.state.requests_session
            response = session.get("https://api.example.com")
            return response.json()
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            import requests
        except ImportError:
            raise ImportError(
                "requests not installed. Install with: pip install requests"
            )

        # Get request from kwargs
        request = kwargs.get("request")
        if not request:
            for arg in args:
                if hasattr(arg, "state"):
                    request = arg
                    break

        request_id = get_request_id()

        # Create session and store in request.state
        session = requests.Session()
        if request_id:
            session.headers["X-Request-ID"] = request_id
        if request:
            request.state.requests_session = session

        try:
            return func(*args, **kwargs)
        finally:
            session.close()

    return wrapper
