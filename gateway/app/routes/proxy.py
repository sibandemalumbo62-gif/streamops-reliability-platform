from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response
import httpx

router = APIRouter()

# Service URLs
SERVICE_URLS = {
    "auth": "http://streamops-auth-service:8001",
    "integrity": "http://streamops-integrity-service:8006",
    "playback": "http://streamops-playback-service:8003",
    "recommendation": "http://streamops-recommendation-service:8004",
    "notification": "http://streamops-notification-service:8005",
    "catalog": "http://streamops-catalog-service:8002",
}

@router.api_route(
    "/api/v1/auth/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"]
)
async def proxy_auth(path: str, request: Request):
    return await proxy_request(
        "auth",
        f"auth/{path}",
        request
    )


@router.api_route("/api/v1/catalog/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_catalog(path: str, request: Request):
    return await proxy_request("catalog", path, request)


@router.api_route("/api/v1/playback/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_playback(path: str, request: Request):
    return await proxy_request("playback", path, request)


@router.api_route("/api/v1/recommendations/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_recommendation(path: str, request: Request):
    return await proxy_request("recommendation", path, request)


@router.api_route("/api/v1/notifications/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_notification(path: str, request: Request):
    return await proxy_request("notification", path, request)


@router.api_route(
    "/api/v1/events",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"]
)
async def proxy_events(request: Request):
    return await proxy_request(
        "integrity",
        "events",
        request
    )


@router.api_route(
    "/api/v1/events/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"]
)
async def proxy_events_path(path: str, request: Request):
    return await proxy_request(
        "integrity",
        f"events/{path}",
        request
    )
async def proxy_request(service: str, path: str, request: Request):
    """
    Proxy request to the appropriate service
    """
    service_url = SERVICE_URLS.get(service)
    if not service_url:
        raise HTTPException(status_code=502, detail=f"Service {service} not configured")
    
    target_url = f"{service_url}/{path}"
    
    # Get request body
    body = await request.body()
    
    # Forward headers (excluding hop-by-hop headers)
    headers = {
    key: value
    for key, value in request.headers.items()
    if key.lower() not in [
        "host",
        "content-length",
        "transfer-encoding",
        "connection"
    ]
}
    
    # Add user info if available from auth middleware
    if hasattr(request.state, "user_id"):
        headers["X-User-ID"] = request.state.user_id
    # Forward Request ID for distributed tracing
    if hasattr(request.state, "request_id"):
        headers["X-Request-ID"] = request.state.request_id

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params,
                timeout=30.0
            )

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type")
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Service unavailable: {str(exc)}"
            )
