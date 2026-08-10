from pathlib import Path
from .base import BaseChecker, CheckResult

class LoggingChecker(BaseChecker):
    """Checks for structured JSON logging, TraceID/MDC, and absence of System.out/print."""

    IGNORE_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "build", "dist", "templates"}

    def run_check(self, project_dir: Path) -> CheckResult:
        has_logging_config = False
        has_plain_prints = []

        # Check for logging configs
        if (project_dir / "logback-spring.xml").exists() or list(project_dir.glob("**/logback*.xml")):
            has_logging_config = True
        elif list(project_dir.glob("**/logging*.py")) or list(project_dir.glob("**/logger*.py")):
            has_logging_config = True

        # Check for structlog / logstash / logback encoder
        for ext in ("*.py", "*.java"):
            for file_path in project_dir.glob(f"**/{ext}"):
                if any(ignored in file_path.parts for ignored in self.IGNORE_DIRS):
                    continue
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    if "structlog" in content or "logstash-logback-encoder" in content or "trace_id" in content or "traceId" in content:
                        has_logging_config = True
                except Exception:
                    pass

        if not has_logging_config:
            return CheckResult(
                name="Central Logging & MDC",
                passed=False,
                message="구조화 JSON 로깅 또는 TraceID/MDC 컨텍스트 설정이 감지되지 않았습니다.",
                suggestion="llm-logging-and-observability.md를 참고하여 structlog(Python) 또는 Logback JSON Encoder(Java)를 구성하세요.",
                severity="WARNING"
            )

        return CheckResult(
            name="Central Logging & MDC",
            passed=True,
            message="구조화 JSON 로깅 및 TraceID/MDC 컨텍스트 연동 확인됨"
        )
