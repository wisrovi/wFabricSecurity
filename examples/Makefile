.PHONY: help test test-core test-json test-image test-p2p test-data test-all test-v test-fabric install clean

help:
	@echo "wFabricSecurity Examples - Comandos disponibles"
	@echo ""
	@echo "Uso: make [comando]"
	@echo ""
	@echo "Tests:"
	@echo "  test          - Ejecutar todos los tests (sin integration)"
	@echo "  test-core     - Tests de la librería core"
	@echo "  test-json     - Tests de ejemplos JSON"
	@echo "  test-image    - Tests de ejemplos Image"
	@echo "  test-p2p      - Tests de ejemplos P2P"
	@echo "  test-data     - Tests de ejemplos Data"
	@echo "  test-all      - Tests completos incluyendo integration"
	@echo "  test-v        - Tests con output verbose"
	@echo ""
	@echo "Ejemplos (requiere Docker de Fabric corriendo):"
	@echo "  run-json-base      - Ejecutar ejemplo JSON base"
	@echo "  run-json-async     - Ejecutar ejemplo JSON async"
	@echo "  run-image-base     - Ejecutar ejemplo Image base"
	@echo "  run-image-async    - Ejecutar ejemplo Image async"
	@echo "  run-p2p-base       - Ejecutar ejemplo P2P base"
	@echo "  run-p2p-async      - Ejecutar ejemplo P2P async"
	@echo "  run-data-base      - Ejecutar ejemplo Data base"
	@echo "  run-data-async     - Ejecutar ejemplo Data async"
	@echo ""
	@echo "Otros:"
	@echo "  install        - Instalar dependencias"
	@echo "  clean          - Limpiar archivos generados"

install:
	pip install -r requirements.txt

test: install
	@echo "Ejecutando tests..."
	python -m pytest test/ -v --ignore=test/test_json.py --ignore=test/test_image.py --ignore=test/test_p2p.py --ignore=test/test_data.py

test-core: install
	@echo "Ejecutando tests de librería core..."
	python -m pytest test/test_library.py -v

test-json: install
	@echo "Ejecutando tests de JSON..."
	python -m pytest test/test_json.py -v

test-image: install
	@echo "Ejecutando tests de Image..."
	python -m pytest test/test_image.py -v

test-p2p: install
	@echo "Ejecutando tests de P2P..."
	python -m pytest test/test_p2p.py -v

test-data: install
	@echo "Ejecutando tests de Data..."
	python -m pytest test/test_data.py -v

test-all: install
	@echo "Ejecutando TODOS los tests..."
	python -m pytest test/ -v

test-v: install
	@echo "Ejecutando tests con verbose..."
	python -m pytest test/ -vv --tb=long

test-fabric:
	@echo "Verificando estado de Fabric..."
	@cd ../enviroment && docker ps --filter "name=peer0\|orderer\|cli" --format "table {{.Names}}\t{{.Status}}" || echo "Contenedores no encontrados"

run-json-base:
	@echo "Ejecutando JSON Base - inicia slave en otra terminal:"
	@echo "  cd json/base && python slave.py"
	@echo ""
	@echo "Luego ejecuta master:"
	@cd json/base && python master.py

run-json-async:
	@echo "Ejecutando JSON Async - inicia slave en otra terminal:"
	@echo "  cd json/async && python slave.py"
	@echo ""
	@echo "Luego ejecuta master:"
	@cd json/async && python master.py

run-image-base:
	@echo "Ejecutando Image Base - inicia slave en otra terminal:"
	@echo "  cd image/base && python slave.py"
	@echo ""
	@echo "Luego ejecuta master:"
	@cd image/base && python master.py

run-image-async:
	@echo "Ejecutando Image Async - inicia slave en otra terminal:"
	@echo "  cd image/async && python slave.py"
	@echo ""
	@echo "Luego ejecuta master:"
	@cd image/async && python master.py

run-p2p-base:
	@echo "Ejecutando P2P Base - inicia slave en otra terminal:"
	@echo "  cd p2p/base && python slave.py"
	@echo ""
	@echo "Luego ejecuta master:"
	@cd p2p/base && python master.py

run-p2p-async:
	@echo "Ejecutando P2P Async - inicia slave en otra terminal:"
	@echo "  cd p2p/async && python slave.py"
	@echo ""
	@echo "Luego ejecuta master:"
	@cd p2p/async && python master.py

run-data-base:
	@echo "Ejecutando Data Base - inicia slave en otra terminal:"
	@echo "  cd data/base && python slave.py"
	@echo ""
	@echo "Luego ejecuta master:"
	@cd data/base && python master.py

run-data-async:
	@echo "Ejecutando Data Async - inicia slave en otra terminal:"
	@echo "  cd data/async && python slave.py"
	@echo ""
	@echo "Luego ejecuta master:"
	@cd data/async && python master.py

clean:
	@echo "Limpiando archivos generados..."
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -f received_* 2>/dev/null || true
	@rm -f reporte_* 2>/dev/null || true
	@echo "Limpieza completada"
