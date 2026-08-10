import shutil
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..config import (
    DOCS_TEMPLATE_DIR,
    RULES_TEMPLATE_DIR,
    DOCKER_TEMPLATE_DIR,
    BOILERPLATES_DIR,
    DEFAULT_DOCS_TARGET
)

console = Console()

def run_init(
    target_dir: Path,
    project_name: str,
    stack: str = "fastapi",
    include_docker: bool = True
):
    target_dir = target_dir.resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    console.print(Panel.fit(
        f"[bold cyan]🚀 LLM Project Initializer (llm-dev init)[/bold cyan]\n"
        f"• Project Name: [yellow]{project_name}[/yellow]\n"
        f"• Target Path : [green]{target_dir}[/green]\n"
        f"• Tech Stack  : [magenta]{stack}[/magenta]",
        title="[bold green]Initializing[/bold green]"
    ))

    created_items = []

    # 1. Copy Standard Knowledge Base Documents
    docs_target = target_dir / DEFAULT_DOCS_TARGET
    docs_target.mkdir(parents=True, exist_ok=True)
    if DOCS_TEMPLATE_DIR.exists():
        for doc_file in DOCS_TEMPLATE_DIR.glob("*.md"):
            dest = docs_target / doc_file.name
            shutil.copy2(doc_file, dest)
            created_items.append((f"{DEFAULT_DOCS_TARGET}/{doc_file.name}", "Standard Knowledge Base"))

    # 2. Copy AI Coding Rules
    if RULES_TEMPLATE_DIR.exists():
        cursorrules_src = RULES_TEMPLATE_DIR / ".cursorrules"
        if cursorrules_src.exists():
            shutil.copy2(cursorrules_src, target_dir / ".cursorrules")
            created_items.append((".cursorrules", "Cursor AI Coding Rules"))

        agents_src = RULES_TEMPLATE_DIR / "AGENTS.md"
        if agents_src.exists():
            shutil.copy2(agents_src, target_dir / "AGENTS.md")
            created_items.append(("AGENTS.md", "AI Agent & Assistant Rules"))

    # 3. Copy Docker & Logging Stack
    if include_docker and DOCKER_TEMPLATE_DIR.exists():
        dc_src = DOCKER_TEMPLATE_DIR / "docker-compose.llm-dev.yml"
        if dc_src.exists():
            content = dc_src.read_text(encoding="utf-8")
            rendered = content.replace("{{ project_name }}", project_name)
            (target_dir / "docker-compose.llm-dev.yml").write_text(rendered, encoding="utf-8")
            created_items.append(("docker-compose.llm-dev.yml", "Local Full-Stack Docker Compose"))

        fb_src = DOCKER_TEMPLATE_DIR / "fluent-bit.conf"
        if fb_src.exists():
            logging_dir = target_dir / "logging"
            logging_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(fb_src, logging_dir / "fluent-bit.conf")
            created_items.append(("logging/fluent-bit.conf", "Fluent Bit Central Logging Config"))

    # 4. Copy Stack Boilerplates
    if stack.lower() == "fastapi":
        fastapi_dir = BOILERPLATES_DIR / "fastapi"
        if fastapi_dir.exists():
            core_dir = target_dir / "src" / "core"
            core_dir.mkdir(parents=True, exist_ok=True)
            for f in fastapi_dir.glob("*.py"):
                shutil.copy2(f, core_dir / f.name)
                created_items.append((f"src/core/{f.name}", "FastAPI Security & Observability Boilerplate"))

    elif stack.lower() == "spring":
        spring_dir = BOILERPLATES_DIR / "spring"
        if spring_dir.exists():
            res_dir = target_dir / "src" / "main" / "resources"
            res_dir.mkdir(parents=True, exist_ok=True)
            logback_f = spring_dir / "logback-spring.xml"
            if logback_f.exists():
                shutil.copy2(logback_f, res_dir / "logback-spring.xml")
                created_items.append(("src/main/resources/logback-spring.xml", "Spring Boot JSON Logging Config"))

            java_dir = target_dir / "src" / "main" / "java" / "com" / "example" / "ai" / "logging"
            java_dir.mkdir(parents=True, exist_ok=True)
            logger_java = spring_dir / "LlmAuditLogger.java"
            if logger_java.exists():
                shutil.copy2(logger_java, java_dir / "LlmAuditLogger.java")
                created_items.append(("src/.../logging/LlmAuditLogger.java", "Spring Boot LLM Audit Logger"))

    # Summary Table
    table = Table(title="[bold green]Scaffolded Files Summary[/bold green]", show_header=True, header_style="bold magenta")
    table.add_column("Relative Path", style="cyan")
    table.add_column("Description", style="white")

    for path_str, desc in created_items:
        table.add_row(f"[✔] {path_str}", desc)

    console.print(table)
    console.print(
        "\n[bold green]✨ Initialized successfully![/bold green] "
        "Run [bold cyan]llm-dev doctor[/bold cyan] anytime to verify governance compliance.\n"
    )
