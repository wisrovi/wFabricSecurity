.PHONY: help install-dev install-pypi build publish clean lint test

help:
	@echo "wFabricSecurity - Comandos"
	@echo ""
	@echo "Uso: make [comando]"
	@echo ""
	@echo "Comandos:"
	@echo "  install-dev   - Instalar librería en modo desarrollo (editable)"
	@echo "  install-pypi  - Instalar librería desde PyPI"
	@echo "  build         - Construir paquete para distribución"
	@echo "  publish       - Publicar en PyPI"
	@echo "  clean         - Limpiar archivos generados"
	@echo "  lint          - Verificar código"
	@echo "  environment   - Ir al entorno y mostrar ayuda"

install-dev:
	@echo ">> Instalando wFabricSecurity en modo desarrollo..."
	pip install -e .
	@echo "✓ Instalación desarrollo completada"

install-pypi:
	@echo ">> Instalando wFabricSecurity desde PyPI..."
	pip install wFabricSecurity
	@echo "✓ Instalación desde PyPI completada"

build:
	@echo ">> Construyendo paquete..."
	pip install --upgrade build
	python -m build
	@echo "✓ Paquete construido en ./dist/"

publish: build
	@echo ">> Publicando en PyPI..."
	@pip install twine || pip install twine
	twine upload dist/*
	@echo "✓ Paquete publicado en PyPI"

clean:
	@echo ">> Limpiando archivos generados..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Limpieza completada"

lint:
	@echo ">> Verificando código..."
	pip install ruff || true
	ruff check wFabricSecurity/ examples/ || true
	@echo "✓ Verificación completada"

test:
	@echo ">> Ejecutando tests..."
	@if [ -d "tests" ]; then \
		pytest tests/; \
	else \
		echo "No se encontraron tests"; \
	fi

environment:
	@cd enviroment && make help
