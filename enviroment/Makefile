.PHONY: help setup up down clean logs network install-chaincode status

BIN_DIR := $(shell pwd)/bin
export PATH := $(BIN_DIR):$(PATH)

DOMAIN := net
ORDERER_HOST := orderer.$(DOMAIN)
PEER_HOST := peer0.org1.$(DOMAIN)

help:
	@echo "wFabricSecurity - Entorno Hyperledger Fabric"
	@echo ""
	@echo "Uso: make [comando]"
	@echo ""
	@echo "Comandos:"
	@echo "  setup            - Genera certificados y configuración"
	@echo "  up               - Levanta la red Docker (sin chaincode)"
	@echo "  install-chaincode - Instala y activa el chaincode"
	@echo "  network          - setup + up"
	@echo "  down             - Detiene la red Docker"
	@echo "  clean            - Limpia todo"
	@echo "  logs             - Ver logs"
	@echo "  status           - Ver estado de la red"

setup:
	@chmod +x setup.sh
	@./setup.sh

up: setup
	@echo ">> Creando red Docker..."
	@docker network rm fabric 2>/dev/null || true
	@docker network create fabric 2>/dev/null || true
	@docker-compose -f docker-compose-fabric.yaml up -d
	@echo ">> Esperando servicios (15s)..."
	@sleep 15
	@echo ">> Uniando peer al canal..."
	@docker exec cli peer channel fetch oldest /tmp/mychannel.block -c mychannel --orderer $(ORDERER_HOST):7050 || true
	@docker exec cli peer channel join -b /tmp/mychannel.block || true
	@echo "✓ Red iniciada (usa modo mock para testing)"

install-chaincode:
	@echo ">> Empaquetando chaincode..."
	@docker exec -e GOFLAGS="-mod=mod" cli peer lifecycle chaincode package /tmp/tasks.tar.gz --path /opt/gopath/src/github.com/hyperledger/fabric/peer/chaincode/tasks --lang golang --label tasks_1 || true
	@echo ">> Instalando chaincode..."
	@docker exec cli peer lifecycle chaincode install /tmp/tasks.tar.gz || true
	@echo ">> Obteniendo ID del chaincode..."
	@docker exec cli peer lifecycle chaincode queryinstalled || true
	@echo "Nota: Para instantiate, usa 'make instantiate-chaincode'"

instantiate-chaincode:
	@PACKAGE_ID=$$(docker exec cli peer lifecycle chaincode queryinstalled 2>/dev/null | grep "tasks_1" | sed 's/Package ID: tasks_1:\([^,]*\).*/\1/') && \
	echo ">> Aprobando chaincode (package: tasks_1:$$PACKAGE_ID)..." && \
	docker exec cli peer lifecycle chaincode approveformyorg -C mychannel -n tasks --version 1 --package-id tasks_1:$$PACKAGE_ID --sequence 1 -o $(ORDERER_HOST):7050 --tls=false --cafile /etc/hyperledger/fabric/msp/tlscacerts/tlsroot.pem && \
	echo ">> Commiteando chaincode..." && \
	docker exec cli peer lifecycle chaincode commit -C mychannel -n tasks --version 1 --sequence 1 -o $(ORDERER_HOST):7050 --tls=false --cafile /etc/hyperledger/fabric/msp/tlscacerts/tlsroot.pem && \
	echo ">> Inicializando chaincode..." && \
	docker exec cli peer chaincode invoke -C mychannel -n tasks --isInit -c '{"function":"init","Args":[]}' -o $(ORDERER_HOST):7050 --tls=false --cafile /etc/hyperledger/fabric/msp/tlscacerts/tlsroot.pem || true && \
	echo "✓ Chaincode instalado"

down:
	@echo ">> Deteniendo red..."
	@docker-compose -f docker-compose-fabric.yaml down -v --remove-orphans 2>/dev/null || true
	@docker network rm fabric 2>/dev/null || true
	@echo "✓ Red detenida"

clean:
	@echo ">> Limpiando..."
	@docker-compose -f docker-compose-fabric.yaml down -v --remove-orphans 2>/dev/null || true
	@docker network rm fabric 2>/dev/null || true
	@rm -rf organizations/ channel-artifacts/*.block channel-artifacts/*.tx crypto-config.yaml configtx.yaml tasks.tar.gz 2>/dev/null || true
	@mkdir -p channel-artifacts
	@mkdir -p organizations/peerOrganizations organizations/ordererOrganizations
	@echo "✓ Limpieza completada"

logs:
	@docker-compose -f docker-compose-fabric.yaml logs -f

status:
	@echo "=== Estado de la Red ==="
	@docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "orderer|peer|cli|couch" || echo "No hay contenedores corriendo"
	@echo ""
	@echo "=== Canal ==="
	@docker exec cli peer channel list 2>/dev/null || echo "CLI no disponible"
	@echo ""
	@echo "=== Chaincode ==="
	@docker exec cli peer lifecycle chaincode queryinstalled 2>/dev/null || echo "No hay chaincode instalado"
	@echo ""
	@echo "Nota: Los ejemplos usan modo mock por defecto."

network: up
	@echo "=============================================="
	@echo "  ✓ Red Hyperledger Fabric lista"
	@echo "=============================================="
	@docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "orderer|peer|cli|couch" || true
