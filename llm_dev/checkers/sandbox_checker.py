from pathlib import Path
from .base import BaseChecker, CheckResult

class SandboxChecker(BaseChecker):
    """Checks for Docker Sandbox / Isolated Code Execution implementation when agents/tools are used."""

    IGNORE_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "templates"}

    def run_check(self, project_dir: Path) -> CheckResult:
        uses_exec = False
        has_sandbox = False

        for ext in ("*.py", "*.java", "*.ts", "*.js"):
            for file_path in project_dir.glob(f"**/{ext}"):
                if any(ignored in file_path.parts for ignored in self.IGNORE_DIRS):
                    continue
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    if "subprocess" in content or "exec(" in content or "Runtime.getRuntime().exec" in content or "ProcessBuilder" in content:
                        uses_exec = True
                    if "network_mode" in content and "none" in content:
                        has_sandbox = True
                    if "SafeCodeSandbox" in content or "sandbox" in content.lower():
                        has_sandbox = True
                except Exception:
                    pass

        if uses_exec and not has_sandbox:
            return CheckResult(
                name="Agent Code Sandbox",
                passed=False,
                message="코드 실행기능(exec/subprocess)이 감지되었으나 Docker Sandbox 격리 보호가 미흡합니다.",
                suggestion="llm-docker-and-sandbox.md를 참고하여 network_mode='none' 및 자원 상한이 지정된 Docker 샌드박스를 적용하세요.",
                severity="ERROR"
            )

        if has_sandbox:
            return CheckResult(
                name="Agent Code Sandbox",
                passed=True,
                message="Docker 샌드박스 격리 실행 환경 확인됨"
            )

        return CheckResult(
            name="Agent Code Sandbox",
            passed=True,
            message="외부 코드 실행 없는 일반 파이프라인 (N/A)",
            severity="INFO"
        )
