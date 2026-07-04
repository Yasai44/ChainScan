from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory, jsonify
from pathlib import Path
import os
import json

from analyzer import Analyzer

app = Flask(__name__)
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

# -------------------------------------------------------------------
# HTML template (inline, uses your Chain Scan branding)
# -------------------------------------------------------------------
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Chain Scan Dashboard</title>
    <link rel="icon" type="image/svg+xml" href="/static/favicon.svg">

    <style>
        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #0b1020;
            color: #f0f0f0;
            margin: 0;
            padding: 2rem;
        }

        .header {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .logo {
            height: 48px;
        }

        .tagline {
            color: #8aa0c8;
            font-size: 0.9rem;
            margin-top: -0.5rem;
        }

        .card {
            background: #141a33;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        }

        h1, h2 {
            margin: 0;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }

        th, td {
            padding: 0.75rem;
            border-bottom: 1px solid #262b45;
            text-align: left;
            font-size: 0.9rem;
        }

        th {
            background: #1c2340;
        }

        a {
            color: #40a9ff;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        .footer {
            margin-top: 2rem;
            text-align: center;
            color: #8aa0c8;
            font-size: 0.8rem;
        }

        .forms {
            display: flex;
            gap: 1.5rem;
            flex-wrap: wrap;
        }

        .forms form {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        input[type="text"], input[type="file"] {
            padding: 0.5rem;
            border-radius: 4px;
            border: 1px solid #262b45;
            background: #0b1020;
            color: #f0f0f0;
        }

        button {
            padding: 0.5rem 1rem;
            border-radius: 4px;
            border: none;
            background: #40a9ff;
            color: #0b1020;
            font-weight: 600;
            cursor: pointer;
        }

        button:hover {
            background: #1890ff;
        }
    </style>
</head>

<body>

    <!-- Branding Header -->
    <div class="header">
        <img src="/static/chain-scan-logo.svg" class="logo">
        <div>
            <h1>Chain Scan Dashboard</h1>
            <p class="tagline">Supply Chain Risk Intelligence</p>
        </div>
    </div>

    <!-- Forms -->
    <div class="card">
        <h2>Run a Scan</h2>
        <div class="forms">
            <form method="post" action="{{ url_for('scan_package') }}">
                <label>Scan PyPI package</label>
                <input type="text" name="package_name" placeholder="e.g. requests" required>
                <button type="submit">Scan package</button>
            </form>

            <form method="post" action="{{ url_for('scan_file') }}" enctype="multipart/form-data">
                <label>Scan local Python file</label>
                <input type="file" name="file" accept=".py" required>
                <button type="submit">Scan file</button>
            </form>
        </div>
    </div>

    <!-- Summary Card -->
    <div class="card">
        <h2>Scanned Targets</h2>
        <p>Overview of all analyzed Python packages and files.</p>
    </div>

    <!-- Table of Reports -->
    <div class="card">
        <table>
            <thead>
                <tr>
                    <th>Target</th>
                    <th>Risk Score</th>
                    <th>Risk Level</th>
                    <th>Report</th>
                    <th>JSON</th>
                </tr>
            </thead>
            <tbody>
                {% for r in reports %}
                <tr>
                    <td>{{ r.target }}</td>
                    <td>{{ r.score }}</td>
                    <td style="color:{{ r.level_color }}; font-weight:bold;">{{ r.level }}</td>
                    <td><a href="{{ url_for('view_report_html', filename=r.html_file) }}">View HTML</a></td>
                    <td><a href="{{ url_for('view_report_json', filename=r.json_file) }}">View JSON</a></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <!-- Footer -->
    <div class="footer">
        Chain Scan v1.0.0 — Built for secure software supply chains
    </div>

</body>
</html>
"""


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def load_reports():
    reports = []

    if not REPORT_DIR.exists():
        return reports

    for filename in os.listdir(REPORT_DIR):
        if not filename.endswith(".json"):
            continue

        path = REPORT_DIR / filename
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        target = data.get("package") or data.get("path") or filename.replace(".json", "")
        score = data.get("risk_score", 0)
        level = data.get("risk_level", "unknown")

        if level == "high":
            level_color = "#ff4d4f"
        elif level == "medium":
            level_color = "#faad14"
        elif level == "low":
            level_color = "#52c41a"
        else:
            level_color = "#d9d9d9"

        reports.append(type("R", (), {
            "target": target,
            "score": score,
            "level": level,
            "level_color": level_color,
            "json_file": filename,
            "html_file": filename.replace(".json", ".html"),
        }))

    return reports


def save_report(result: dict):
    target = result.get("package") or result.get("path") or "unknown"
    base = target.replace(os.sep, "_").replace(":", "_")
    json_path = REPORT_DIR / f"{base}.json"
    html_path = REPORT_DIR / f"{base}.html"

    # Save JSON
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    # Simple HTML report
    findings_rows = ""
    for f in result.get("findings", []):
        findings_rows += f"""
        <tr>
            <td>{f.get('type')}</td>
            <td>{f.get('indicator')}</td>
            <td>{f.get('score')}</td>
            <td>{f.get('details')}</td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>Chain Scan Report - {target}</title>
        <style>
            body {{
                font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                background: #0b1020;
                color: #f0f0f0;
                margin: 0;
                padding: 2rem;
            }}
            .card {{
                background: #141a33;
                border-radius: 8px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 1rem;
            }}
            th, td {{
                padding: 0.75rem;
                border-bottom: 1px solid #262b45;
                text-align: left;
                font-size: 0.9rem;
            }}
            th {{
                background: #1c2340;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Chain Scan Report</h1>
            <p><strong>Target:</strong> {target}</p>
            <p><strong>Risk score:</strong> {result.get('risk_score')}</p>
            <p><strong>Risk level:</strong> {result.get('risk_level')}</p>
        </div>

        <div class="card">
            <h2>Findings</h2>
            <table>
                <thead>
                    <tr>
                        <th>Type</th>
                        <th>Indicator</th>
                        <th>Severity</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
                    {findings_rows}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    html_path.write_text(html_content, encoding="utf-8")


# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------
@app.route("/")
def index():
    reports = load_reports()
    return render_template_string(DASHBOARD_TEMPLATE, reports=reports)


@app.route("/scan/package", methods=["POST"])
def scan_package():
    package_name = request.form.get("package_name", "").strip()
    if not package_name:
        return redirect(url_for("index"))

    analyzer = Analyzer()
    result = analyzer.analyze_pypi_package(package_name)
    save_report(result)

    return redirect(url_for("index"))


@app.route("/scan/file", methods=["POST"])
def scan_file():
    file = request.files.get("file")
    if not file:
        return redirect(url_for("index"))

    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / file.filename
    file.save(file_path)

    analyzer = Analyzer()
    result = analyzer.analyze_file(str(file_path))
    save_report(result)

    return redirect(url_for("index"))


@app.route("/reports/<path:filename>")
def view_report_html(filename):
    return send_from_directory(REPORT_DIR, filename)


@app.route("/api/reports/<path:filename>")
def view_report_json(filename):
    path = REPORT_DIR / filename
    if not path.exists():
        return jsonify({"error": "not found"}), 404
    data = json.loads(path.read_text(encoding="utf-8"))
    return jsonify(data)


# Static for logo + favicon (put files in ./static/)
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)


if __name__ == "__main__":
    app.run(debug=True)
