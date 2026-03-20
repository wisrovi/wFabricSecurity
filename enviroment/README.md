# Entorno Hyperledger Fabric

Este directorio contiene la configuración para una red Hyperledger Fabric de desarrollo.

## Estado Actual

**Funcional:**
- ✅ Orderer funcionando (solo)
- ✅ Red Docker configurada
- ✅ Canal "mychannel" creado
- ✅ Peer0.org1.net unido al canal
- ✅ Chaincode "tasks" instalado

**En desarrollo:**
- ⚙️ Chaincode instantiated (requiere configuración adicional)
- ⚙️ Actualización de anchor peer

## Estructura

```
enviroment/
├── setup.sh              # Script principal de configuración
├── Makefile              # Comandos便捷
├── docker-compose.yaml   # Definición de servicios
├── configtx.yaml        # Configuración de canales
├── crypto-config.yaml   # Configuración de organizaciones
├── chaincode/           # Chaincode Go
│   └── tasks/
│       ├── tasks.go    # Código del chaincode
│       └── go.mod      # Módulos Go
├── organizations/       # Certificados (generados)
│   ├── ordererOrganizations/
│   └── peerOrganizations/
├── channel-artifacts/   # Artefactos (generados)
└── bin/                # Binarios Fabric (descargados)
```

## Comandos Rápidos

```bash
# Configuración inicial completa
make setup && make up && make network

# Solo levantar/redesplegar
make down && make up

# Instalar chaincode
make install-chaincode

# Ver estado de la red
docker ps
docker logs orderer.net
docker logs peer0.org1.net
```

## Solución de Problemas

### El orderer no inicia

```bash
# Verificar logs
docker logs orderer.net

# Causa común: genesis block inválido
make clean && make setup && make up
```

### El peer no puede unirse al canal

```bash
# Verificar que el orderer está funcionando
docker logs orderer.net | grep "Beginning to serve"

# Verificar que el canal existe
docker exec cli peer channel list
```

### Chaincode no se ejecuta

```bash
# Reinstalar chaincode
make install-chaincode

# Verificar que está instalado
docker exec cli peer lifecycle chaincode queryinstalled
```

## Configuración de Red

### Hosts (agregar a /etc/hosts si es necesario)

```
127.0.0.1    orderer.net
127.0.0.1    peer0.org1.net
```

### Puertos Expuestos

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| orderer.net | 7050 | Orderer (solo) |
| peer0.org1.net | 7051 | Peer gRPC |
| peer0.org1.net | 7052 | Chaincode |
| peer0.org1.net | 7053 | Event hub |
| couchdb0 | 5984 | CouchDB |

## Configuración TLS

**Estado actual:** TLS deshabilitado para simplificar la configuración.

Para habilitar TLS en producción, modificar:
1. `docker-compose.yaml` - Habilitar variables `CORE_TLS_ENABLED` y `ORDERER_GENERAL_TLS_ENABLED`
2. Regenerar certificados con `make clean && make setup`

## Próximos Pasos

1. Resolver problemas de políticas de canal
2. Completar instalación del chaincode
3. Agregar más organizaciones
4. Configurar RAFT consensus para producción
