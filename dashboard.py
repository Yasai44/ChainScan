import os
import json
from pathlib import Path


def load_reports(report_dir: str = "reports"):
    reports = []

    if not os.path.isdir(report_dir):
        return reports

    for filename in os.listdir(report_dir):
        if not filename.endswith(".json"):
            continue

        path = os.path.join(report_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        target = (
            data.get("package")
            or data.get("path")
            or filename.replace(".json", "")
        )

        score = data.get("risk_score", 0)
        level = data.get("risk_level", "unknown")

        reports.append({
            "target": target,
            "score": score,
            "level": level,
            "json_file": filename,
            "html_file": filename.replace(".json", ".html"),
        })

    return reports


def generate_rows(reports):
    rows = ""

    for r in reports:
        target = r["target"]
        score = r["score"]
        level = r["level"]
        html_file = r["html_file"]

        # Color coding
        if level == "high":
            level_color = "#ff4d4f"
        elif level == "medium":
            level_color = "#faad14"
        elif level == "low":
            level_color = "#52c41a"
        else:
            level_color = "#d9d9d9"

        rows += f"""
        <tr>
            <td>{target}</td>
            <td>{score}</td>
            <td style="color:{level_color}; font-weight:bold;">{level}</td>
            <td><a href="reports/{html_file}">View report</a></td>
        </tr>
        """

    return rows


def generate_dashboard(output_file: str = "dashboard.html"):
    reports = load_reports("reports")

    if not reports:
        print("No reports found in 'reports' directory. Run some scans first.")
        return

    rows_html = generate_rows(reports)

    # Load template
    template_path = Path("dashboard.html")
    if not template_path.exists():
        print("dashboard.html template not found.")
        return

    template = template_path.read_text(encoding="utf-8")

    # Insert rows
    final_html = template.replace("{{rows}}", rows_html)

    # Write final dashboard
    output_path = Path("dashboard_rendered.html")
    output_path.write_text(final_html, encoding="utf-8")

    print(f"Dashboard generated: {output_path}")


if __name__ == "__main__":
    generate_dashboard()
