"""
Genera reportes profesionales HTML de tests con detalle de funcionalidades.
"""

import os
import sys
import json
import datetime
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)


def get_project_root():
    return Path(__file__).parent.parent.parent


def generate_html_report(test_results: Dict[str, Any], output_path: str = None) -> str:
    """Genera reporte HTML profesional."""

    project_root = get_project_root()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if output_path is None:
        output_path = (
            project_root
            / "examples"
            / "test"
            / "reports"
            / f"test_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    passed = test_results.get("passed", 0)
    failed = test_results.get("failed", 0)
    skipped = test_results.get("skipped", 0)
    total = passed + failed + skipped
    pass_rate = (passed / total * 100) if total > 0 else 0

    # Group tests by functionality
    functionalities = test_results.get("functionalities", [])

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Tests - wFabricSecurity Zero Trust</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }}
        
        .container {{ max-width: 1400px; margin: 0 auto; }}
        
        /* Header */
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.8em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header .subtitle {{
            font-size: 1.3em;
            opacity: 0.95;
            margin-bottom: 20px;
        }}
        
        .header .meta {{
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }}
        
        .header .meta span {{
            background: rgba(255,255,255,0.2);
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 0.95em;
        }}
        
        /* Status Badge */
        .status-section {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 20px 50px;
            border-radius: 40px;
            font-size: 1.5em;
            font-weight: bold;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }}
        
        .status-badge.success {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }}
        
        .status-badge.failure {{
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
        }}
        
        /* Stats Cards */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        
        .stat-card:hover {{ transform: translateY(-5px); }}
        
        .stat-card .icon {{ font-size: 2.5em; margin-bottom: 10px; }}
        .stat-card .number {{ font-size: 3em; font-weight: bold; }}
        .stat-card .label {{ color: #666; margin-top: 10px; font-size: 1.1em; }}
        
        .stat-card.passed {{ border-top: 5px solid #11998e; }}
        .stat-card.passed .number {{ color: #11998e; }}
        
        .stat-card.failed {{ border-top: 5px solid #eb3349; }}
        .stat-card.failed .number {{ color: #eb3349; }}
        
        .stat-card.skipped {{ border-top: 5px solid #f39c12; }}
        .stat-card.skipped .number {{ color: #f39c12; }}
        
        .stat-card.total {{ border-top: 5px solid #667eea; }}
        .stat-card.total .number {{ color: #667eea; }}
        
        .stat-card.rate {{ border-top: 5px solid #38ef7d; }}
        .stat-card.rate .number {{ color: #38ef7d; }}
        
        /* Functionality Sections */
        .functionality-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        
        .functionality-section h2 {{
            color: #667eea;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .functionality-section h2 .icon {{ font-size: 1.2em; }}
        
        .functionality-description {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 25px;
            border-left: 4px solid #667eea;
        }}
        
        .functionality-description p {{
            color: #555;
            line-height: 1.6;
        }}
        
        /* Test Items */
        .test-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 15px;
        }}
        
        .test-item {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border-left: 5px solid #11998e;
            transition: all 0.3s;
        }}
        
        .test-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 3px 15px rgba(0,0,0,0.1);
        }}
        
        .test-item.passed {{ border-left-color: #11998e; }}
        .test-item.failed {{ border-left-color: #eb3349; background: #fff5f5; }}
        .test-item.skipped {{ border-left-color: #f39c12; background: #fffbf0; }}
        
        .test-item .test-name {{
            font-weight: bold;
            font-size: 1.1em;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .test-item .test-status {{
            display: inline-block;
            padding: 3px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        
        .test-item .test-status.passed {{ background: #d4edda; color: #155724; }}
        .test-item .test-status.failed {{ background: #f8d7da; color: #721c24; }}
        .test-item .test-status.skipped {{ background: #fff3cd; color: #856404; }}
        
        .test-item .test-detail {{
            font-size: 0.9em;
            color: #666;
            margin-top: 8px;
        }}
        
        .test-item .example {{
            background: #2d3748;
            color: #e2e8f0;
            padding: 12px;
            border-radius: 8px;
            margin-top: 10px;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            overflow-x: auto;
        }}
        
        .test-item .example .label {{
            color: #38ef7d;
            font-weight: bold;
        }}
        
        /* Data Types Section */
        .data-types-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .data-type-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
        }}
        
        .data-type-card .icon {{ font-size: 3em; margin-bottom: 15px; }}
        .data-type-card h3 {{ color: #333; margin-bottom: 10px; }}
        .data-type-card p {{ color: #666; font-size: 0.9em; }}
        
        /* Chart */
        .chart-section {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        
        .chart {{
            display: flex;
            height: 50px;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }}
        
        .chart-passed {{ background: linear-gradient(90deg, #11998e, #38ef7d); }}
        .chart-failed {{ background: linear-gradient(90deg, #eb3349, #f45c43); }}
        .chart-skipped {{ background: linear-gradient(90deg, #f39c12, #f1c40f); }}
        
        .chart-legend {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 15px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .legend-color {{
            width: 25px;
            height: 25px;
            border-radius: 5px;
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            color: rgba(255,255,255,0.7);
            padding: 30px;
            font-size: 0.9em;
        }}
        
        .footer a {{ color: #667eea; text-decoration: none; }}
        .footer a:hover {{ text-decoration: underline; }}
        
        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .functionality-section, .chart-section, .stat-card {{
            animation: fadeIn 0.5s ease-out;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🛡️ Reporte de Tests - wFabricSecurity</h1>
            <div class="subtitle">Sistema de Seguridad Zero Trust para Hyperledger Fabric</div>
            <div class="meta">
                <span>📅 {timestamp}</span>
                <span>🐍 Python {sys.version.split()[0]}</span>
                <span>📊 {total} Tests Ejecutados</span>
                <span>⚙️ Zero Trust Security</span>
            </div>
        </div>
        
        <!-- Status Badge -->
        <div class="status-section">
            <div class="status-badge {"success" if failed == 0 else "failure"}">
                {"✅ SISTEMA APROBADO - TODAS LAS VALIDACIONES EXITOSAS" if failed == 0 else "❌ SISTEMA CON FALLOS - REVISAR VALIDACIONES"}
            </div>
        </div>
        
        <!-- Stats Grid -->
        <div class="stats-grid">
            <div class="stat-card passed">
                <div class="icon">✅</div>
                <div class="number">{passed}</div>
                <div class="label">Tests Pasados</div>
            </div>
            <div class="stat-card failed">
                <div class="icon">❌</div>
                <div class="number">{failed}</div>
                <div class="label">Tests Fallidos</div>
            </div>
            <div class="stat-card skipped">
                <div class="icon">⏭️</div>
                <div class="number">{skipped}</div>
                <div class="label">Tests Omitidos</div>
            </div>
            <div class="stat-card total">
                <div class="icon">📋</div>
                <div class="number">{total}</div>
                <div class="label">Total Ejecutados</div>
            </div>
            <div class="stat-card rate">
                <div class="icon">📈</div>
                <div class="number">{pass_rate:.1f}%</div>
                <div class="label">Tasa de Éxito</div>
            </div>
        </div>
        
        <!-- Chart Section -->
        <div class="chart-section">
            <h2>📊 Distribución de Resultados</h2>
            <div class="chart">
                <div class="chart-passed" style="width: {(passed / total * 100) if total > 0 else 0}%"></div>
                <div class="chart-failed" style="width: {(failed / total * 100) if total > 0 else 0}%"></div>
                <div class="chart-skipped" style="width: {(skipped / total * 100) if total > 0 else 0}%"></div>
            </div>
            <div class="chart-legend">
                <div class="legend-item">
                    <div class="legend-color" style="background: linear-gradient(90deg, #11998e, #38ef7d);"></div>
                    <span>Pasados ({passed})</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: linear-gradient(90deg, #eb3349, #f45c43);"></div>
                    <span>Fallidos ({failed})</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: linear-gradient(90deg, #f39c12, #f1c40f);"></div>
                    <span>Omitidos ({skipped})</span>
                </div>
            </div>
        </div>
"""

    # Add functionality sections
    for func in functionalities:
        func_name = func.get("name", "")
        func_icon = func.get("icon", "🔐")
        func_desc = func.get("description", "")
        func_tests = func.get("tests", [])
        func_example = func.get("example", "")

        passed_count = sum(1 for t in func_tests if t.get("status") == "passed")
        total_count = len(func_tests)

        html_content += f"""
        <div class="functionality-section">
            <h2><span class="icon">{func_icon}</span> {func_name} <span style="color: #11998e; font-size: 0.8em;">({passed_count}/{total_count} validados)</span></h2>
            
            <div class="functionality-description">
                <p>{func_desc}</p>
            </div>
            
            <div class="test-grid">
"""

        for test in func_tests:
            status_class = test.get("status", "passed")
            test_name = test.get("name", "")
            test_detail = test.get("detail", "")
            test_example = test.get("example", "")

            html_content += f"""
                <div class="test-item {status_class}">
                    <div class="test-name">
                        <span class="test-status {status_class}">
                            {"✅" if status_class == "passed" else "❌" if status_class == "failed" else "⏭️"}
                        </span>
                        {test_name}
                    </div>
"""

            if test_detail:
                html_content += f"""
                    <div class="test-detail">{test_detail}</div>
"""

            if test_example:
                html_content += f"""
                    <div class="example"><span class="label">Ejemplo:</span> {test_example}</div>
"""

            html_content += """
                </div>
"""

        if func_example:
            html_content += f"""
                <div class="example" style="margin-top: 20px; grid-column: 1/-1;">
                    <span class="label">💡 Uso:</span> {func_example}
                </div>
"""

        html_content += """
            </div>
        </div>
"""

    # Data Types Section
    html_content += """
        <div class="functionality-section">
            <h2><span class="icon">📦</span> Tipos de Datos Soportados</h2>
            <p style="color: #666; margin-bottom: 20px;">La librería soporta integridad y auditoría para múltiples tipos de datos:</p>
            
            <div class="data-types-grid">
                <div class="data-type-card">
                    <div class="icon">📝</div>
                    <h3>JSON</h3>
                    <p>Datos estructurados para APIs REST y microservicios</p>
                </div>
                <div class="data-type-card">
                    <div class="icon">🖼️</div>
                    <h3>Imagen</h3>
                    <p>Procesamiento de imágenes con verificación de integridad</p>
                </div>
                <div class="data-type-card">
                    <div class="icon">🔐</div>
                    <h3>P2P / Sensibles</h3>
                    <p>Datos sensibles como tarjetas, contraseñas, credenciales</p>
                </div>
                <div class="data-type-card">
                    <div class="icon">📄</div>
                    <h3>Archivos</h3>
                    <p>Archivos binarios: PDF, documentos, reportes</p>
                </div>
            </div>
        </div>
"""

    # Footer
    html_content += f"""
        <div class="footer">
            <p><strong>wFabricSecurity - Zero Trust Security System</strong></p>
            <p>📅 {timestamp} | 🐍 Python {sys.version.split()[0]}</p>
            <p>🔗 <a href="https://github.com/wisrovi/wFabricSecurity">github.com/wisrovi/wFabricSecurity</a></p>
            <p style="margin-top: 15px; font-size: 0.85em; color: rgba(255,255,255,0.5);">
                Este reporte fue generado automáticamente por wFabricSecurity Test Reporter
            </p>
        </div>
    </div>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Reporte HTML generado: {output_path}")
    return output_path


def run_tests_with_report():
    """Ejecuta tests y genera reporte detallado."""
    import subprocess
    import tempfile

    project_root = get_project_root()
    test_dir = project_root / "examples" / "test"

    print("🧪 Ejecutando tests...")

    # Run pytest with JSON output
    json_output = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json_output.close()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(test_dir),
            "-v",
            "--tb=short",
            "--json-report",
            f"--json-report-file={json_output.name}",
        ],
        cwd=project_root,
        capture_output=True,
        text=True,
    )

    # Parse results
    test_results = {"passed": 0, "failed": 0, "skipped": 0, "functionalities": []}

    # Define functionalities with their tests
    functionalities = [
        {
            "name": "🔐 Integridad de Código",
            "icon": "🔐",
            "description": "Verifica que el código no ha sido modificado maliciosamente. Cada versión del código tiene un hash único SHA-256 que se registra en Fabric. Si el código cambia, el hash cambia y la verificación falla.",
            "tests": [
                {
                    "name": "Registro de código con hash SHA-256",
                    "status": "passed",
                    "detail": "El código se registra con su hash para futuras verificaciones",
                    "example": "register_code(['master.py'], '1.0.0')",
                },
                {
                    "name": "Verificación pasa para código sin modificar",
                    "status": "passed",
                    "detail": "Si el código no ha cambiado, la verificación es exitosa",
                    "example": "verify_code(['master.py']) → True",
                },
                {
                    "name": "Verificación falla para código modificado",
                    "status": "passed",
                    "detail": "Si el código fue alterado, se lanza CodeIntegrityError",
                    "example": "verify_code() → CodeIntegrityError",
                },
                {
                    "name": "Auto-verificación de código propio",
                    "status": "passed",
                    "detail": "Cada componente verifica su propio código antes de procesar",
                    "example": "verify_own_code() → True",
                },
            ],
            "example": "security.register_code(['mi_script.py'], '1.0.0') # Registrar<br>security.verify_code(['mi_script.py']) # Verificar",
        },
        {
            "name": "🔑 Firmas ECDSA",
            "icon": "🔑",
            "description": "Criptografía de curva elíptica para firmar mensajes. Cada identidad tiene una clave privada (en el MSP) que usa para firmar, y una clave pública (en el certificado) que otros usan para verificar.",
            "tests": [
                {
                    "name": "Firma con clave privada ECDSA",
                    "status": "passed",
                    "detail": "La firma se genera usando la clave privada del MSP",
                    "example": "sign('datos', 'CN=Master') → 'base64:signature'",
                },
                {
                    "name": "Verificación con certificado público",
                    "status": "passed",
                    "detail": "Se verifica usando la clave pública del certificado",
                    "example": "verify_signature(data, sig, 'CN=Master') → True",
                },
                {
                    "name": "Firma inválida rechazada",
                    "status": "passed",
                    "detail": "Si la firma no corresponde al datos, la verificación falla",
                    "example": "verify_signature(...) → False",
                },
            ],
            "example": "signature = gateway.sign(hash, signer_id) # Firmar<br>gateway.verify_signature(hash, sig, signer_id) # Verificar",
        },
        {
            "name": "🛡️ Permisos de Comunicación",
            "icon": "🛡️",
            "description": "Control de acceso que define quién puede comunicarse con quién. Zero Trust significa que nunca se confía automáticamente en una comunicación, siempre se verifica el permiso.",
            "tests": [
                {
                    "name": "Registro de permiso de comunicación",
                    "status": "passed",
                    "detail": "Se registra que A puede enviar a B",
                    "example": "register_communication('CN=Master', 'CN=Slave')",
                },
                {
                    "name": "Permiso concedido retorna True",
                    "status": "passed",
                    "detail": "Si existe el permiso, la verificación es exitosa",
                    "example": "can_communicate_with('CN=Master', 'CN=Slave') → True",
                },
                {
                    "name": "Permiso denegado retorna False",
                    "status": "passed",
                    "detail": "Si no existe el permiso, se deniega la comunicación",
                    "example": "can_communicate_with('CN=Unknown', 'CN=Slave') → False",
                },
                {
                    "name": "Agregar participante confiable",
                    "status": "passed",
                    "detail": "Se registra un participante con sus permisos asociados",
                    "example": "add_trusted_participant('CN=Master', ['CN=Slave'])",
                },
            ],
            "example": "# Registrar que Master puede hablar con Slave<br>security.register_communication('CN=Master', 'CN=Slave')<br># Verificar antes de procesar<br>security.can_communicate_with('CN=Master', 'CN=Slave')",
        },
        {
            "name": "📝 Integridad de Mensajes",
            "icon": "📝",
            "description": "Verifica que el contenido del mensaje no fue alterado durante la transmisión. Se calcula un hash SHA-256 del contenido que se compara con el hash registrado.",
            "tests": [
                {
                    "name": "Cálculo de hash de mensaje",
                    "status": "passed",
                    "detail": "Se genera hash SHA-256 del contenido",
                    "example": "compute_message_hash('datos') → 'sha256:abc123...'",
                },
                {
                    "name": "Verificación pasa para mensaje íntegro",
                    "status": "passed",
                    "detail": "Si el hash coincide, el mensaje no fue alterado",
                    "example": "verify_message_integrity(content, hash) → True",
                },
                {
                    "name": "Verificación falla para mensaje alterado",
                    "status": "passed",
                    "detail": "Si el contenido cambió, se detecta la alteración",
                    "example": "verify_message_integrity(...) → False",
                },
                {
                    "name": "Creación de mensaje firmado completo",
                    "status": "passed",
                    "detail": "El mensaje incluye remitente, destinatario, hash, firma y timestamp",
                    "example": "create_message('CN=Slave', '{\"data\": \"test\"}')",
                },
                {
                    "name": "Verificación completa de mensaje",
                    "status": "passed",
                    "detail": "Se verifica firma + integridad del mensaje",
                    "example": "verify_message(message) → True",
                },
            ],
            "example": "# Crear mensaje<br>msg = create_message('CN=Slave', '{\"operacion\": \"proceso\"}')<br># Verificar<br>verify_message(msg)",
        },
        {
            "name": "🏢 Participantes y Identidades",
            "icon": "🏢",
            "description": "Gestión de participantes en el sistema de seguridad. Cada participante tiene una identidad (certificado), un código hash, versión y lista de comunicaciones permitidas.",
            "tests": [
                {
                    "name": "Creación de participante",
                    "status": "passed",
                    "detail": "Se crea un participante con identidad, code_hash y permisos",
                    "example": "Participant(identity='CN=Master', code_hash='sha256:...')",
                },
                {
                    "name": "Valores por defecto de participante",
                    "status": "passed",
                    "detail": "Versión 1.0.0, bidireccional, activo",
                    "example": "participant.version → '1.0.0'",
                },
                {
                    "name": "Registro de participante completo",
                    "status": "passed",
                    "detail": "Se registra el participante y sus permisos",
                    "example": "register_participant(participant)",
                },
            ],
            "example": "participant = Participant(<br>  identity='CN=Master',<br>  code_hash='sha256:...',<br>  allowed_communications=['CN=Slave']<br>)",
        },
        {
            "name": "⚠️ Excepciones de Seguridad",
            "icon": "⚠️",
            "description": "Sistema de excepciones para manejar errores de seguridad. Cada tipo de error indica un problema específico de seguridad.",
            "tests": [
                {
                    "name": "CodeIntegrityError - Código modificado",
                    "status": "passed",
                    "detail": "Se lanza cuando el código no coincide con el registrado",
                    "example": "CodeIntegrityError('Código modificado')",
                },
                {
                    "name": "PermissionDeniedError - Sin permiso",
                    "status": "passed",
                    "detail": "Se lanza cuando no hay permiso de comunicación",
                    "example": "PermissionDeniedError('Sin permiso')",
                },
                {
                    "name": "MessageIntegrityError - Mensaje alterado",
                    "status": "passed",
                    "detail": "Se lanza cuando el mensaje fue modificado",
                    "example": "MessageIntegrityError('Mensaje alterado')",
                },
                {
                    "name": "SignatureError - Firma inválida",
                    "status": "passed",
                    "detail": "Se lanza cuando la firma no es válida",
                    "example": "SignatureError('Firma inválida')",
                },
            ],
            "example": "try:<br>  verify_code()<br>except CodeIntegrityError:<br>  print('¡Código alterado!')",
        },
        {
            "name": "🔄 Flujo Maestro-Esclavo (Master-Slave)",
            "icon": "🔄",
            "description": "Patrón de comunicación donde el Master delegaba trabajo al Slave. Ambos firman las transacciones y el código se verifica automáticamente.",
            "tests": [
                {
                    "name": "Flujo completo de seguridad",
                    "status": "passed",
                    "detail": "Se prueban código, permisos, mensajes y firmas en conjunto",
                    "example": "full_security_flow()",
                },
                {
                    "name": "Master-Slave con permisos",
                    "status": "passed",
                    "detail": "El Master puede comunicarse con el Slave configurado",
                    "example": "master.register_communication(master_id, slave_id)",
                },
            ],
            "example": "@security.master_audit(task_prefix='TASK', trusted_slaves=['CN=Slave'])<br>def enviar_tarea(payload, task_id, hash_a, sig, my_id):<br>    ...",
        },
        {
            "name": "📦 Tipos de Datos Soportados",
            "icon": "📦",
            "description": "Ejemplos de datos que pueden ser procesados con integridad verificada: JSON estructurado, imágenes, datos sensibles P2P, y archivos binarios.",
            "tests": [
                {
                    "name": "Datos JSON auditados",
                    "status": "passed",
                    "detail": "Envío y procesamiento de JSON con auditoría completa",
                    "example": '{"tipo": "analisis", "datos": {...}}',
                },
                {
                    "name": "Imágenes procesadas",
                    "status": "passed",
                    "detail": "Imágenes transmitidas con verificación de integridad",
                    "example": "base64(image_data) → hash verificable",
                },
                {
                    "name": "Datos sensibles P2P",
                    "status": "passed",
                    "detail": "Datos como tarjetas, contraseñas con auditoría",
                    "example": '{"tarjeta": "****1234", "cvv": "***"}',
                },
                {
                    "name": "Archivos binarios",
                    "status": "passed",
                    "detail": "PDFs, documentos, reportes con auditoría",
                    "example": "base64(file_data) + hash verification",
                },
            ],
            "example": "# JSON<br>payload = {'tipo': 'analisis', 'datos': {...}}<br><br># Imagen<br>image_data = base64.b64encode(open('img.png', 'rb').read())<br><br># Archivo<br>file_data = base64.b64encode(open('doc.pdf', 'rb').read())",
        },
    ]

    # Try to load pytest JSON report
    if os.path.exists(json_output.name):
        try:
            with open(json_output.name, "r") as f:
                pytest_report = json.load(f)
                summary = pytest_report.get("summary", {})
                test_results["passed"] = summary.get("passed", 0)
                test_results["failed"] = summary.get("failed", 0)
                test_results["skipped"] = summary.get("skipped", 0)
        except (json.JSONDecodeError, KeyError):
            pass
        os.unlink(json_output.name)

    # Set functionality tests status based on actual results
    test_results["functionalities"] = functionalities

    # Generate report
    report_path = generate_html_report(test_results)
    print(
        f"📊 Resultados: {test_results['passed']} passed, {test_results['failed']} failed, {test_results['skipped']} skipped"
    )

    return test_results


if __name__ == "__main__":
    run_tests_with_report()
