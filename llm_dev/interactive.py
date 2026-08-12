import sys
from pathlib import Path
from typing import List, Optional
import questionary
from questionary import Choice, Style, Separator
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from . import __version__
from .commands.init import run_init
from .commands.doctor import run_doctor
from .commands.status import run_status
from .commands.view import run_view

console = Console()

# questionary 커스텀 테마 (다크 & 모던 시안/그린/옐로우 스타일)
CUSTOM_STYLE = Style([
    ('qmark', 'fg:#06b6d4 bold'),        # 질문 아이콘 (?)
    ('question', 'bold'),                 # 질문 텍스트
    ('answer', 'fg:#10b981 bold'),        # 선택/입력 완료된 답변
    ('pointer', 'fg:#38bdf8 bold'),       # 포인터 화살표 (>)
    ('highlighted', 'fg:#38bdf8 bold'),   # 현재 하이라이트된 항목
    ('selected', 'fg:#34d399 bold'),      # 체크박스 선택 항목
    ('separator', 'fg:#6b7280'),          # 구분선
    ('instruction', 'fg:#9ca3af italic'), # 가이드 설명
    ('text', ''),
    ('disabled', 'fg:#4b5563 italic')
])

def print_banner():
    banner_text = Text()
    banner_text.append("🤖 LLM Development CLI & Governance Hub", style="bold cyan")
    banner_text.append(f" (v{__version__})\n", style="dim cyan")
    banner_text.append("Day 0 사전 인프라 스캐폴딩 • 룰셋 정적 진단 • 진척도 추적 • 실시간 대시보드\n", style="dim white")
    banner_text.append("방향키(↑/↓)로 메뉴를 이동하고 [Enter] 키로 선택하세요.", style="bold yellow")

    console.print(Panel(
        banner_text,
        border_style="cyan",
        title="[bold green]Interactive Mode[/bold green]",
        subtitle="[dim]DevDooly/llm-dev-cli[/dim]"
    ))

