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
│  │  Workers  │    │  (API)   │                                    │
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

### Opción 2: Configuración de variables de entorno

Los ejemplos usan Hyperledger Fabric real. Configura las variables de entorno:

```bash
# Peer URL (puerto mapeado del contenedor)
export FABRIC_PEER_URL=localhost:7051

# Path al MSP del admin (dentro del contenedor CLI)
export FABRIC_MSP_PATH=/home/wisrovi/Documentos/wFabricSecurity/enviroment/organizations/peerOrganizations/org1.net/users/Admin@org1.net/msp
```

### Verificar estado de la red

```bash
cd enviroment
make status
```

## Configuración de Puertos

Los slaves corren en diferentes puertos:

| Ejemplo | Puerto | Descripción |
|---------|--------|-------------|
| json/base | 8001 | JSON síncrono |
| json/async | 8001 | JSON asíncrono |
| image/base | 8002 | Imágenes síncrono |
| image/async | 8002 | Imágenes asíncrono |
| p2p/base | 8003 | P2P síncrono |
| p2p/async | 8003 | P2P asíncrono |
| data/base | 8004 | Archivos síncrono |
| data/async | 8004 | Archivos asíncrono |

**Nota**: Ejecutar un Slave a la vez (o cambiar puertos para ejecutar varios).
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

Todos los ejemplos usan **Hyperledger Fabric real** por defecto.

### JSON - Datos Simples

```bash
# Terminal 1 - Slave (puerto 8001)
cd examples/json/base
python slave.py

# Terminal 2 - Master
cd examples/json/base
python master.py
```

### JSON Async - Datos Asíncronos

```bash
# Terminal 1 - Slave
cd examples/json/async
python slave.py

# Terminal 2 - Master
python master.py
```

### Imagen - Procesamiento de Imágenes

```bash
# Terminal 1 - Slave (puerto 8002)
cd examples/image/base
python slave.py

# Terminal 2 - Master
python master.py
```

### P2P - Datos Sensibles

```bash
# Terminal 1 - Slave (puerto 8003)
cd examples/p2p/base
python slave.py

# Terminal 2 - Master
python master.py
```

### Data - Archivos Binarios

```bash
# Terminal 1 - Slave (puerto 8004)
cd examples/data/base
python slave.py

# Terminal 2 - Master
python master.py
```

**Nota**: Ejecutar un Slave a la vez. Cambiar puertos en los archivos si necesitas ejecutar varios.

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

### Fabric Real (Por Defecto)

Todos los ejemplos usan **Hyperledger Fabric real** para almacenar transacciones de forma inmutable.

**Requisitos:**
1. Red Docker corriendo: `cd enviroment && make network`
2. Chaincode instalado: `make install-chaincode && make instantiate-chaincode`
3. Variables de entorno configuradas (ver arriba)

**Estado de la red:**
```bash
cd enviroment && make status
```

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
