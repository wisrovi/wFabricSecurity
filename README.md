# wFabricSecurity

**Sistema de Seguridad Zero Trust para Hyperledger Fabric**

Librería Python que implementa un sistema completo de auditoría criptográfica distribuida con verificación de identidad, integridad de código, permisos de comunicación y validación de mensajes.

## Características Principales

- 🔐 **Integridad de Código**: Verificación SHA-256 del código fuente
- 🔑 **Firmas ECDSA**: Criptografía de curva elíptica para firmar mensajes
- 🛡️ **Permisos de Comunicación**: Control de acceso Zero Trust
- 📝 **Integridad de Mensajes**: Verificación de que los datos no fueron alterados
- 📦 **Tipos de Datos**: JSON, Imágenes, Datos sensibles P2P, Archivos
- 🏢 **Participantes**: Gestión de identidades con certificados X.509
- ⚡ **Rate Limiting**: Protección contra ataques DoS con token bucket
- 🔄 **Retry Logic**: Reintentos automáticos con exponential backoff
- 💾 **Certificate Caching**: Cache LRU con TTL para certificados
- ⚙️ **Configuración Flexible**: YAML o variables de entorno

## Arquitectura Zero Trust

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    VALIDACIONES DE SEGURIDAD                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. ¿El CÓDIGO del remitente es íntegro?                              │
│     → Verifica code_hash contra Fabric                                   │
│                                                                         │
│  2. ¿El REMITENTE tiene PERMISO de hablar con el DESTINATARIO?          │
│     → Verifica tabla de permisos                                        │
│                                                                         │
│  3. ¿La FIRMA del mensaje es válida?                                    │
│     → Verifica ECDSA con certificado del remitente                      │
│                                                                         │
│  4. ¿El MENSAJE no fue ALTERADO?                                       │
│     → Verifica hash SHA-256 del contenido                               │
│                                                                         │
│  5. ¿El CÓDIGO del destinatario es íntegro?                            │
│     → Auto-verificación antes de procesar                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Instalación Rápida

```bash
# 1. Clonar repositorio
git clone https://github.com/wisrovi/wFabricSecurity.git
cd wFabricSecurity

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate

# 3. Instalar librería
pip install -e .

# 4. Preparar Hyperledger Fabric
cd enviroment
make setup
make up
cd ..

# 5. Instalar dependencias de ejemplos
pip install -r examples/requirements.txt
```

## Arquitectura Modular

```
wFabricSecurity/fabric_security/
├── __init__.py                    # Exports públicos
├── config/
│   ├── __init__.py
│   ├── settings.py                # Configuración centralizada
│   ├── defaults.py               # Valores por defecto
│   └── config.yaml              # Ejemplo de configuración
├── core/
│   ├── __init__.py
│   ├── exceptions.py              # Todas las excepciones (8 tipos)
│   ├── models.py                  # Message, Participant, Task
│   └── enums.py                  # CommunicationDirection, DataType, etc.
├── crypto/
│   ├── __init__.py
│   ├── hashing.py                 # HashingService
│   ├── signing.py                 # SigningService (ECDSA)
│   └── identity.py                # IdentityManager (certificados con cache)
├── fabric/
│   ├── __init__.py
│   ├── gateway.py                 # FabricGateway
│   ├── network.py                # FabricNetwork
│   └── contract.py               # FabricContract
├── security/
│   ├── __init__.py
│   ├── integrity.py               # IntegrityVerifier
│   ├── permissions.py            # PermissionManager
│   ├── messages.py               # MessageManager (con TTL)
│   ├── decorators.py             # @master_audit, @slave_verify
│   ├── rate_limiter.py           # RateLimiter (token bucket)
│   └── retry.py                  # @with_retry, RetryContext
├── storage/
│   ├── __init__.py
│   ├── local.py                  # LocalStorage (fallback)
│   └── fabric_storage.py         # FabricStorage (blockchain)
├── cli.py                        # CLI tool
└── fabric_security.py            # FabricSecurity, FabricSecuritySimple
```

