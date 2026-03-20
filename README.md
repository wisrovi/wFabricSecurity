# wFabricSecurity

**Librería Python para seguridad distribuida en Hyperledger Fabric usando un patrón Master-Slave con auditoría inmutable.**

## Descripción

wFabricSecurity permite implementar un sistema de **auditoría criptográfica distribuida** donde las tareas master delegan trabajo a slaves, pero ambos registran pruebas inmutables en Hyperledger Fabric para garantizar:

- **No-repudio**: Ninguna parte puede negar haber participado
- **Verificabilidad**: Cualquiera puede verificar la integridad
- **Inmutabilidad**: Los registros no pueden ser alterados

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                    RED HYPERLEDGER FABRIC                       │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  Master  │───►│  Peer    │───►│ Orderer  │───►│ CouchDB  │  │
│  │  (Core)  │    │          │    │          │    │          │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│       │               │                                    ▲    │
│       │          Private                                 │      │
│       │          Data                                    │      │
│       │          (P2P)                              Ledger     │
│       │               │                             (Hash)    │
│       ▼               ▼                                    │      │
│  ┌──────────┐    ┌──────────┐ ───────────────────────────┘     │
│  │  Slaves  │◄──►│  Gateway │                                    │
│  │ Workers  │    │  (API)   │                                    │
│  └──────────┘    └──────────┘                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Flujo de Trabajo

1. **Master**: Genera hash SHA-256 del payload
2. **Master**: Registra dato privado (P2P) + Hash en Ledger
3. **Master**: Firma hash y envía a Slave (vía HTTP)
4. **Slave** (FastAPI): Recibe, verifica firma, procesa
5. **Slave**: Registra resultado en Ledger
6. **Slave**: Devuelve resultado + firma al Master
7. **Master**: Verifica firma del Slave

## Instalación Rápida

### Opción 1: Instalación completa con Fabric (Production)

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate

# 2. Instalar librería
pip install -e .

# 3. Preparar Hyperledger Fabric
cd enviroment
make setup      # Genera certificados y artefactos
make up         # Levanta la red Docker
make network    # Configura canal y chaincode
cd ..

# 4. Instalar dependencias de ejemplos
pip install -r examples/requirements.txt
```

### Opción 2: Ejemplos standalone (sin Fabric real)

Los ejemplos pueden ejecutarse en modo **mock** sin necesidad de Hyperledger Fabric:

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate

# 2. Instalar librería
pip install -e .

# 3. Instalar dependencias de ejemplos
pip install -r examples/requirements.txt

# 4. Ejecutar ejemplos (usan modo mock por defecto)
```

## Estructura del Proyecto

```
wFabricSecurity/
├── wFabricSecurity/        # Paquete Python
│   ├── __init__.py
│   └── fabric_security/    # Módulo principal
│       └── fabric_security.py
├── examples/               # Ejemplos funcionales
│   ├── requirements.txt    # Dependencias
│   ├── json/              # Datos JSON
│   │   ├── base/          # Síncrono
│   │   └── async/         # Async
│   ├── image/             # Imágenes
│   │   ├── base/
│   │   └── async/
│   ├── p2p/               # Datos sensibles
│   │   ├── base/
│   │   └── async/
│   └── data/              # Archivos binarios
│       ├── base/
│       └── async/
├── enviroment/            # Hyperledger Fabric
│   ├── setup.sh           # Script de configuración
│   ├── Makefile           # Comandos便捷
│   ├── docker-compose.yaml # Servicios Docker
│   ├── chaincode/         # Chaincode Go
│   ├── organizations/     # Certificados
│   └── channel-artifacts/ # Artefactos del canal
├── requirements.txt       # Dependencias de la librería
└── Makefile              # Comandos de la raíz
```

## Uso de la Librería

### Uso Básico (Síncrono)

```python
from fabric_security import FabricSecurity

# Crear instancia
security = FabricSecurity(
    peer_endpoint="peer0.org1.net:7051",
    identity_path="/path/to/msp",
    gateway_url="peer0.org1.net:7051"
)

# Registrar una tarea
task_id = "task-001"
hash_a = security.hash_data({"task": "data"})
sig = security.sign(task_id, hash_a)

# Almacenar en Fabric
security.store_task(task_id, hash_a, sig)

# Recuperar
task = security.get_task(task_id)
```

### Uso Async

```python
import asyncio
from fabric_security import FabricSecurity

async def main():
    security = FabricSecurity(
        peer_endpoint="peer0.org1.net:7051",
        identity_path="/path/to/msp",
        gateway_url="peer0.org1.net:7051"
    )
    
    hash_a = await security.hash_data_async({"task": "data"})
    result = await security.store_task_async(task_id, hash_a, signature)
    
asyncio.run(main())
```

## Ejemplos

### JSON - Datos Simples

```bash
# Terminal 1 - Slave (recibe tareas)
cd examples/json/base
python slave.py

# Terminal 2 - Master (envía tareas)
cd examples/json/base
python master.py
```

### Imagen - Procesamiento de Imágenes

