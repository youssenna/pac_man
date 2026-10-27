PYTHON =uv run python3
MYPY = uv run mypy
FLAKE8 = uv run flake8
CONFIG_F = config.json

install:
	uv sync
	UV_SKIP_WHEEL_FILENAME_CHECK=1 uv pip install mazegenerator-00001-py3-none-any.whl


run: install
	clear
	$(PYTHON) -m src
# 	$(PYTHON) -m src $(CONFIG_F)

debug: install
	clear
	$(PYTHON) -m pdb -m src
# 	$(PYTHON) -m pdb -m src $(CONFIG_F)

clean:
	find . \( -name "__pycache__" -o -name ".mypy_cache" -o -name ".venv" -o -name "venv" -o -name "cache" \) -exec rm -rf {} +

lint:
	FLAKE8 .
	MYPY  . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs


lint-strict:
	FLAKE8 .
	MYPY . --strict