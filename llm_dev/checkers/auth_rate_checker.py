from pathlib import Path
from .base import BaseChecker, CheckResult

class AuthRateChecker(BaseChecker):
    """Checks for Rate Limiting / Token Quotas and PII Masking."""

    IGNORE_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "templates"}

    def run_check(self, project_dir: Path) -> CheckResult:
        has_rate_limiter = False
        has_pii_masker = False

        for ext in ("*.py", "*.java"):
            for file_path in project_dir.glob(f"**/{ext}"):
                if any(ignored in file_path.parts for ignored in self.IGNORE_DIRS):
                    continue
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    if "rate" in content.lower() and ("tpm" in content.lower() or "rpm" in content.lower() or "limiter" in content.lower()):
                        has_rate_limiter = True
                    if "pii" in content.lower() or "mask" in content.lower() or "presidio" in content.lower():
                        has_pii_masker = True
                except Exception:
                    pass

        issues = []
        suggestions = []

        if not has_rate_limiter:
            issues.append("Rate Limiter(RPM/TPM) 미구성")
            suggestions.append("Redis Token Bucket 기반 Rate Limiter 적용")
        if not has_pii_masker:
            issues.append("PII 마스킹 필터 미구성")
            suggestions.append("PiiMasker 모듈 적용")

        if issues:
            return CheckResult(
                name="Auth, Quotas & PII",
                passed=False,
                message="보안 및 비용 제어 미흡: " + ", ".join(issues),
                suggestion=" -> ".join(suggestions) + " (참조: llm-auth-and-security.md)",
                severity="WARNING"
            )

        return CheckResult(
            name="Auth, Quotas & PII",
            passed=True,
            message="Rate Limiter 및 PII 마스킹 필터 확인됨"
        )
