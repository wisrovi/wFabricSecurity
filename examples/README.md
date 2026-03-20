# Ejemplos de wFabricSecurity

Este directorio contiene ejemplos funcionales que demuestran cómo usar la librería **wFabricSecurity** para seguridad distribuida con Hyperledger Fabric.

## Estructura de Ejemplos

```
examples/
├── json/           # Ejemplos con datos JSON
│   ├── base/      # Síncrono
│   └── async/     # Asíncrono
├── image/          # Ejemplos con imágenes
│   ├── base/
│   └── async/
├── p2p/            # Ejemplos con datos sensibles (P2P)
│   ├── base/
│   └── async/
├── data/           # Ejemplos con archivos binarios
│   ├── base/
│   └── async/
├── test/           # Tests automatizados
│   ├── conftest.py
│   ├── test_library.py   # Tests de la librería core
│   ├── test_json.py
│   ├── test_image.py
│   ├── test_p2p.py
│   └── test_data.py
├── requirements.txt
└── Makefile
```

## Tipos de Ejemplos

### 1. JSON (json/)
Envía y recibe datos JSON estructurados auditados en Fabric.

**Casos de uso:**
- APIs REST con auditoría
- Intercambio de datos estructurados
- Microservicios con registro inmutable

**Puerto:** 8001

**Ejecución:**
```bash
# Terminal 1 - Slave
cd examples/json/base
python slave.py

# Terminal 2 - Master
cd examples/json/base
python master.py
```

### 2. Image (image/)
Procesa imágenes con auditoría completa en Fabric.

**Casos de uso:**
- Procesamiento de imágenes médico
- Verificación de documentos
- Análisis de imágenes con auditoría

**Puerto:** 8002

**Ejecución:**
```bash
# Terminal 1 - Slave
cd examples/image/base
python slave.py

# Terminal 2 - Master
python master.py
```

### 3. P2P (p2p/)
Manejo de datos sensibles (tarjetas, contraseñas) con auditoría.

**Casos de uso:**
- Procesamiento de pagos
- Manejo de credenciales
- Datos personales sensibles

**Puerto:** 8003

**Ejecución:**
```bash
# Terminal 1 - Slave
cd examples/p2p/base
python slave.py

# Terminal 2 - Master
python master.py
```

### 4. Data (data/)
Envío y procesamiento de archivos binarios con auditoría.

**Casos de uso:**
- Reportes PDF firmados
- Documentos legales
- Archivos de configuración

**Puerto:** 8004

**Ejecución:**
```bash
# Terminal 1 - Slave
cd examples/data/base
python slave.py

# Terminal 2 - Master
python master.py
```

## Variantes (base vs async)

### Base (síncrono)
- Usa `requests` para HTTP
- Más simple de entender
- Adecuado para scripts y CLI

### Async (asíncrono)
- Usa `httpx` con async/await
- Mejor rendimiento con múltiples requests
- Adecuado para servidores y alta concurrencia

## Arquitectura de cada Ejemplo

```
┌─────────────┐                    ┌─────────────┐
│   MASTER    │ ──── HTTP POST ───► │   SLAVE     │
│             │                     │  (FastAPI)  │
│ - Genera    │                     │ - Verifica  │
│   hash_a    │                     │ - Procesa   │
│ - Firma     │                     │ - Genera    │
│ - Envía     │ ◄─── Response ─────│   hash_b    │
│             │                     │ - Firma     │
└─────────────┘                     └─────────────┘
       │                                    │
       │         ┌─────────────┐            │
       └────────►│  Fabric     │◄───────────┘
                 │  Gateway    │
                 │             │
                 │ - Register  │
                 │   Task      │
                 │ - Complete  │
                 │   Task      │
                 └─────────────┘
```

## Flujo de una Transacción

1. **Master** genera `hash_a` del payload
2. **Master** firma `hash_a` con su clave privada (ECDSA)
3. **Master** envía datos + firma al Slave via HTTP
4. **Slave** verifica firma del Master
5. **Slave** procesa y genera `hash_b` del resultado
6. **Slave** firma `hash_b` con su clave privada
7. **Slave** registra en Fabric (`CompleteTask`)
8. **Slave** responde al Master
9. **Master** verifica firma del Slave
10. **Master** registra en Fabric (`RegisterTask`)

## Tests

Los tests verifican que todas las funcionalidades работают correctamente.

### Ejecutar todos los tests (core):
```bash
cd examples
make test
```

### Tests específicos:
```bash
make test-core     # Tests de la librería
make test-json    # Tests de JSON
make test-image   # Tests de Image
make test-p2p     # Tests de P2P
make test-data    # Tests de Data
```

### Tests completos (incluyendo integration):
```bash
make test-all
```

## Configuración

### Variables de entorno:

```bash
# Puerto del peer de Fabric
export FABRIC_PEER_URL=localhost:7051

# Path al MSP (Membership Service Provider)
export FABRIC_MSP_PATH=/path/to/msp

# URL del slave (para el master)
export SLAVE_URL=http://127.0.0.1:8001/process
```

### Identidades

Cada ejemplo usa su propia identidad configurada en el MSP:

- **Master**: Identidad del Master (clave privada + certificado)
- **Slave**: Identidad del Slave (clave privada + certificado)

Las identidades se cargan automáticamente desde el directorio del MSP.

## Code Signing

Cada ejemplo soporta **verificación de integridad de código**:

```python
# Registrar el código al iniciar
security.register_code(["master.py"], "1.0.0")

# Verificar antes de operaciones sensibles
security.verify_code(["master.py"])
```

Si el código es modificado después del registro, la verificación fallará con `CodeIntegrityError`.

## Dependencias

```
fastapi        # API del slave
uvicorn        # Servidor ASGI
requests       # HTTP síncrono
httpx          # HTTP asíncrono
pillow         # Procesamiento de imágenes
pytest         # Testing
```

Instalar con:
```bash
make install
```

## Verificación de Estado de Fabric

```bash
make test-fabric
```

Esto verifica que los contenedores de Docker de Fabric estén corriendo.

## Troubleshooting

### "Connection refused"
- Verifica que el slave esté corriendo en el puerto correcto
- Verifica que no haya otro proceso usando ese puerto

### "Chaincode no funcional"
- Los ejemplos funcionan con almacenamiento local si el chaincode no está disponible
- Para usar chaincode real: `cd ../enviroment && make network`

### Tests fallan
- Asegúrate de tener las dependencias instaladas: `make install`
- Verifica que el MSP path sea correcto

## Créditos

- **Master**: Genera y firma la transacción inicial
- **Slave**: Procesa y firma la respuesta
- **Fabric Gateway**: Maneja la comunicación con Hyperledger Fabric
- **ECDSA**: Algoritmo de firma criptográfica
