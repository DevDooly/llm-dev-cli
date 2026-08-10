from abc import ABC, abstractmethod
from pathlib import Path
from typing import NamedTuple, List, Optional

class CheckResult(NamedTuple):
    name: str
    passed: bool
    message: str
    suggestion: Optional[str] = None
    severity: str = "ERROR" # ERROR, WARNING, INFO

class BaseChecker(ABC):
    @abstractmethod
    def run_check(self, project_dir: Path) -> CheckResult:
        """Run check against given project directory."""
        pass
