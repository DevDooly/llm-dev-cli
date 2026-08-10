import re
from pathlib import Path
from .base import BaseChecker, CheckResult

class SecretChecker(BaseChecker):
    """Checks for hardcoded API keys and unignored .env files."""

    SECRET_PATTERNS = [
        (re.compile(r"sk-[a-zA-Z0-9]{20,T3BlbkFJ[a-zA-Z0-9]{20,}"), "OpenAI API Key"),
        (re.compile(r"AIza[0-9A-Za-z-_]{35}"), "Google / Gemini API Key"),
        (re.compile(r"ghp_[a-zA-Z0-9]{36}"), "GitHub Personal Access Token"),
        (re.compile(r"ANTHROPIC_API_KEY\s*=\s*['\"][a-zA-Z0-9_-]{20,}['\"]"), "Anthropic Key")
    ]

    IGNORE_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "build", "dist"}

    def run_check(self, project_dir: Path) -> CheckResult:
        found_secrets = []
        gitignore_path = project_dir / ".gitignore"
        env_files = list(project_dir.glob("**/.env"))

        # 1. Check if .gitignore ignores .env
        if gitignore_path.exists():
            gitignore_content = gitignore_path.read_text(encoding="utf-8", errors="ignore")
            if ".env" not in gitignore_content:
                return CheckResult(
                    name="Secret Governance",
                    passed=False,
                    message=".gitignore 파일에 '.env'가 포함되어 있지 않습니다.",
                    suggestion=".gitignore에 '**/.env'를 추가하여 비밀번호/키 유출을 방어하세요.",
                    severity="ERROR"
                )

        # 2. Check for hardcoded API keys in source files
        for ext in ("*.py", "*.java", "*.js", "*.ts", "*.json", "*.yml", "*.yaml"):
            for file_path in project_dir.glob(f"**/{ext}"):
                if any(ignored in file_path.parts for ignored in self.IGNORE_DIRS):
                    continue
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    for pattern, secret_type in self.SECRET_PATTERNS:
                        if pattern.search(content):
                            found_secrets.append(f"{file_path.relative_to(project_dir)}: {secret_type}")
                except Exception:
                    pass

        if found_secrets:
            return CheckResult(
                name="Secret Governance",
                passed=False,
                message=f"소스코드 내 하드코딩된 API Key/비밀번호 발견 ({len(found_secrets)}건)",
                suggestion="발견된 파일: " + ", ".join(found_secrets[:3]) + " -> 환경변수 또는 Secret Manager를 사용하세요.",
                severity="ERROR"
            )

        return CheckResult(
            name="Secret Governance",
            passed=True,
            message="API Key 및 시크릿 하드코딩 없음 (정상 격리됨)"
        )
