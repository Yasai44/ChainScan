from indicators.metadata import MetadataIndicator

def test_low_downloads_indicator():
    indicator = MetadataIndicator()

    fake_metadata = {
        "downloads_last_month": 0
    }

    findings = indicator.check(fake_metadata)

    assert len(findings) > 0
    assert findings[0]["type"] == "metadata"
    assert findings[0]["indicator"] == "low_downloads"
