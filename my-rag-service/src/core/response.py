from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel, Field
from fastapi import Request, status
from fastapi.responses import JSONResponse

T = TypeVar("T")

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    reason: str

class ApiError(BaseModel):
    code: str = Field(description="고유 에러 코드 (예: INVALID_INPUT_VALUE, LLM_QUOTA_EXCEEDED)")
    message: str = Field(description="사용자 친화적 에러 메시지")
    details: Optional[List[ErrorDetail]] = Field(default=None, description="세부 에러 항목 리스트")

class ApiResponse(BaseModel, Generic[T]):
    """
    LLM Dev 거버넌스 표준 API 응답 규격
    - 성공 (HTTP 200/201): { "success": true, "data": ..., "error": null }
    - 실패 (HTTP 4xx/5xx): { "success": false, "data": null, "error": { "code": ..., "message": ... } }
    """
    success: bool
    data: Optional[T] = None
    error: Optional[ApiError] = None

    @classmethod
    def ok(cls, data: T) -> "ApiResponse[T]":
        return cls(success=True, data=data, error=None)

    @classmethod
    def fail(cls, code: str, message: str, details: Optional[List[ErrorDetail]] = None) -> "ApiResponse[None]":
        return cls(
            success=False,
            data=None,
            error=ApiError(code=code, message=message, details=details)
        )

async def standard_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """전역 예외 발생 시 표준 API 에러 형식으로 래핑하여 반환"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    err_code = "INTERNAL_SERVER_ERROR"
    msg = "서버 내부 처리 중 오류가 발생하였습니다."

    if hasattr(exc, "status_code"):
        status_code = exc.status_code
    if hasattr(exc, "detail") and isinstance(exc.detail, str):
        msg = exc.detail

    response_payload = ApiResponse.fail(code=err_code, message=msg).model_dump()
    return JSONResponse(status_code=status_code, content=response_payload)
