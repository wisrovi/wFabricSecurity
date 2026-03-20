# Ejemplo JSON - Async

## Archivos

- `master.py` - Master async que envía JSON usando `httpx`
- `slave.py` - Slave FastAPI async que recibe y procesa

## Uso

### Terminal 1 - Slave:
```bash
cd examples/json/async
python slave.py
```

### Terminal 2 - Master:
```bash
cd examples/json/async
python master.py
```