### Módulos Principales

| Módulo | Descripción |
|--------|-------------|
| `core` | Excepciones, modelos de datos, enums |
| `crypto` | Servicios criptográficos (hash, firma, identidad) |
| `fabric` | Comunicación con Hyperledger Fabric |
| `security` | Verificación de integridad, permisos, rate limiting |
| `storage` | Almacenamiento local y en Fabric |
| `config` | Configuración centralizada (YAML + env vars) |

## Mejoras Implementadas

- **Type hints** completos en todos los métodos
- **Retry logic** con exponential backoff (`@with_retry`)
- **Rate limiting** con token bucket (`RateLimiter`)
- **Message expiration** con TTL y limpieza automática
- **Participant revocation** para revocar participantes comprometidos
- **Certificate caching** con LRU cache y TTL
- **Configuración** via `config.yaml` o variables de entorno
- **CLI tool** con comandos: register, verify, send, receive, etc.

## Uso Básico

### Sistema Zero Trust Completo

```python
from wFabricSecurity import FabricSecurity

security = FabricSecurity(
    me="Master",
    msp_path="/path/to/msp"
)

# 1. Registrar identidad y código
security.register_identity()
security.register_code(["master.py"], "1.0.0")

# 2. Registrar permisos de comunicación
security.register_communication("CN=Master", "CN=Slave")

# 3. Crear mensaje firmado
message = security.create_message(
    recipient="CN=Slave",
    content='{"operacion": "proceso_datos"}'
)

# 4. Verificar mensaje recibido
if security.verify_message(message):
    print("✅ Mensaje válido")
```

### Decoradores Master-Slave

```python
# MASTER - Envía tareas auditadas
@security.master_audit(task_prefix="TASK", trusted_slaves=["CN=Slave"])
def enviar_tarea(payload, task_id, hash_a, sig, my_id, message):
    return enviar_a_slave(payload)

# SLAVE - Procesa tareas con verificación
@security.slave_verify(trusted_masters=["CN=Master"])
def procesar_tarea(payload):
    return procesar(payload)
```

### Sistema Simplificado

```python
from wFabricSecurity import FabricSecuritySimple

security = FabricSecuritySimple(me="MiServicio")

@security.master_audit(task_prefix="TASK", trusted_slaves=["SLAVE"])
def mi_tarea(payload, task_id, hash_a, sig, my_id):
    return {"resultado": "procesado"}
```

## Ejemplos de Uso

### Datos JSON

```python
payload = {
    "tipo": "analisis_datos",
    "datos": {
        "usuario": "juan_perez",
        "email": "juan@example.com",
        "edad": 30
    }
}
# El hash SHA-256 se calcula automáticamente
# La firma ECDSA se genera con la clave privada
```

### Imágenes

```python
import base64

with open("imagen.png", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

# La imagen se transmite con hash de verificación
# El slave verifica la integridad antes de procesar
```

### Datos Sensibles (P2P)

```python
payload = {
    "tipo": "datos_sensibles",
    "datos": {
        "tarjeta": "**** **** **** 1234",
        "cvv": "***",
        "propietario": "Juan Perez"
    }
}
# Requiere permisos específicos para este tipo de datos
```

### Archivos Binarios

```python
with open("documento.pdf", "rb") as f:
    file_data = base64.b64encode(f.read()).decode()

# El archivo se transmite como base64
# Hash SHA-256 garantiza integridad
```

## Tests

```bash
cd examples

# Ejecutar todos los tests
make test

# Tests específicos
make test-core          # Tests de librería core (228 tests)
make test-json         # Tests de JSON
make test-image        # Tests de imágenes
make test-p2p          # Tests P2P
make test-data         # Tests de archivos

# Generar reporte HTML
make report
```

## Reportes de Tests

Genera reportes profesionales en HTML con:

