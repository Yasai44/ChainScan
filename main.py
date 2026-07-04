import argparse
import json
import os

from analyzer import Analyzer
from reporter import Reporter


def main():
    parser = argparse.ArgumentParser(description="Supply Chain Risk Analyzer")

    parser.add_argument(
        "--package",
        type=str,
        help="Analyze a PyPI package"
    )

    parser.add_argument(
        "--path",
        type=str,
        help="Analyze a local Python file"
    )

    args = parser.parse_args()

    analyzer = Analyzer()
    reporter = Reporter()

    # Decide what to analyze
    if args.package:
        result = analyzer.analyze_pypi_package(args.package)
        target_name = args.package

    elif args.path:
        result = analyzer.analyze_file(args.path)
        target_name = args.path.replace("\\", "/").split("/")[-1]

    else:
        print("You must specify either --package or --path")
        return

    # Print CLI output (color + Rich table)
    print(reporter.to_cli(result))

    # Ensure reports directory exists
    os.makedirs("reports", exist_ok=True)

    # Export JSON report
    json_filename = os.path.join("reports", f"{target_name}.json")
    with open(json_filename, "w", encoding="utf-8") as jf:
        json.dump(result, jf, indent=2)

    # Export HTML dashboard for this target
    html = reporter.to_html(result)
    html_filename = os.path.join("reports", f"{target_name}.html")
    with open(html_filename, "w", encoding="utf-8") as hf:
        hf.write(html)

    print(f"\nJSON report saved as: {json_filename}")
    print(f"HTML report saved as: {html_filename}")


if __name__ == "__main__":
    main()
