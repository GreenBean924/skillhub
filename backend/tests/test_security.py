import pytest

from app.services.security.llm_reviewer import (
    _fallback_report,
    _parse_llm_response,
    _validate_report,
)


class TestFallbackReport:
    def test_empty_capabilities(self):
        report = _fallback_report([])
        assert report["risk_level"] == "low"
        assert report["score"] == 80
        assert report["findings"] == []
        assert "Static analysis only" in report["summary"]

    def test_safe_capabilities(self):
        report = _fallback_report(["file_read", "search"])
        assert report["risk_level"] == "low"
        assert report["score"] == 80
        assert len(report["findings"]) == 0

    def test_risky_capabilities(self):
        report = _fallback_report(["file_write", "network_access"])
        assert report["risk_level"] == "medium"
        assert report["score"] < 80
        assert len(report["findings"]) == 2

    def test_high_risk_capabilities(self):
        report = _fallback_report(["code_exec", "sudo"])
        assert report["risk_level"] == "medium"
        assert len(report["findings"]) == 2
        assert all(f["severity"] == "medium" for f in report["findings"])


class TestValidateReport:
    def test_valid_report(self):
        report = {
            "risk_level": "safe",
            "score": 95,
            "findings": [
                {
                    "id": "F001",
                    "severity": "info",
                    "title": "Test",
                    "description": "Test finding",
                    "evidence": "test.py",
                    "recommendation": "No action needed",
                }
            ],
        }
        validated = _validate_report(report)
        assert validated["risk_level"] == "safe"
        assert validated["score"] == 95
        assert len(validated["findings"]) == 1
        assert "scannedAt" in validated
        assert validated["review_version"] == "llm-v1"

    def test_invalid_risk_level(self):
        report = {"risk_level": "invalid", "score": 50, "findings": []}
        validated = _validate_report(report)
        assert validated["risk_level"] == "medium"

    def test_invalid_score(self):
        report = {"risk_level": "safe", "score": 200, "findings": []}
        validated = _validate_report(report)
        assert validated["score"] == 50

    def test_missing_fields(self):
        report = {"risk_level": "safe"}
        validated = _validate_report(report)
        assert validated["score"] == 50
        assert validated["findings"] == []

    def test_invalid_severity(self):
        report = {
            "risk_level": "safe",
            "score": 90,
            "findings": [{"id": "F001", "severity": "invalid", "title": "Test"}],
        }
        validated = _validate_report(report)
        assert validated["findings"][0]["severity"] == "info"


class TestParseLLMResponse:
    def test_valid_json(self):
        text = '{"risk_level": "safe", "score": 95, "findings": []}'
        result = _parse_llm_response(text)
        assert result["risk_level"] == "safe"

    def test_json_with_markdown(self):
        text = '```json\n{"risk_level": "safe", "score": 95, "findings": []}\n```'
        result = _parse_llm_response(text)
        assert result["risk_level"] == "safe"

    def test_invalid_json(self):
        with pytest.raises(Exception):
            _parse_llm_response("not json")
