import os
import tempfile
import tarfile
import requests
from pathlib import Path


class PyPIClient:
    """Simple PyPI client for metadata + source download."""

    PYPI_URL = "https://pypi.org/pypi/{package}/json"

    # ---------------------------------------------------------
    # Fetch metadata
    # ---------------------------------------------------------
    def fetch_metadata(self, package: str) -> dict:
        url = self.PYPI_URL.format(package=package)
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception:
            return {"info": {}, "releases": {}}

    # ---------------------------------------------------------
    # Download and extract source tarball
    # ---------------------------------------------------------
    def download_source(self, package: str) -> Path:
        """
        Downloads the source distribution (.tar.gz) for a package
        and extracts it into a temporary directory.
        Returns the path to the extracted folder.
        """

        metadata = self.fetch_metadata(package)
        releases = metadata.get("releases", {})

        # Find the latest release with a source tarball
        for version in sorted(releases.keys(), reverse=True):
            for file_info in releases[version]:
                if file_info.get("packagetype") == "sdist":
                    url = file_info.get("url")
                    return self._download_and_extract_tar(url)

        # No source found → return empty temp directory
        return Path(tempfile.mkdtemp())

    # ---------------------------------------------------------
    # Helper: download + extract tar.gz
    # ---------------------------------------------------------
    def _download_and_extract_tar(self, url: str) -> Path:
        temp_dir = Path(tempfile.mkdtemp())

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            tar_path = temp_dir / "package.tar.gz"
            tar_path.write_bytes(response.content)

            with tarfile.open(tar_path, "r:gz") as tar:
                tar.extractall(temp_dir)

        except Exception:
            # Return empty directory if anything fails
            return temp_dir

        return temp_dir
