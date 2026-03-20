"""
Genera reportes profesionales de tests en HTML y PDF.
"""

import os
import sys
import json
import datetime
from pathlib import Path
from typing import List, Dict, Any


def get_project_root():
    return Path(__file__).parent.parent.parent


def generate_html_report(results: Dict[str, Any], output_path: str = None):
    """Genera reporte HTML profesional con los resultados de tests."""

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

    passed = results.get("passed", 0)
    failed = results.get("failed", 0)
    skipped = results.get("skipped", 0)
    total = passed + failed + skipped

    pass_rate = (passed / total * 100) if total > 0 else 0
    status_color = "#28a745" if failed == 0 else "#dc3545"
    status_text = "EXITOSO" if failed == 0 else "CON FALLOS"

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Tests - wFabricSecurity</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .header .meta {{
            margin-top: 20px;
            display: flex;
            gap: 30px;
            font-size: 0.9em;
        }}
        
        .header .meta span {{
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 20px;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-card .number {{
            font-size: 3em;
            font-weight: bold;
        }}
        
        .stat-card .label {{
            color: #666;
            margin-top: 10px;
        }}
        
        .stat-card.passed .number {{ color: #28a745; }}
        .stat-card.failed .number {{ color: #dc3545; }}
        .stat-card.skipped .number {{ color: #ffc107; }}
        .stat-card.total .number {{ color: #667eea; }}
        .stat-card.rate .number {{ color: {status_color}; }}
        
        .status-badge {{
            display: inline-block;
            padding: 15px 40px;
            border-radius: 30px;
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 30px;
        }}
        
        .status-badge.success {{
            background: #d4edda;
            color: #155724;
            border: 2px solid #28a745;
        }}
        
        .status-badge.failure {{
            background: #f8d7da;
            color: #721c24;
            border: 2px solid #dc3545;
        }}
        
        .tests-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        
        .tests-section h2 {{
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }}
        
        .test-item {{
            padding: 15px 20px;
            border-left: 4px solid #28a745;
            margin-bottom: 15px;
            background: #f8f9fa;
            border-radius: 0 10px 10px 0;
        }}
        
        .test-item.failed {{
            border-left-color: #dc3545;
            background: #fff5f5;
        }}
        
        .test-item.skipped {{
            border-left-color: #ffc107;
            background: #fffbf0;
        }}
        
        .test-item .name {{
            font-weight: bold;
            color: #333;
            font-size: 1.1em;
        }}
        
        .test-item .class {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        .test-item .error {{
            color: #dc3545;
            font-family: monospace;
            font-size: 0.85em;
            margin-top: 10px;
            padding: 10px;
            background: #fff;
            border-radius: 5px;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        
        .footer {{
            text-align: center;
            color: rgba(255,255,255,0.7);
            padding: 20px;
            font-size: 0.9em;
        }}
        
        .footer a {{
            color: #667eea;
            text-decoration: none;
        }}
        
        .chart-container {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        
        .chart {{
            display: flex;
            height: 40px;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 20px;
        }}
        
        .chart-passed {{ background: #28a745; }}
        .chart-failed {{ background: #dc3545; }}
        .chart-skipped {{ background: #ffc107; }}
        
        .chart-legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 15px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
        
        .legend-color.passed {{ background: #28a745; }}
        .legend-color.failed {{ background: #dc3545; }}
        .legend-color.skipped {{ background: #ffc107; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Reporte de Tests</h1>
            <div class="subtitle">wFabricSecurity - Librería de Seguridad Distribuida</div>
            <div class="meta">
                <span>📅 {timestamp}</span>
                <span>🐍 Python pytest</span>
                <span>📊 {total} tests ejecutados</span>
            </div>
        </div>
        
        <div style="text-align: center;">
            <div class="status-badge {"success" if failed == 0 else "failure"}">
                {"✓ EJECUCIÓN EXITOSA" if failed == 0 else "✗ EJECUCIÓN CON FALLOS"}
            </div>
        </div>
        
        <div class="summary">
            <div class="stat-card passed">
                <div class="number">{passed}</div>
                <div class="label">✓ Pasados</div>
            </div>
            <div class="stat-card failed">
                <div class="number">{failed}</div>
                <div class="label">✗ Fallidos</div>
            </div>
            <div class="stat-card skipped">
                <div class="number">{skipped}</div>
                <div class="label">⊘ Omitidos</div>
            </div>
            <div class="stat-card total">
                <div class="number">{total}</div>
                <div class="label">📋 Total</div>
            </div>
            <div class="stat-card rate">
                <div class="number">{pass_rate:.1f}%</div>
                <div class="label">📈 Tasa de Éxito</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h2>📊 Distribución de Resultados</h2>
            <div class="chart">
                <div class="chart-passed" style="width: {(passed / total * 100) if total > 0 else 0}%"></div>
                <div class="chart-failed" style="width: {(failed / total * 100) if total > 0 else 0}%"></div>
                <div class="chart-skipped" style="width: {(skipped / total * 100) if total > 0 else 0}%"></div>
            </div>
            <div class="chart-legend">
                <div class="legend-item">
                    <div class="legend-color passed"></div>
                    <span>Pasados ({passed})</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color failed"></div>
                    <span>Fallidos ({failed})</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color skipped"></div>
                    <span>Omitidos ({skipped})</span>
                </div>
            </div>
        </div>
        
        <div class="tests-section">
            <h2>📋 Detalle de Tests</h2>
"""

    test_results = results.get("tests", [])
    for test in test_results:
        status_class = (
            "passed"
            if test.get("outcome") == "passed"
            else "failed"
            if test.get("outcome") == "failed"
            else "skipped"
        )
        error_html = (
            f'<div class="error">{test.get("longrepr", "")}</div>'
            if status_class == "failed"
            else ""
        )

        html_content += f"""
            <div class="test-item {status_class}">
                <div class="name">{"✓" if status_class == "passed" else "✗" if status_class == "failed" else "⊘"} {test.get("nodeid", "Unknown")}</div>
                {error_html}
            </div>
"""

    html_content += f"""
        </div>
        
        <div class="footer">
            <p>Generado automáticamente por wFabricSecurity Test Reporter</p>
            <p>📅 {timestamp} | 🐍 Python {sys.version.split()[0]}</p>
            <p><a href="https://github.com/wisrovi/wFabricSecurity">github.com/wisrovi/wFabricSecurity</a></p>
        </div>
    </div>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✓ Reporte HTML generado: {output_path}")
    return output_path


def run_tests_with_report(output_format: str = "html"):
    """Ejecuta los tests y genera un reporte profesional."""
    import subprocess
    import tempfile
    import json

    project_root = get_project_root()
    test_dir = project_root / "examples" / "test"

    print("🧪 Ejecutando tests...")

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
            f"--json-report",
            f"--json-report-file={json_output.name}",
        ],
        cwd=project_root,
        capture_output=True,
        text=True,
    )

    results = {"passed": 0, "failed": 0, "skipped": 0, "tests": []}

    if os.path.exists(json_output.name):
        with open(json_output.name, "r") as f:
            try:
                report = json.load(f)
                results["passed"] = report.get("summary", {}).get("passed", 0)
                results["failed"] = report.get("summary", {}).get("failed", 0)
                results["skipped"] = report.get("summary", {}).get("skipped", 0)

                for test in report.get("tests", []):
                    results["tests"].append(
                        {
                            "nodeid": test.get("nodeid", ""),
                            "outcome": test.get("outcome", ""),
                            "longrepr": str(test.get("longrepr", ""))[:500]
                            if test.get("longrepr")
                            else "",
                        }
                    )
            except json.JSONDecodeError:
                pass
        os.unlink(json_output.name)

    print(
        f"📊 Resultados: {results['passed']} passed, {results['failed']} failed, {results['skipped']} skipped"
    )

    if output_format == "html":
        return generate_html_report(results)

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Genera reportes de tests")
    parser.add_argument(
        "--format", choices=["html", "json"], default="html", help="Formato del reporte"
    )
    args = parser.parse_args()

    run_tests_with_report(args.format)
