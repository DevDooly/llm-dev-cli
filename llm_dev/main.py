import argparse
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))
    from llm_dev import __version__
    from llm_dev.commands.init import run_init
    from llm_dev.commands.doctor import run_doctor
    from llm_dev.commands.status import run_status
    from llm_dev.commands.view import run_view
    from llm_dev.interactive import run_interactive_menu
else:
    from . import __version__
    from .commands.init import run_init
    from .commands.doctor import run_doctor
    from .commands.status import run_status
    from .commands.view import run_view
    from .interactive import run_interactive_menu

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="llm-dev",
        description="🤖 LLM Development Standard Scaffolder, Doctor & Compliance CLI"
    )
    parser.add_argument("-v", "--version", action="version", version=f"llm-dev v{__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands (run without args for interactive TUI menu)")

    # init command
    init_parser = subparsers.add_parser("init", help="Scaffold standard LLM project knowledge base & templates")
    init_parser.add_argument("--name", "-n", type=str, default=None, help="Project name (defaults to current dir name)")
    init_parser.add_argument("--dir", "-d", type=str, default=".", help="Target project directory")
    init_parser.add_argument("--stack", "-s", choices=["fastapi", "spring", "none"], default="fastapi", help="Backend boilerplate stack")
    init_parser.add_argument("--preset", choices=["standard", "minimal"], default="standard", help="Scaffolding preset")
    init_parser.add_argument("--docker-mode", choices=["local_efk", "remote_es", "vector_only", "none"], default=None, help="Docker & logging stack mode")
    init_parser.add_argument("--es-host", type=str, default="elasticsearch", help="Remote Elasticsearch host (when using remote_es mode)")
    init_parser.add_argument("--es-port", type=int, default=9200, help="Remote Elasticsearch port (default: 9200)")
    init_parser.add_argument("--no-docker", action="store_true", help="Skip generating docker-compose and logging stack")
    init_parser.add_argument("--no-rules", action="store_true", help="Skip generating AI ruleset (.cursorrules, AGENTS.md)")
    init_parser.add_argument("--docs", type=str, default=None, help="Comma-separated doc names to include (e.g. 'foundation,auth,guidelines')")

    # doctor command
    doctor_parser = subparsers.add_parser("doctor", help="Run diagnostic checks on governance and security rules")
    doctor_parser.add_argument("--dir", "-d", type=str, default=".", help="Target project directory to inspect")

    # status command
    status_parser = subparsers.add_parser("status", help="Inspect checklist completion status across markdown docs")
    status_parser.add_argument("--dir", "-d", type=str, default=".", help="Target project directory to inspect")

    # view command
    view_parser = subparsers.add_parser("view", help="Start local web dashboard server")
    view_parser.add_argument("--dir", "-d", type=str, default=".", help="Target project directory to serve")
    view_parser.add_argument("--port", "-p", type=int, default=8899, help="Port for the dashboard server (default: 8899)")
    view_parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address (default: 127.0.0.1)")

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        # 인자 없이 실행 시 대화형 TUI 메뉴 시작
        try:
            run_interactive_menu()
        except KeyboardInterrupt:
            print("\n👋 프로그램을 종료합니다.")
            sys.exit(0)
        return

    target_dir = Path(args.dir).resolve()

    if args.command == "init":
        p_name = args.name or target_dir.name
        
        # docker_mode 결정
        docker_mode = args.docker_mode
        if args.no_docker:
            docker_mode = "none"
        elif docker_mode is None:
            docker_mode = "none" if args.preset == "minimal" else "local_efk"

        # 문서 필터링 결정
        docs_selection = None
        if args.preset == "minimal":
            docs_selection = ["README.md", "llm-foundation-setup.md", "llm-guidelines.md"]
        elif args.docs:
            docs_selection = ["README.md"]
            for d in args.docs.split(","):
                d = d.strip()
                if not d.endswith(".md"):
                    d = f"llm-{d}.md"
                docs_selection.append(d)

        run_init(
            target_dir=target_dir,
            project_name=p_name,
            stack=args.stack,
            docker_mode=docker_mode,
            es_host=args.es_host,
            es_port=args.es_port,
            docs_selection=docs_selection,
            include_rules=not args.no_rules
        )
    elif args.command == "doctor":
        success = run_doctor(target_dir)
        sys.exit(0 if success else 1)
    elif args.command == "status":
        run_status(target_dir)
    elif args.command == "view":
        run_view(target_dir, port=args.port, host=args.host)


if __name__ == "__main__":
    main()
