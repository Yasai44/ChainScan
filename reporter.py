import json
from colorama import Fore, Style, init
from rich.table import Table
from rich.console import Console

# Initialize colorama for Windows terminals
init(autoreset=True)

console = Console()


class Reporter:
    """Format analysis results for CLI, JSON, and HTML dashboard output."""

    def _risk_bar(self, score: int, max_score: int = 10) -> str:
        """Return a horizontal risk bar like [■■■■■□□□□□] 5/10."""
        filled = min(score, max_score)
        empty = max_score - filled
        return f"[{'■' * filled}{'□' * empty}] {score}/{max_score}"

    def to_cli(self, result: dict) -> str:
        lines = []

        # Target
        target = result.get("package") or result.get("path")
        lines.append(f"{Fore.CYAN}Target:{Style.RESET_ALL} {target}")

        # Risk score
        score = result.get("risk_score")
        lines.append(f"{Fore.MAGENTA}Risk score:{Style.RESET_ALL} {score}")

        # Horizontal risk bar
        bar = self._risk_bar(score)
        lines.append(f"{Fore.BLUE}{bar}{Style.RESET_ALL}")

        # Risk level with color
        level = result.get("risk_level")
        if level == "high":
            level_color = Fore.RED
        elif level == "medium":
            level_color = Fore.YELLOW
        elif level == "low":
            level_color = Fore.GREEN
        else:
            level_color = Fore.WHITE

        lines.append(f"{Fore.CYAN}Risk level:{Style.RESET_ALL} {level_color}{level}{Style.RESET_ALL}")

        # Build Rich table for findings
        table = Table(title="Findings", show_lines=True)

        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Indicator", style="magenta")
        table.add_column("Severity", style="yellow")
        table.add_column("Details", style="white")

        for f in result.get("findings", []):
            ftype = f.get("type", "general")
            indicator = f.get("indicator", "unknown")
            details = f.get("details", "")
            severity = f.get("score", 0)

            # Severity label + color
            if severity >= 3:
                sev_label = f"[bold red]{severity}[/bold red]"
            elif severity == 2:
                sev_label = f"[bold yellow]{severity}[/bold yellow]"
            else:
                sev_label = f"[bold green]{severity}[/bold green]"

            table.add_row(ftype, indicator, sev_label, details)

        # Print the table directly using Rich
        console.print(table)

        return "\n".join(lines)

    def to_json(self, result: dict) -> str:
        return json.dumps(result, indent=2)

    def to_html(self, result: dict) -> str:
        """Return an HTML dashboard string for the analysis result."""
        target = result.get("package") or result.get("path")
        score = result.get("risk_score")
        level = result.get("risk_level")
        findings = result.get("findings", [])

        # Simple severity color
        if level == "high":
            level_color = "#ff4d4f"
        elif level == "medium":
            level_color = "#faad14"
        elif level == "low":
            level_color = "#52c41a"
        else:
            level_color = "#d9d9d9"

        rows = ""
        for f in findings:
            ftype = f.get("type", "general")
            indicator = f.get("indicator", "unknown")
            details = f.get("details", "")
            severity = f.get("score", 0)

            if severity >= 3:
                sev_color = "#ff4d4f"
            elif severity == 2:
                sev_color = "#faad14"
            else:
                sev_color = "#52c41a"

            rows += f"""
            <tr>
                <td>{ftype}</td>
                <td>{indicator}</td>
                <td style="color:{sev_color}; font-weight:bold;">{severity}</td>
                <td>{details}</td>
            </tr>
            """

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <title>Supply Chain Risk Report - {target}</title>
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
                h1, h2 {{
                    margin: 0 0 0.75rem 0;
                }}
                .risk-level {{
                    color: {level_color};
                    font-weight: bold;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 1rem;
                }}
                th, td {{
                    padding: 0.5rem 0.75rem;
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
                <h1>Supply Chain Risk Report</h1>
                <p><strong>Target:</strong> {target}</p>
                <p><strong>Risk score:</strong> {score}</p>
                <p><strong>Risk level:</strong> <span class="risk-level">{level}</span></p>
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
                        {rows}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        return html
