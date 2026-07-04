from reporter import Reporter

def fake_result():
    return {
        "package": "example",
        "risk_score": 3,
        "risk_level": "medium",
        "findings": [
            {
                "type": "metadata",
                "indicator": "low_downloads",
                "details": "Downloads last month: 0",
                "score": 2
            }
        ]
    }

def test_cli_output():
    reporter = Reporter()
    output = reporter.to_cli(fake_result())

    assert "Target:" in output
    assert "Risk score:" in output
    assert "Risk level:" in output

def test_html_output():
    reporter = Reporter()
    html = reporter.to_html(fake_result())

    assert "<html" in html
    assert "example" in html
    assert "low_downloads" in html
