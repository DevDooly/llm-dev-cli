import uvicorn
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from ..web.app import create_app

console = Console()

def run_view(project_dir: Path, port: int = 8899, host: str = "127.0.0.1"):
    project_dir = project_dir.resolve()
    app = create_app(project_dir)

    url = f"http://{host}:{port}"
    console.print(Panel.fit(
        f"[bold cyan]🚀 LLM Development Live Dashboard[/bold cyan]\n"
        f"• Project Path : [green]{project_dir}[/green]\n"
        f"• Dashboard URL: [bold yellow]{url}[/bold yellow]\n"
        f"[dim]Press Ctrl+C to stop the dashboard server[/dim]",
        title="[bold green]Dashboard Online[/bold green]"
    ))

    uvicorn.run(app, host=host, port=port, log_level="warning")
