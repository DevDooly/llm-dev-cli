from pathlib import Path

PACKAGE_ROOT = Path(__file__).parent.resolve()
TEMPLATES_DIR = PACKAGE_ROOT / "templates"
DOCS_TEMPLATE_DIR = TEMPLATES_DIR / "docs"
RULES_TEMPLATE_DIR = TEMPLATES_DIR / "rules"
DOCKER_TEMPLATE_DIR = TEMPLATES_DIR / "docker"
BOILERPLATES_DIR = TEMPLATES_DIR / "boilerplates"
STATIC_DIR = PACKAGE_ROOT / "web" / "static"

DEFAULT_DOCS_TARGET = "docs/llm-development"
