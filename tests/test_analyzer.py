from analyzer import Analyzer

def test_analyze_pypi_package_basic():
    analyzer = Analyzer()
    result = analyzer.analyze_pypi_package("requests")

    assert "risk_score" in result
    assert "risk_level" in result
    assert "findings" in result
    assert isinstance(result["findings"], list)