def interactive_init():
    console.print("\n[bold cyan]🚀 신규 LLM 프로젝트 초기화 (Project Init)[/bold cyan]")
    
    # 1. 기본 정보 입력
    project_name = questionary.text(
        "1. 프로젝트 이름을 입력하세요:",
        default="my-llm-service",
        style=CUSTOM_STYLE
    ).ask()
    if not project_name:
        return

    default_dir = f"./{project_name}"
    target_dir_str = questionary.text(
        "2. 생성할 디렉토리 경로를 입력하세요:",
        default=default_dir,
        style=CUSTOM_STYLE
    ).ask()
    if not target_dir_str:
        return

    # 2. 스캐폴딩 프리셋 / 모드 선택
    preset = questionary.select(
        "3. 초기화 모드(Preset)를 선택하세요:",
        choices=[
            Choice(
                "🌟 표준 전체 스캐폴딩 (Standard Full) - [기본 추천]\n     4대 인프라 가이드 + AI 룰셋 + 로컬 전체 EFK/Docker + 백엔드 보일러플레이트",
                value="standard"
            ),
            Choice(
                "🪶 경량 빠른 시작 (Lightweight / Minimal)\n     핵심 가이드 + AI 룰셋 + 백엔드 코드 (무거운 ELK/Docker 인프라 제외)",
                value="minimal"
            ),
            Choice(
                "🛠️  커스텀 맞춤 선택 (Custom Scaffolding)\n     포함할 가이드 문서, 원격 Elasticsearch 연동, 도커 스택 직접 하나씩 선택",
                value="custom"
            )
        ],
        style=CUSTOM_STYLE
    ).ask()
    if not preset:
        return

    # 기본값 변수
    stack = "fastapi"
    docker_mode = "local_efk"
    es_host = "elasticsearch"
    es_port = 9200
    docs_selection: Optional[List[str]] = None
    include_rules = True

    # 프리셋별 분기
    if preset == "standard":
        stack_choice = questionary.select(
            "4. 백엔드 보일러플레이트 스택을 선택하세요:",
            choices=[
                Choice("🐍 FastAPI (Python) - PII Masker, Presidio, structlog 포함", value="fastapi"),
                Choice("☕ Spring Boot 3 (Java 21) - Logback JSON, Virtual Threads", value="spring"),
                Choice("📄 None - 표준 가이드 문서 및 인프라만 생성", value="none")
            ],
            style=CUSTOM_STYLE
        ).ask()
        if not stack_choice:
            return
        stack = stack_choice
        docker_mode = "local_efk"
        include_rules = True
        docs_selection = None  # 전체 문서 포함

    elif preset == "minimal":
        stack_choice = questionary.select(
            "4. 백엔드 보일러플레이트 스택을 선택하세요:",
            choices=[
                Choice("🐍 FastAPI (Python) - PII Masker & 로컬 JSON 로거", value="fastapi"),
                Choice("☕ Spring Boot 3 (Java 21) - Logback JSON 로거", value="spring"),
                Choice("📄 None - 핵심 가이드 및 AI 룰셋만 생성", value="none")
            ],
            style=CUSTOM_STYLE
        ).ask()
        if not stack_choice:
            return
        stack = stack_choice
        docker_mode = "none"
        include_rules = True
        # 경량 문서만 선택
        docs_selection = [
            "README.md",
            "llm-foundation-setup.md",
            "llm-guidelines.md"
        ]

    elif preset == "custom":
        # 3-1. 백엔드 스택 선택
        stack_choice = questionary.select(
            "4. 백엔드 보일러플레이트 스택을 선택하세요:",
            choices=[
                Choice("🐍 FastAPI (Python) - PII Masker, Presidio, structlog 포함", value="fastapi"),
                Choice("☕ Spring Boot 3 (Java 21) - Logback JSON, Virtual Threads", value="spring"),
                Choice("📄 None - 문서 및 인프라만 생성", value="none")
            ],
            style=CUSTOM_STYLE
        ).ask()
        if not stack_choice:
            return
        stack = stack_choice

        # 3-2. 포함할 문서 체크박스 선택
        doc_choices = [
            Choice("🏗️  Day 0 필수 사전 인프라 마스터 가이드 (llm-foundation-setup.md)", value="llm-foundation-setup.md", checked=True),
            Choice("🔒 보안·인증, Rate Limiter & PII 자동 마스킹 (llm-auth-and-security.md)", value="llm-auth-and-security.md", checked=True),
            Choice("🐳 Docker 컨테이너 & Agent 샌드박스 격리 (llm-docker-and-sandbox.md)", value="llm-docker-and-sandbox.md", checked=True),
            Choice("📊 ELF/EFK 중앙 로깅 & 메트릭 관측성 (llm-logging-and-observability.md)", value="llm-logging-and-observability.md", checked=True),
            Choice("📘 LLM 개발 6단계 라이프사이클 & 코딩 룰셋 (llm-guidelines.md)", value="llm-guidelines.md", checked=True),
            Choice("🗺️  지식베이스 구축 마스터 로드맵 (llm-roadmap.md)", value="llm-roadmap.md", checked=True),
            Choice("🛠️  자동화 도구 기획 및 명세서 (llm-automation-tool-spec.md)", value="llm-automation-tool-spec.md", checked=False),
        ]
        selected_docs = questionary.checkbox(
            "5. 프로젝트에 포함할 가이드라인 문서를 선택하세요 (스페이스바로 토글):",
            choices=doc_choices,
            style=CUSTOM_STYLE
        ).ask()
        if selected_docs is None:
            return
        # 마스터 README는 항상 포함
        if "README.md" not in selected_docs:
            selected_docs.append("README.md")
        docs_selection = selected_docs

        # 3-3. AI 룰셋 포함 여부
        include_rules = questionary.confirm(
            "6. AI 코딩 어시스턴트 룰셋(.cursorrules, AGENTS.md)을 포함하시겠습니까?",
            default=True,
            style=CUSTOM_STYLE
        ).ask()

        # 3-4. Docker 및 로깅 스택 구성 방식 선택
        docker_choice = questionary.select(
            "7. Docker 및 중앙 로깅 스택 구성 방식을 선택하세요:",
            choices=[
                Choice("🐳 1. 로컬 독립형 EFK 풀스택 (Elasticsearch + Fluent Bit + Kibana + Qdrant + Redis + Ollama)", value="local_efk"),
                Choice("🌐 2. 기존 원격 Elasticsearch 연동 (Fluent Bit + Qdrant + Redis / 외부 ES 주소 지정)", value="remote_es"),
                Choice("⚡ 3. Vector DB & Redis만 구동 (Qdrant + Redis + Ollama / ELK 스택 제외)", value="vector_only"),
                Choice("🚫 4. Docker 스택 미포함 (순수 소스코드 및 문서만 생성)", value="none")
            ],
            style=CUSTOM_STYLE
        ).ask()
        if not docker_choice:
            return
        docker_mode = docker_choice

        # 원격 ES 설정 입력
        if docker_mode == "remote_es":
            es_host = questionary.text(
                "  ↳ 기존 원격 Elasticsearch 호스트(IP/도메인)를 입력하세요:",
                default="192.168.0.28",
                style=CUSTOM_STYLE
            ).ask() or "elasticsearch"

            es_port_str = questionary.text(
                "  ↳ 원격 Elasticsearch 포트 번호를 입력하세요:",
                default="9200",
                style=CUSTOM_STYLE
            ).ask() or "9200"
            try:
                es_port = int(es_port_str)
            except ValueError:
                es_port = 9200

    target_path = Path(target_dir_str).resolve()
    console.print(f"\n[dim]스캐폴딩 생성 중: [bold green]{target_path}[/bold green][/dim]\n")
    
    run_init(
        target_dir=target_path,
        project_name=project_name,
        stack=stack,
        docker_mode=docker_mode,
        es_host=es_host,
        es_port=es_port,
        docs_selection=docs_selection,
        include_rules=include_rules
    )

