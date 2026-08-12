import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from ..config import STATIC_DIR
from ..checkers import ALL_CHECKERS
from ..commands.status import parse_checklists

def create_app(project_dir: Path) -> FastAPI:
    app = FastAPI(title="LLM Dev Governance Dashboard")

    @app.get("/api/diagnostics")
    async def get_diagnostics():
        results = []
        passed = 0
        for checker in ALL_CHECKERS:
            res = checker.run_check(project_dir)
            results.append({
                "name": res.name,
                "passed": res.passed,
                "message": res.message,
                "suggestion": res.suggestion,
                "severity": res.severity
            })
            if res.passed:
                passed += 1

        total = len(ALL_CHECKERS)
        score = int((passed / total) * 100)
        return {
            "score": score,
            "passed": passed,
            "total": total,
            "results": results
        }

    @app.get("/api/tasks")
    async def get_tasks():
        return parse_checklists(project_dir)

    @app.get("/api/doc")
    async def get_doc(name: str):
        # 후보 경로들 탐색
        candidates = [
            project_dir / "docs" / "llm-development" / name,
            project_dir / "docs" / name,
            project_dir / name,
        ]
        for p in candidates:
            if p.exists() and p.is_file():
                try:
                    content = p.read_text(encoding="utf-8")
                    return {"name": name, "content": content, "path": str(p.relative_to(project_dir))}
                except Exception as e:
                    return JSONResponse(status_code=500, content={"error": str(e)})
        return JSONResponse(status_code=404, content={"error": "Document not found"})

    @app.get("/")
    async def index():
        return FileResponse(STATIC_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    return app