```bash
# Terminal 1 - Slave
cd examples/image/base
python slave.py

# Terminal 2 - Master
python master.py
```

### P2P - Datos Sensibles

```bash
# Terminal 1 - Slave
cd examples/p2p/base
python slave.py

# Terminal 2 - Master
python master.py
```

### Data - Archivos Binarios

```bash
# Terminal 1 - Slave
cd examples/data/base
python slave.py

# Terminal 2 - Master
python master.py
```

### Ejemplos con Fabric Real

Los ejemplos en `examples/fabric/` usan Hyperledger Fabric real en lugar de mock:

```bash
# 1. Asegúrate de que la red Fabric esté corriendo
cd enviroment
make network
make install-chaincode
# Nota: make instantiate-chaincode puede requerir configuración adicional

# 2. Configurar variables de entorno
export FABRIC_PEER_URL=peer0.org1.net:7051
export FABRIC_MSP_PATH=$(pwd)/organizations/peerOrganizations/org1.net/users/Admin@org1.net/msp

# 3. Terminal 1 - Slave (puerto 8002)
cd examples/fabric/json
python slave.py

# 4. Terminal 2 - Master
cd examples/fabric/json
python master.py
```

**Diferencia entre mock y real:**
- **Mock**: Los datos se almacenan en memoria (se pierden al reiniciar)
- **Real**: Los datos se registran en Hyperledger Fabric (permanentes e inmutables)

## Comandos del Entorno (carpeta enviroment)

```bash
make help          # Ver todos los comandos
make setup         # Generar certificados y artefactos
make up            # Levantar red Docker
make down          # Detener red
make clean         # Limpiar todo
make network       # Configurar canal
make install-chaincode  # Instalar chaincode
```

## Comandos de la Raíz

```bash
make install-dev   # Instalar librería en desarrollo
make install-pypi  # Instalar desde PyPI
make lint          # Verificar código
make clean         # Limpiar archivos generados
```

## Configuración de Fabric

### Variables de Entorno

```bash
export ORDERER_HOST=orderer.net
export ORDERER_PORT=7050
export PEER_HOST=peer0.org1.net
export PEER_PORT=7051
export CHANNEL_NAME=mychannel
export CHAINCODE_NAME=tasks
```

### Arquitectura de la Red

```
┌──────────────────────────────────────────────┐
│              Red Docker "fabric"            │
│                                              │
│  ┌──────────────┐      ┌──────────────┐   │
│  │ orderer.net  │      │ peer0.org1.net│   │
│  │   :7050      │◄────►│    :7051      │   │
│  └──────────────┘      └──────────────┘   │
│                              │              │
│                              ▼              │
│                      ┌──────────────┐      │
│                      │   couchdb0   │      │
│                      │    :5984     │      │
│                      └──────────────┘      │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │              cli                      │   │
│  │  (Administración y chaincode)       │   │
│  └──────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
```

## Dependencias

### Librería principal (requirements.txt)
- `fabric-gateway-python` - Cliente de Hyperledger Fabric
- `cryptography` - Criptografía
- `ecdsa` - Firmas ECDSA
- `loguru` - Logging

### Ejemplos (examples/requirements.txt)
- `fastapi` - API del Slave
- `uvicorn` - Servidor ASGI
- `requests` - Cliente HTTP síncrono
- `httpx` - Cliente HTTP async
- `pillow` - Procesamiento de imágenes

## Estado Actual

### Modo Mock (Recomendado para desarrollo)

Los ejemplos funcionan completamente en **modo mock** sin necesidad de Hyperledger Fabric real:

```bash
# Los ejemplos usan use_mock=True por defecto
python examples/json/base/master.py    # ✓ Funciona
python examples/json/base/slave.py     # ✓ Funciona
```

### Red Fabric Real (Avanzado)

La red Docker se configura con `cd enviroment && make network`, pero el chaincode requiere configuración adicional.

**Estado actual:**
- ✓ Red Docker configurable (orderer, peer, couchdb, cli)
- ✓ Canal y chaincode definiables
- ⚠ Instanciación puede requerir ajustes según el entorno

**Para usar con Fabric real:**
1. Levantar red: `cd enviroment && make network`
2. Instalar chaincode: `make install-chaincode`
3. Usar ejemplos en `examples/fabric/` con `FABRIC_PEER_URL` y `FABRIC_MSP_PATH`

## Troubleshooting

### Problema: "No such host"

```bash
# Verificar que la red Docker existe
docker network ls | grep fabric

# Crear la red si no existe
docker network create fabric
```

### Problema: "Connection refused"

```bash
# Verificar que los contenedores están corriendo
docker ps

# Reiniciar los contenedores
make down && make up
```

### Problema: Chaincode no encontrado

```bash
cd enviroment
make install-chaincode
```

### Problema: Instanciación falla con "implicit policy evaluation failed"

Este es un problema conocido con la configuración de políticas del canal. Los ejemplos funcionan con modo mock.

## Licencia

MIT - Ver archivo `LICENSE`
