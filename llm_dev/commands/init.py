import shutil
from typing import List, Optional
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

def generate_fluent_bit_conf(es_host: str = "elasticsearch", es_port: int = 9200, index_prefix: str = "llm-app-logs") -> str:
    return f"""[SERVICE]
    Flush         1
    Log_Level     info

[INPUT]
    Name          forward
    Listen        0.0.0.0
    Port          24224

[OUTPUT]
    Name          es
    Match         *
    Host          {es_host}
    Port          {es_port}
    Index         {index_prefix}-%Y.%m.%d
    Type          _doc
    Suppress_Type_Name On
"""

def generate_docker_compose(
    project_name: str,
    docker_mode: str = "local_efk",
    es_host: str = "elasticsearch",
    es_port: int = 9200
) -> str:
    if docker_mode == "none":
        return ""

    compose_lines = [
        "version: '3.8'",
        "",
        "networks:",
        "  llm-network:",
        "    name: llm-network",
        "    driver: bridge",
        "",
        "volumes:",
    ]

    # Volumes
    if docker_mode == "local_efk":
        compose_lines.append("  es_data:")
    compose_lines.extend([
        "  qdrant_data:",
        "  ollama_models:",
        "  redis_data:",
        "",
        "services:"
    ])

    # 1. Elasticsearch (local_efk only)
    if docker_mode == "local_efk":
        compose_lines.extend([
            "  # 1. 중앙 로깅: Elasticsearch (Local Cluster)",
            "  elasticsearch:",
            "    image: docker.elastic.co/elasticsearch/elasticsearch:8.13.4",
            f"    container_name: {project_name}-elasticsearch",
            "    environment:",
            "      - discovery.type=single-node",
            '      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"',
            "      - xpack.security.enabled=false",
            "    ports:",
            '      - "9200:9200"',
            "    volumes:",
            "      - es_data:/usr/share/elasticsearch/data",
            "    networks:",
            "      - llm-network",
            ""
        ])

    # 2. Fluent Bit (local_efk or remote_es)
    if docker_mode in ["local_efk", "remote_es"]:
        compose_lines.extend([
            f"  # 2. 중앙 로깅 포워더: Fluent Bit ({'Local ES' if docker_mode == 'local_efk' else f'Remote ES: {es_host}:{es_port}'})",
            "  fluent-bit:",
            "    image: fluent/fluent-bit:3.0.4",
            f"    container_name: {project_name}-fluent-bit",
            "    ports:",
            '      - "24224:24224"',
            "    volumes:",
            "      - ./logging/fluent-bit.conf:/fluent-bit/etc/fluent-bit.conf:ro",
        ])
        if docker_mode == "local_efk":
            compose_lines.extend([
                "    depends_on:",
                "      - elasticsearch",
            ])
        compose_lines.extend([
            "    networks:",
            "      - llm-network",
            ""
        ])

    # 3. Kibana (local_efk only)
    if docker_mode == "local_efk":
        compose_lines.extend([
            "  # 3. 중앙 로깅 대시보드: Kibana",
            "  kibana:",
            "    image: docker.elastic.co/kibana/kibana:8.13.4",
            f"    container_name: {project_name}-kibana",
            "    environment:",
            "      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200",
            "    ports:",
            '      - "5601:5601"',
            "    depends_on:",
            "      - elasticsearch",
            "    networks:",
            "      - llm-network",
            ""
        ])

    # 4. Vector DB: Qdrant
    compose_lines.extend([
        "  # 4. 고성능 Vector DB: Qdrant",
        "  qdrant:",
        "    image: qdrant/qdrant:v1.9.0",
        f"    container_name: {project_name}-qdrant",
        "    ports:",
        '      - "6333:6333"',
        "    volumes:",
        "      - qdrant_data:/qdrant/storage",
        "    networks:",
        "      - llm-network",
        "",
        "  # 5. 캐싱 & Rate Limiter: Redis",
        "  redis:",
        "    image: redis:7.2-alpine",
        f"    container_name: {project_name}-redis",
        "    ports:",
        '      - "6379:6379"',
        "    volumes:",
        "      - redis_data:/data",
        "    networks:",
        "      - llm-network",
        "",
        "  # 6. 로컬 LLM 서버: Ollama",
        "  ollama:",
        "    image: ollama/ollama:latest",
        f"    container_name: {project_name}-ollama",
        "    ports:",
        '      - "11434:11434"',
        "    volumes:",
        "      - ollama_models:/root/.ollama",
        "    networks:",
        "      - llm-network",
        ""
    ])

    return "\n".join(compose_lines)

