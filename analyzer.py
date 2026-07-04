import os
from pathlib import Path
from indicators import MetadataIndicator, CodeIndicators
from pypi_client import PyPIClient


class Analyzer:
    """Main analysis engine for packages and local files."""

    def __init__(self):
        self.metadata_indicator = MetadataIndicator()
        self.code_indicator = CodeIndicators()
        self.pypi = PyPIClient()

    # ---------------------------------------------------------
    # Analyze a PyPI package
    # ---------------------------------------------------------
    def analyze_pypi_package(self, package_name: str) -> dict:
        metadata = self.pypi.fetch_metadata(package_name)

        findings = []

        # Metadata indicators
        findings.extend(self.metadata_indicator.check(metadata))

        # If package has source files, scan them
        source_files = self._download_and_extract(package_name)
        for file_path in source_files:
            findings.extend(self.code_indicator.scan_file(file_path))

        # Compute risk score
        risk_score = sum(f["score"] for f in findings)
        risk_level = self._risk_level(risk_score)

        return {
            "package": package_name,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "findings": findings
        }

    # ---------------------------------------------------------
    # Analyze a local Python file
    # ---------------------------------------------------------
    def analyze_file(self, file_path: str) -> dict:
        path = Path(file_path)

        findings = self.code_indicator.scan_file(path)

        risk_score = sum(f["score"] for f in findings)
        risk_level = self._risk_level(risk_score)

        return {
            "path": file_path,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "findings": findings
        }

    # ---------------------------------------------------------
    # Helper: download and extract package source
    # ---------------------------------------------------------
    def _download_and_extract(self, package_name: str) -> list[Path]:
        """
        Downloads the package source using PyPIClient and returns a list of .py files.
        """
        temp_dir = self.pypi.download_source(package_name)
        py_files = []

        for root, _, files in os.walk(temp_dir):
            for f in files:
                if f.endswith(".py"):
                    py_files.append(Path(root) / f)

        return py_files

    # ---------------------------------------------------------
    # Helper: risk level mapping
    # ---------------------------------------------------------
    def _risk_level(self, score: int) -> str:
        if score >= 10:
            return "high"
        elif score >= 5:
            return "medium"
        else:
            return "low"
