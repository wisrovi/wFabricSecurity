# Ejemplo JSON - Base (Síncrono)

## Archivos

- `master.py` - Master que envía JSON usando `requests`
- `slave.py` - Slave FastAPI que recibe y procesa

## Uso

### Terminal 1 - Slave:
```bash
cd examples/json/base
python slave.py
```

### Terminal 2 - Master:
```bash
cd examples/json/base
python master.py
```
