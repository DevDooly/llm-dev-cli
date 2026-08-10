import json
import logging
import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

try:
    import structlog
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
    logger = structlog.get_logger()
    _HAS_STRUCTLOG = True
except ImportError:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    _std_logger = logging.getLogger("llm-service")
    _HAS_STRUCTLOG = False

    class FallbackJsonLogger:
        def info(self, msg: str, **kwargs):
            payload = {"level": "INFO", "message": msg, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **kwargs}
            _std_logger.info(json.dumps(payload, ensure_ascii=False))

        def error(self, msg: str, **kwargs):
            payload = {"level": "ERROR", "message": msg, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **kwargs}
            _std_logger.error(json.dumps(payload, ensure_ascii=False))

    logger = FallbackJsonLogger()

class LlmLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Trace-Id", str(uuid.uuid4()))
        if _HAS_STRUCTLOG:
            structlog.contextvars.clear_contextvars()
            structlog.contextvars.bind_contextvars(
                trace_id=trace_id,
                service_name="llm-service",
                user_id=request.headers.get("X-User-Id", "anonymous")
            )
        
        start_time = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - start_time) * 1000)
        
        logger.info("HTTP Request Processed", trace_id=trace_id, http_status=response.status_code, duration_ms=duration_ms)
        return response
