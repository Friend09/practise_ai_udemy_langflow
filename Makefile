.PHONY: compile install clean all help


compile:
	uv pip compile requirements.in -o requirements.txt


install:
	uv pip install --upgrade pip && \
	uv pip install -r requirements.txt ; \
	clear


clean:
	rm -rf .pytest_cache .ruff_cache

all: clean compile install

help:
	@echo "Available commands:"
	@echo "  compile      - Update requirements.txt based on requirements.in"
	@echo "  install      - Upgrade pip and install packages from requirements.txt"
	@echo "  clean        - Remove .pytest_cache and .ruff_cache directories"
	@echo "  all          - Run clean, compile, and install"
	@echo "  help         - Show this help message"
