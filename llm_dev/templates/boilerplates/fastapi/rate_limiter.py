import time
import redis
from fastapi import HTTPException, status

class LlmRateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def check_and_consume_token_quota(
        self, 
        user_id: str, 
        estimated_tokens: int, 
        rpm_limit: int = 20, 
        tpm_limit: int = 40000, 
        monthly_token_budget: int = 500000
    ):
        current_minute = int(time.time() // 60)
        current_month = time.strftime("%Y-%m")
        
        rpm_key = f"rate:rpm:{user_id}:{current_minute}"
        tpm_key = f"rate:tpm:{user_id}:{current_minute}"
        budget_key = f"quota:monthly:{user_id}:{current_month}"

        pipe = self.redis.pipeline()
        pipe.incr(rpm_key)
        pipe.expire(rpm_key, 65)
        pipe.incrby(tpm_key, estimated_tokens)
        pipe.expire(tpm_key, 65)
        pipe.get(budget_key)
        
        current_rpm, _, current_tpm, _, current_monthly_usage = pipe.execute()
        current_monthly_tokens = int(current_monthly_usage or 0)

        if current_rpm > rpm_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"분당 요청 한도({rpm_limit} RPM)를 초과하였습니다."
            )

        if current_tpm > tpm_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"분당 토큰 한도({tpm_limit} TPM)를 초과하였습니다."
            )

        if current_monthly_tokens + estimated_tokens > monthly_token_budget:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="월간 LLM 토큰 예산을 소진하였습니다."
            )

        self.redis.incrby(budget_key, estimated_tokens)
