from pypi_client import PyPIClient

def test_fetch_metadata():
    client = PyPIClient()
    metadata = client.fetch_metadata("requests")

    assert "info" in metadata
    assert "releases" in metadata
