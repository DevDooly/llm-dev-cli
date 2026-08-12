import sys
from pathlib import Path
import questionary
from questionary import Choice, Style
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
    ('selected', 'fg:#34d399'),           # 선택 항목
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

    stack_choice = questionary.select(
        "3. 백엔드 보일러플레이트 스택을 선택하세요:",
        choices=[
            Choice("🐍 FastAPI (Python) - PII Masker, Presidio, structlog 포함", value="fastapi"),
            Choice("☕ Spring Boot 3 (Java 21) - Logback JSON, Virtual Threads", value="spring"),
            Choice("📄 None - 표준 가이드 문서 및 AI 룰셋(.cursorrules)만 생성", value="none")
        ],
        style=CUSTOM_STYLE
    ).ask()
    if not stack_choice:
        return

    include_docker = questionary.confirm(
        "4. Docker Compose 및 Fluent Bit 로깅 스택을 포함하시겠습니까?",
        default=True,
        style=CUSTOM_STYLE
    ).ask()

    target_path = Path(target_dir_str).resolve()
    console.print(f"\n[dim]스캐폴딩 생성 중: [bold green]{target_path}[/bold green][/dim]\n")
    
    run_init(
        target_dir=target_path,
        project_name=project_name,
        stack=stack_choice,
        include_docker=include_docker
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
