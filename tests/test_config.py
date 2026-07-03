"""
Tests for Config and DolarVzlaLogger.

We use monkeypatch to set environment variables before re-creating Config.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

# Force minimal env before importing Config
os.environ.setdefault("NTFY_TOPIC", "test-topic")
os.environ.setdefault("NTFY_URL", "https://ntfy.example.com")
os.environ.setdefault("BINANCE_EXTRA_FIATS", "")
os.environ.setdefault("BINANCE_EXTRA_CRON", "0 */3 * * *")
os.environ.setdefault("BINANCE_VES_CRON", "*/30 * * * *")
os.environ.setdefault("BCV_CRON", "0 0 * * *")

from app.config import Config, DolarVzlaLogger


class TestConfig:
    def test_default_values(self):
        """Config reads env vars and provides sensible defaults."""
        c = Config(
            NTFY_TOPIC="t",
            NTFY_URL="https://n.example.com",
            BINANCE_EXTRA_FIATS="",
            BINANCE_EXTRA_CRON="0 */3 * * *",
            BINANCE_VES_CRON="*/30 * * * *",
            BCV_CRON="0 0 * * *",
            DATABASE_URL="sqlite+aiosqlite:///custom/test.db",
            _env_file=None,
        )
        assert c.APP_NAME == "P2P Exchange Tracker"
        assert c.APP_VERSION is not None
        assert c.API_HOST == "127.0.0.1"
        assert c.API_PORT == 8000
        assert "sqlite+aiosqlite:///" in c.DATABASE_URL
        assert "test.db" in c.DATABASE_URL

    def test_dirs_created(self, tmp_path):
        """ensure_dirs creates instance and logs directories."""
        c = Config(
            NTFY_TOPIC="t",
            NTFY_URL="https://n.example.com",
            BINANCE_EXTRA_FIATS="",
            BINANCE_EXTRA_CRON="0 */3 * * *",
            BINANCE_VES_CRON="*/30 * * * *",
            BCV_CRON="0 0 * * *",
            INSTANCE_DIR=tmp_path / "instance",
            LOGS_DIR=tmp_path / "logs",
            _env_file=None,
        )
        assert (tmp_path / "instance").exists()
        assert (tmp_path / "logs").exists()

    def test_env_override(self, monkeypatch):
        """Environment variables override defaults."""
        monkeypatch.setenv("API_PORT", "9000")
        monkeypatch.setenv("NTFY_TOPIC", "topic-x")
        monkeypatch.setenv("NTFY_URL", "https://n.example.com")
        monkeypatch.setenv("BINANCE_EXTRA_FIATS", "PEN")
        monkeypatch.setenv("BINANCE_EXTRA_CRON", "0 */3 * * *")
        monkeypatch.setenv("BINANCE_VES_CRON", "*/30 * * * *")
        monkeypatch.setenv("BCV_CRON", "0 0 * * *")

        c = Config(_env_file=None)
        assert c.API_PORT == 9000


class TestDolarVzlaLogger:
    def test_setup_logging_creates_log_file(self, tmp_path):
        """Calling setup_logging creates the log directory and file."""
        logs_dir = tmp_path / "test_logs"

        DolarVzlaLogger.setup_logging(logs_dir=logs_dir, level="DEBUG")

        assert logs_dir.exists()
        log_file = logs_dir / "dolar_vzla.log"
        assert log_file.exists()

    def test_level_map_contains_expected_keys(self):
        assert "DEBUG" in DolarVzlaLogger.LEVEL_MAP
        assert "INFO" in DolarVzlaLogger.LEVEL_MAP
        assert "ERROR" in DolarVzlaLogger.LEVEL_MAP