def interactive_doctor():
    console.print("\n[bold cyan]🔍 프로젝트 거버넌스 & 보안 진단 (Doctor)[/bold cyan]")
    
    target_dir_str = questionary.text(
        "진단할 프로젝트 디렉토리 경로를 입력하세요:",
        default=".",
        style=CUSTOM_STYLE
    ).ask()
    if not target_dir_str:
        return

    target_path = Path(target_dir_str).resolve()
    if not target_path.exists():
        console.print(f"[bold red]❌ 디렉토리가 존재하지 않습니다: {target_path}[/bold red]")
        return

    console.print(f"\n[dim]진단 시작: [bold green]{target_path}[/bold green][/dim]\n")
    run_doctor(target_path)

def interactive_status():
    console.print("\n[bold cyan]📊 마크다운 체크리스트 진척도 확인 (Status)[/bold cyan]")
    
    target_dir_str = questionary.text(
        "진척도를 확인할 프로젝트 디렉토리 경로를 입력하세요:",
        default=".",
        style=CUSTOM_STYLE
    ).ask()
    if not target_dir_str:
        return

    target_path = Path(target_dir_str).resolve()
    if not target_path.exists():
        console.print(f"[bold red]❌ 디렉토리가 존재하지 않습니다: {target_path}[/bold red]")
        return

    console.print(f"\n[dim]체크리스트 스캔 중: [bold green]{target_path}[/bold green][/dim]\n")
    run_status(target_path)

def interactive_view():
    console.print("\n[bold cyan]🌐 로컬 실시간 웹 대시보드 실행 (View)[/bold cyan]")
    
    target_dir_str = questionary.text(
        "1. 서빙할 프로젝트 디렉토리 경로를 입력하세요:",
        default=".",
        style=CUSTOM_STYLE
    ).ask()
    if not target_dir_str:
        return

    port_str = questionary.text(
        "2. 대시보드 포트 번호를 입력하세요:",
        default="8899",
        style=CUSTOM_STYLE
    ).ask()
    if not port_str:
        return
    
    try:
        port = int(port_str)
    except ValueError:
        port = 8899

    host_choice = questionary.select(
        "3. 호스트 바인딩 주소를 선택하세요:",
        choices=[
            Choice("🌐 0.0.0.0 (외부/원격 및 LAN 접속 허용)", value="0.0.0.0"),
            Choice("🔒 127.0.0.1 (로컬 PC 내부 접속 전용)", value="127.0.0.1")
        ],
        style=CUSTOM_STYLE
    ).ask()
    if not host_choice:
        return

    target_path = Path(target_dir_str).resolve()
    console.print(f"\n[dim]대시보드 시작 중: [bold green]{target_path}[/bold green][/dim]\n")
    run_view(target_path, port=port, host=host_choice)

def run_interactive_menu():
    while True:
        console.clear()
        print_banner()
        console.print("")

        action = questionary.select(
            "실행할 작업을 선택하세요:",
            choices=[
                Choice("🚀  1. 신규 LLM 프로젝트 초기화 (Init)", value="init"),
                Choice("🔍  2. 거버넌스 & 보안 진단 (Doctor)", value="doctor"),
                Choice("📊  3. 라이프사이클 체크리스트 진척도 (Status)", value="status"),
                Choice("🌐  4. 로컬 실시간 웹 대시보드 실행 (View)", value="view"),
                Choice("❌  0. 종료 (Exit)", value="exit")
            ],
            style=CUSTOM_STYLE
        ).ask()

        if not action or action == "exit":
            console.print("\n[bold yellow]👋 llm-dev 도구를 종료합니다. 즐거운 LLM 개발 되세요![/bold yellow]\n")
            sys.exit(0)

        try:
            if action == "init":
                interactive_init()
            elif action == "doctor":
                interactive_doctor()
            elif action == "status":
                interactive_status()
            elif action == "view":
                interactive_view()
        except KeyboardInterrupt:
            console.print("\n[dim]작업이 취소되었습니다.[/dim]")

        console.print("\n" + "─" * 60)
        input("⏎ 계속하려면 [Enter] 키를 누르세요...")
