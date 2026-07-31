"""
tests_logger.py — logger/

Covers: logger.py — Logger.log_event and Logger.run_preflight_checks.
Uses pytest's caplog fixture (correct tool for output going through
Python's logging module) plus tmp_path/monkeypatch for filesystem and
env checks. No real Groq key or network needed.

Run with:
    cd backend/srs/logger
    python -m pytest tests_logger.py -v
"""

import logging
import pytest
from logger.logger import Logger


@pytest.fixture(autouse=True)
def _capture_jinie_logger(caplog):
    caplog.set_level(logging.DEBUG, logger="jinie.srs")


# =====================================================================
# log_event
# =====================================================================

def test_log_event_runs_without_error(caplog):
    logger = Logger(trace_id="trc-test-001")
    logger.log_event("test_module.py", "This is a test message", level="INFO")
    assert "trc-test-001" in caplog.text
    assert "test_module.py" in caplog.text
    assert "This is a test message" in caplog.text


def test_log_event_includes_level(caplog):
    logger = Logger(trace_id="trc-test-002")
    logger.log_event("test_module.py", "Warning message", level="WARNING")
    assert "level=WARNING" in caplog.text


def test_log_event_invalid_level_defaults_to_info(caplog):
    logger = Logger(trace_id="trc-test-003")
    logger.log_event("test_module.py", "message", level="NOT_A_REAL_LEVEL")
    assert "level=INFO" in caplog.text


def test_log_event_uses_instance_trace_id_by_default(caplog):
    logger = Logger(trace_id="trc-instance-id")
    logger.log_event("test_module.py", "message")
    assert "trace_id=trc-instance-id" in caplog.text


def test_log_event_call_level_trace_id_overrides_instance(caplog):
    logger = Logger(trace_id="trc-instance-id")
    logger.log_event("test_module.py", "message", trace_id="trc-override-id")
    assert "trace_id=trc-override-id" in caplog.text
    assert "trc-instance-id" not in caplog.text


def test_log_event_no_trace_id_anywhere_uses_placeholder(caplog):
    logger = Logger()
    logger.log_event("test_module.py", "message")
    assert "trace_id=no-trace-id" in caplog.text


def test_log_event_includes_iso_timestamp(caplog):
    logger = Logger(trace_id="trc-test-004")
    logger.log_event("test_module.py", "message")
    assert "T" in caplog.text
    assert "Z" in caplog.text


def test_log_event_default_level_is_info(caplog):
    logger = Logger(trace_id="trc-test-005")
    logger.log_event("test_module.py", "no level passed")
    assert "level=INFO" in caplog.text


def test_log_event_debug_level_reaches_output(caplog):
    logger = Logger(trace_id="trc-test-006")
    logger.log_event("test_module.py", "debug detail", level="DEBUG")
    assert "level=DEBUG" in caplog.text


def test_log_event_critical_level_reaches_output(caplog):
    logger = Logger(trace_id="trc-test-007")
    logger.log_event("test_module.py", "critical failure", level="CRITICAL")
    assert "level=CRITICAL" in caplog.text


# =====================================================================
# run_preflight_checks
# =====================================================================

def test_preflight_fails_on_nonexistent_path(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_valid_looking_key")
    logger = Logger(trace_id="trc-pf-001")
    result = logger.run_preflight_checks("/this/path/does/not/exist/at/all")
    assert result is False


def test_preflight_fails_on_file_instead_of_directory(tmp_path, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_valid_looking_key")
    fake_file = tmp_path / "not_a_directory.txt"
    fake_file.write_text("hello")
    logger = Logger(trace_id="trc-pf-002")
    result = logger.run_preflight_checks(str(fake_file))
    assert result is False


def test_preflight_fails_when_api_key_missing(tmp_path, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    logger = Logger(trace_id="trc-pf-003")
    result = logger.run_preflight_checks(str(tmp_path))
    assert result is False


def test_preflight_passes_with_valid_directory_and_key(tmp_path, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_valid_looking_key_1234567890")
    logger = Logger(trace_id="trc-pf-004")
    result = logger.run_preflight_checks(str(tmp_path))
    assert result is True


def test_preflight_warns_but_does_not_fail_on_unusual_key_format(tmp_path, monkeypatch, caplog):
    monkeypatch.setenv("GROQ_API_KEY", "not_the_expected_prefix_12345")
    logger = Logger(trace_id="trc-pf-005")
    result = logger.run_preflight_checks(str(tmp_path))
    assert result is True
    assert "WARNING" in caplog.text


def test_preflight_logs_each_check(tmp_path, monkeypatch, caplog):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_valid_looking_key")
    logger = Logger(trace_id="trc-pf-006")
    logger.run_preflight_checks(str(tmp_path))
    assert "Starting preflight checks" in caplog.text
    assert "All preflight checks PASSED" in caplog.text


def test_preflight_logs_failure_summary_when_checks_fail(monkeypatch, caplog):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    logger = Logger(trace_id="trc-pf-007")
    logger.run_preflight_checks("/nonexistent/path/xyz")
    assert "FAILED" in caplog.text