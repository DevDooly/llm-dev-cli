from setuptools import setup, find_packages

setup(
    name="llm-dev-cli",
    version="0.1.0",
    description="LLM Project Scaffolder, Doctor & Lifecycle Compliance CLI",
    author="DevDooly",
    author_email="sunhongyi@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "llm_dev": [
            "templates/**/*",
            "templates/**/.*",
            "web/static/*"
        ]
    },
    install_requires=[
        "rich>=13.7.0",
        "fastapi>=0.110.0",
        "uvicorn>=0.28.0",
        "jinja2>=3.1.3",
        "pydantic>=2.6.0",
        "questionary>=2.0.0"
    ],
    entry_points={
        "console_scripts": [
            "llm-dev=llm_dev.main:main",
        ],
    },
    python_requires=">=3.10",
)