- 📅 Fecha y hora de ejecución
- 📊 Estadísticas de resultados
- 🔐 Detalle de cada funcionalidad validada
- 📦 Tipos de datos soportados
- 📈 Gráfico visual de distribución
- 🎨 Diseño profesional con modo oscuro

```bash
make report          # Generar reporte
make view-report     # Ver último reporte
```

Los reportes se guardan en: `examples/test/reports/test_report_YYYYMMDD_HHMMSS.html`

## Estructura del Proyecto

```
wFabricSecurity/
├── wFabricSecurity/           # Paquete Python
│   └── fabric_security/      # Módulo principal
│       ├── config/          # Configuración
│       ├── core/            # Excepciones, modelos, enums
│       ├── crypto/          # Criptografía
│       ├── fabric/          # Comunicación Fabric
│       ├── security/        # Seguridad
│       ├── storage/         # Almacenamiento
│       └── fabric_security.py # Sistema Zero Trust
├── test/                     # Tests de librería (228 tests)
├── examples/                 # Ejemplos funcionales
│   ├── json/                 # Ejemplos JSON
│   ├── image/                # Ejemplos de imágenes
│   ├── p2p/                 # Ejemplos P2P
│   ├── data/                 # Ejemplos de archivos
│   ├── test/                 # Tests automatizados
│   │   ├── test_library.py   # Tests core
│   │   ├── test_zero_trust.py # Tests Zero Trust
│   │   └── reports/          # Reportes HTML
│   └── Makefile              # Comandos de examples
├── enviroment/               # Hyperledger Fabric
│   ├── docker-compose.yaml   # Servicios Docker
│   ├── chaincode/            # Chaincode Go
│   └── organizations/        # Certificados
├── README.md                 # Este archivo
└── requirements.txt          # Dependencias
```

## Clases Principales

### Message
Representa un mensaje firmado con remitente, destinatario, hash y firma.

### Participant
Representa un participante con identidad, code_hash, versión y permisos.

### Excepciones
- `CodeIntegrityError`: El código fue modificado
- `PermissionDeniedError`: Sin permiso de comunicación
- `MessageIntegrityError`: El mensaje fue alterado
- `SignatureError`: La firma es inválida
- `RateLimitError`: Se excedió el rate limit
- `RevocationError`: Participante revocado

## Configuración

### Variables de Entorno

```bash
export FABRIC_PEER_URL=localhost:7051
export FABRIC_MSP_PATH=/path/to/msp
export FABRIC_MSP_PATH=/path/to/users/Admin@org1.net/msp
```

### config.yaml

```yaml
local_data_dir: /tmp/fabric_security_data
fabric_channel: mychannel
fabric_chaincode: tasks
retry_max_attempts: 3
rate_limit_requests_per_second: 100
rate_limit_burst: 200
message_ttl_seconds: 3600
cert_cache_size: 100
cert_cache_ttl_seconds: 3600
```

### MSP (Membership Service Provider)

```
organizations/peerOrganizations/org1.net/users/
├── Admin@org1.net/msp/        # Admin
├── Master@org1.net/msp/        # Identidad Master
└── Slave@org1.net/msp/         # Identidad Slave
    ├── signcerts/cert.pem      # Certificado (clave pública)
    └── keystore/key.pem         # Clave privada
```

## Comandos del Entorno

```bash
cd enviroment

make setup        # Generar certificados y artefactos
make up           # Levantar red Docker
make down         # Detener red
make clean        # Limpiar todo
make status      # Ver estado de la red
```

## Documentación Adicional

- [README de Examples](examples/README.md) - Documentación detallada de ejemplos
- [Tests](examples/test/) - Suite completa de tests automatizados (228 tests)
- [Reportes](examples/test/reports/) - Reportes HTML de tests

## Cobertura de Tests

```
test/test_library.py          # 228 tests - 84% cobertura
examples/test/               # 96 tests - ejemplos funcionales
```

## Licencia

MIT License
