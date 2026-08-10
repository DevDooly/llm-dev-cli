from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..checkers import ALL_CHECKERS, CheckResult

console = Console()

def run_doctor(project_dir: Path) -> bool:
    project_dir = project_dir.resolve()

    console.print(Panel.fit(
        f"[bold cyan]🔍 LLM Governance & Standard Doctor[/bold cyan]\n"
        f"Scanning Project: [green]{project_dir}[/green]",
        title="[bold yellow]Doctor Diagnostics[/bold yellow]"
    ))

    results = []
    total = len(ALL_CHECKERS)
    passed_count = 0

    for checker in ALL_CHECKERS:
        res = checker.run_check(project_dir)
        results.append(res)
        if res.passed:
            passed_count += 1

    # Print Diagnostic Table
    table = Table(title="[bold]Diagnostic Results[/bold]", show_header=True, header_style="bold magenta")
    table.add_column("Category", style="cyan", width=25)
    table.add_column("Status", width=12)
    table.add_column("Details & Action Items", style="white")

    for res in results:
        if res.passed:
            status_text = "[bold green][✔] PASS[/bold green]"
            if res.severity == "INFO":
                status_text = "[bold blue][i] INFO[/bold blue]"
            msg = res.message
        else:
            if res.severity == "ERROR":
                status_text = "[bold red][✖] ERROR[/bold red]"
            else:
                status_text = "[bold yellow][!] WARN[/bold yellow]"
            msg = f"{res.message}"
            if res.suggestion:
                msg += f"\n[dim yellow]↳ 조치: {res.suggestion}[/dim yellow]"

        table.add_row(res.name, status_text, msg)

    console.print(table)

    # Score calculation
    score = int((passed_count / total) * 100)
    score_color = "green" if score >= 80 else ("yellow" if score >= 60 else "red")

    console.print(
        f"\n📊 [bold]표준 준수율 (Compliance Score):[/bold] [{score_color}][bold]{score}%[/bold][/{score_color}] "
        f"({passed_count}/{total} Passed)"
    )

    if score == 100:
        console.print("[bold green]🎉 축하합니다! 모든 LLM 표준 가이드라인을 완벽히 준수하고 있습니다.[/bold green]\n")
    else:
        console.print("[yellow]💡 위 경고 및 오류 항목의 권장 조치를 확인하여 보안 및 품질을 보강하세요.[/yellow]\n")

    return score >= 80
