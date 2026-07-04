import re

class MetadataIndicator:
    """Scan PyPI metadata for suspicious characteristics."""

    def check(self, metadata: dict) -> list[dict]:
        findings = []
        info = metadata.get("info", {})

        # Very low downloads
        downloads = info.get("downloads", {}).get("last_month", 0)
        if downloads < 50:
            findings.append({
                "type": "metadata",
                "indicator": "low_downloads",
                "score": 1,
                "details": f"Downloads last month: {downloads}"
            })

        # No homepage or project URL
        if not info.get("home_page") and not info.get("project_url"):
            findings.append({
                "type": "metadata",
                "indicator": "no_homepage",
                "score": 2,
                "details": "No homepage or project URL"
            })

        # Simple typo-squatting detection
        name = info.get("name", "")
        if re.search(r"(reqeusts|numpyy|pandasx)", name):
            findings.append({
                "type": "metadata",
                "indicator": "typo_squatting_suspected",
                "score": 4,
                "details": f"Package name looks like typo-squatting: {name}"
            })

        return findings
