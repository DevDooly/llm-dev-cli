import docker
import os
import tempfile
from typing import Dict, Any

class SafeCodeSandbox:
    def __init__(self, image_name: str = "python:3.11-alpine"):
        self.client = docker.from_env()
        self.image_name = image_name

    def execute_python_code(self, code_snippet: str, timeout_sec: int = 5) -> Dict[str, Any]:
        with tempfile.TemporaryDirectory() as temp_dir:
            script_path = os.path.join(temp_dir, "script.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code_snippet)

            try:
                container = self.client.containers.run(
                    image=self.image_name,
                    command=["python", "/sandbox/script.py"],
                    volumes={temp_dir: {"bind": "/sandbox", "mode": "ro"}},
                    network_mode="none",
                    mem_limit="256m",
                    cpu_period=100000,
                    cpu_quota=50000,
                    read_only=True,
                    tmpfs={"/tmp": "size=16m,noexec"},
                    user="10001:10001",
                    detach=True,
                    stdout=True,
                    stderr=True,
                    remove=False
                )

                try:
                    result = container.wait(timeout=timeout_sec)
                    exit_code = result.get("StatusCode", 1)
                    logs = container.logs().decode("utf-8")
                except Exception:
                    container.kill()
                    return {"success": False, "exit_code": -1, "output": f"Execution timed out after {timeout_sec}s."}
                finally:
                    container.remove(force=True)

                return {"success": (exit_code == 0), "exit_code": exit_code, "output": logs}

            except Exception as e:
                return {"success": False, "exit_code": -1, "output": f"Sandbox error: {str(e)}"}
