# FastAPI Request ID

A FastAPI middleware for request ID propagation and tracing across microservices.

## Quick Start

### 1. Add Middleware

```python
from fastapi import FastAPI
from fastapi_reqid import RequestIDMiddleware

app = FastAPI()

# Add middleware with default settings
app.add_middleware(RequestIDMiddleware)

# Or customize it
app.add_middleware(
    RequestIDMiddleware,
    header_name="X-Correlation-ID",  # Custom header name
    generator=lambda: str(uuid.uuid4())  # Custom ID generator
)
```

### 2. Access Request ID

```python
from fastapi import Request
from fastapi_reqid import get_request_id

@app.get("/")
async def root(request: Request):
    # Access via request.state
    request_id = request.state.request_id

    # Or use the context helper
    request_id = get_request_id()

    return {"request_id": request_id}
```

## HTTP Client Decorators

Automatically inject request IDs into outgoing HTTP requests.

### httpx

```python
from fastapi import Request
from fastapi_reqid import inject_httpx_requestid

@app.get("/external")
@inject_httpx_requestid
async def call_external(request: Request):
    client = request.state.httpx_client
    response = await client.get("https://api.example.com")
    return response.json()
```

### aiohttp

```python
from fastapi import Request
from fastapi_reqid import inject_aiohttp_requestid

@app.get("/external")
@inject_aiohttp_requestid
async def call_external(request: Request):
    session = request.state.aiohttp_session
    async with session.get("https://api.example.com") as resp:
        return await resp.json()
```

### requests

```python
from fastapi import Request
from fastapi_reqid import inject_requests_requestid

@app.get("/external")
@inject_requests_requestid
def call_external(request: Request):
    session = request.state.requests_session
    response = session.get("https://api.example.com")
    return response.json()
```

## Manual Request ID Management

Use these functions to manually get or set request IDs:

```python
from fastapi_reqid import get_request_id, set_request_id, request_id_context

# Get current request ID
request_id = get_request_id()

# Set request ID manually
token = set_request_id("custom-request-id")
try:
    # Do work with this request ID
    pass
finally:
    # Reset to previous value
    request_id_context.reset(token)
```

## Building and Publishing

### Building the Library

This project uses [uv](https://github.com/astral-sh/uv) for building. To build the distribution packages:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Build the package (creates wheel and source distribution)
uv build
```

This will create two files in the `dist/` directory:
- `fastapi_reqid-{version}-py3-none-any.whl` - Python wheel
- `fastapi_reqid-{version}.tar.gz` - Source distribution

### Publishing to PyPI

#### Test on TestPyPI First (Recommended)

Before publishing to the main PyPI, test your package on TestPyPI:

```bash
# Publish to TestPyPI
uv publish --publish-url https://test.pypi.org/legacy/
```

You'll need a TestPyPI account and API token from [test.pypi.org](https://test.pypi.org).

#### Publish to PyPI

Once you've verified the package works correctly:

```bash
# Publish to PyPI
uv publish
```

You'll need a PyPI account and API token from [pypi.org](https://pypi.org).

### Development Setup

To set up a development environment:

```bash
# Create virtual environment
uv venv

# Install package in editable mode with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest
```

## How It Works

1. The middleware extracts the request ID from incoming headers (default: `X-Request-ID`)
2. If no request ID is found, it generates one using UUID v4
3. The request ID is stored in both `request.state` and a context variable
4. The request ID is automatically added to response headers
5. Context is automatically cleaned up after each request

## License

MIT License - see LICENSE file for details
