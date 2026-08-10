from pathlib import Path
from .base import BaseChecker, CheckResult

class ResponseSchemaChecker(BaseChecker):
    """Checks for standard API response schema {success, data, error}."""

    IGNORE_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "templates"}

    def run_check(self, project_dir: Path) -> CheckResult:
        has_standard_dto = False

        for ext in ("*.py", "*.java"):
            for file_path in project_dir.glob(f"**/{ext}"):
                if any(ignored in file_path.parts for ignored in self.IGNORE_DIRS):
                    continue
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    if "success" in content and "data" in content and "error" in content:
                        has_standard_dto = True
                        break
                except Exception:
                    pass

        if not has_standard_dto:
            return CheckResult(
                name="API Response Format",
                passed=False,
                message="표준 API 응답 포맷({success, data, error}) DTO가 감지되지 않았습니다.",
                suggestion="llm-guidelines.md Section 3.3의 ApiResponse 표준 스키마를 적용하세요.",
                severity="WARNING"
            )

        return CheckResult(
            name="API Response Format",
            passed=True,
            message="표준 API 응답 구조({success, data, error}) 적용 확인됨"
        )
