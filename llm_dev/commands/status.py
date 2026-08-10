import re
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..config import DEFAULT_DOCS_TARGET

console = Console()

CHECKED_RE = re.compile(r"^\s*-\s*\[x\]\s*(.+)$", re.IGNORECASE | re.MULTILINE)
UNCHECKED_RE = re.compile(r"^\s*-\s*\[\s*\]\s*(.+)$", re.MULTILINE)

def parse_checklists(project_dir: Path):
    doc_paths = set()
    for pattern in (
        f"{DEFAULT_DOCS_TARGET}/*.md",
        "llm-development/*.md",
        "docs/*.md",
        "*.md"
    ):
        doc_paths.update(project_dir.glob(pattern))

    summary = []
    total_checked = 0
    total_unchecked = 0

    for doc_path in sorted(doc_paths):
        # Skip node_modules / venv / build
        if any(p in doc_path.parts for p in ("node_modules", ".venv", "venv", "build", "dist")):
            continue
        try:
            content = doc_path.read_text(encoding="utf-8", errors="ignore")
            checked = CHECKED_RE.findall(content)
            unchecked = UNCHECKED_RE.findall(content)

            total_items = len(checked) + len(unchecked)
            if total_items > 0:
                summary.append({
                    "file": str(doc_path.relative_to(project_dir)),
                    "checked": len(checked),
                    "unchecked": len(unchecked),
                    "total": total_items,
                    "percent": int((len(checked) / total_items) * 100)
                })
                total_checked += len(checked)
                total_unchecked += len(unchecked)
        except Exception:
            pass

    grand_total = total_checked + total_unchecked
    grand_percent = int((total_checked / grand_total) * 100) if grand_total > 0 else 0

    return {
        "files": summary,
        "total_checked": total_checked,
        "total_unchecked": total_unchecked,
        "grand_total": grand_total,
        "grand_percent": grand_percent
    }

def run_status(project_dir: Path):
    project_dir = project_dir.resolve()
    data = parse_checklists(project_dir)

    console.print(Panel.fit(
        f"[bold cyan]📊 LLM Development Checklist & Lifecycle Progress[/bold cyan]\n"
        f"Scanning: [green]{project_dir}[/green]",
        title="[bold blue]Status Overview[/bold blue]"
    ))

    if not data["files"]:
        console.print("[yellow]마크다운 체크리스트 문서를 찾을 수 없습니다. (먼저 'llm-dev init'을 실행하세요)[/yellow]\n")
        return

    table = Table(title="[bold]Document Checklist Progress[/bold]", show_header=True, header_style="bold magenta")
    table.add_column("Document", style="cyan", width=38)
    table.add_column("Done / Total", justify="right", width=15)
    table.add_column("Progress Bar", width=25)
    table.add_column("Rate", justify="right", style="green", width=10)

    for item in data["files"]:
        bar_len = 15
        filled = int((item["percent"] / 100) * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        color = "green" if item["percent"] == 100 else ("yellow" if item["percent"] > 50 else "white")

        table.add_row(
            item["file"],
            f"{item['checked']} / {item['total']}",
            f"[{color}]{bar}[/{color}]",
            f"{item['percent']}%"
        )

    console.print(table)

    g_color = "green" if data["grand_percent"] >= 80 else ("yellow" if data["grand_percent"] >= 50 else "cyan")
    console.print(
        f"\n🎯 [bold]종합 완료율 (Overall Progress):[/bold] [{g_color}][bold]{data['grand_percent']}%[/bold][/{g_color}] "
        f"({data['total_checked']}/{data['grand_total']} Tasks Completed)\n"
    )