def run_init(
    target_dir: Path,
    project_name: str,
    stack: str = "fastapi",
    include_docker: bool = True,
    docker_mode: str = "local_efk",
    es_host: str = "elasticsearch",
    es_port: int = 9200,
    docs_selection: Optional[List[str]] = None,
    include_rules: bool = True
):
    target_dir = target_dir.resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    # 하위 호환성 매핑
    if not include_docker:
        docker_mode = "none"

    console.print(Panel.fit(
        f"[bold cyan]🚀 LLM Project Initializer (llm-dev init)[/bold cyan]\n"
        f"• Project Name: [yellow]{project_name}[/yellow]\n"
        f"• Target Path : [green]{target_dir}[/green]\n"
        f"• Tech Stack  : [magenta]{stack}[/magenta]\n"
        f"• Docker/Log  : [cyan]{docker_mode}[/cyan]"
        + (f" [dim]({es_host}:{es_port})[/dim]" if docker_mode == "remote_es" else ""),
        title="[bold green]Initializing[/bold green]"
    ))

    created_items = []

    # 1. Copy Selected Knowledge Base Documents
    docs_target = target_dir / DEFAULT_DOCS_TARGET
    docs_target.mkdir(parents=True, exist_ok=True)
    if DOCS_TEMPLATE_DIR.exists():
        all_doc_files = list(DOCS_TEMPLATE_DIR.glob("*.md"))
        for doc_file in all_doc_files:
            # 필터링 적용 (docs_selection이 지정된 경우 해당 문서만 복사)
            if docs_selection is not None and doc_file.name not in docs_selection:
                continue
            dest = docs_target / doc_file.name
            shutil.copy2(doc_file, dest)
            created_items.append((f"{DEFAULT_DOCS_TARGET}/{doc_file.name}", "Knowledge Base Guide"))

    # 2. Copy AI Coding Rules
    if include_rules and RULES_TEMPLATE_DIR.exists():
        cursorrules_src = RULES_TEMPLATE_DIR / ".cursorrules"
        if cursorrules_src.exists():
            shutil.copy2(cursorrules_src, target_dir / ".cursorrules")
            created_items.append((".cursorrules", "Cursor AI Coding Rules"))

        agents_src = RULES_TEMPLATE_DIR / "AGENTS.md"
        if agents_src.exists():
            shutil.copy2(agents_src, target_dir / "AGENTS.md")
            created_items.append(("AGENTS.md", "AI Agent & Assistant Rules"))

    # 3. Generate Docker & Logging Stack
    if docker_mode != "none":
        # Docker Compose 생성
        compose_content = generate_docker_compose(
            project_name=project_name,
            docker_mode=docker_mode,
            es_host=es_host,
            es_port=es_port
        )
        (target_dir / "docker-compose.llm-dev.yml").write_text(compose_content, encoding="utf-8")
        created_items.append(("docker-compose.llm-dev.yml", f"Docker Compose ({docker_mode})"))

        # Fluent Bit 설정 생성 (local_efk 또는 remote_es 일 때)
        if docker_mode in ["local_efk", "remote_es"]:
            logging_dir = target_dir / "logging"
            logging_dir.mkdir(parents=True, exist_ok=True)
            fb_conf = generate_fluent_bit_conf(
                es_host=es_host if docker_mode == "remote_es" else "elasticsearch",
                es_port=es_port,
                index_prefix=f"{project_name}-logs"
            )
            (logging_dir / "fluent-bit.conf").write_text(fb_conf, encoding="utf-8")
            created_items.append(("logging/fluent-bit.conf", f"Fluent Bit Config -> {es_host if docker_mode == 'remote_es' else 'local es'}:{es_port}"))

    # 4. Copy Stack Boilerplates
    if stack.lower() == "fastapi":
        fastapi_dir = BOILERPLATES_DIR / "fastapi"
        if fastapi_dir.exists():
            core_dir = target_dir / "src" / "core"
            core_dir.mkdir(parents=True, exist_ok=True)
            for f in fastapi_dir.glob("*.py"):
                shutil.copy2(f, core_dir / f.name)
                created_items.append((f"src/core/{f.name}", "FastAPI Security & PII Boilerplate"))
            env_src = fastapi_dir / ".env.example"
            if env_src.exists():
                shutil.copy2(env_src, target_dir / ".env.example")
                created_items.append((".env.example", "Environment Variables Template"))


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
