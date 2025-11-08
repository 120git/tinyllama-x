"""Tests for history module."""
from __future__ import annotations

import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from tinyllamax.core.history import (
    OperationHistory,
    OperationRecord,
    find_similar_failures,
    get_history,
    get_recent_operations,
    log_operation,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test_history.sqlite")
        yield db_path


@pytest.fixture
def history(temp_db):
    """Create a history instance with temporary database."""
    return OperationHistory(db_path=temp_db)


def test_operation_record_creation():
    """Test creating an OperationRecord."""
    record = OperationRecord(
        timestamp=datetime.now(),
        intent_type="InstallPackage",
        command="apt install curl",
        status="success",
        output_summary="Package installed successfully"
    )
    assert record.intent_type == "InstallPackage"
    assert record.command == "apt install curl"
    assert record.status == "success"
    assert record.error_message is None


def test_history_initialization(temp_db):
    """Test history database initialization."""
    _ = OperationHistory(db_path=temp_db)
    assert Path(temp_db).exists()
    
    # Check that tables and indexes were created
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='operations'"
        )
        assert cursor.fetchone() is not None
        
        # Check indexes exist
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
        )
        indexes = [row[0] for row in cursor.fetchall()]
        assert "idx_timestamp" in indexes
        assert "idx_intent" in indexes
        assert "idx_status" in indexes


def test_add_operation(history):
    """Test adding an operation to history."""
    record = OperationRecord(
        timestamp=datetime.now(),
        intent_type="InstallPackage",
        command="apt install curl",
        status="success",
        output_summary="Package installed"
    )
    
    record_id = history.add(record)
    assert record_id > 0


def test_get_recent(history):
    """Test retrieving recent operations."""
    # Add multiple records
    for i in range(5):
        record = OperationRecord(
            timestamp=datetime.now(),
            intent_type=f"Intent{i}",
            command=f"command{i}",
            status="success",
            output_summary=f"output{i}"
        )
        history.add(record)
    
    # Get recent records
    recent = history.get_recent(limit=3)
    assert len(recent) == 3
    # Should be in reverse chronological order
    assert recent[0].intent_type == "Intent4"
    assert recent[2].intent_type == "Intent2"


def test_get_by_intent(history):
    """Test filtering operations by intent type."""
    # Add records with different intents
    for intent in ["InstallPackage", "RemovePackage", "InstallPackage"]:
        record = OperationRecord(
            timestamp=datetime.now(),
            intent_type=intent,
            command=f"cmd for {intent}",
            status="success",
            output_summary="output"
        )
        history.add(record)
    
    # Filter by intent
    install_ops = history.get_by_intent("InstallPackage")
    assert len(install_ops) == 2
    assert all(op.intent_type == "InstallPackage" for op in install_ops)


def test_get_by_status(history):
    """Test filtering operations by status."""
    # Add records with different statuses
    statuses = ["success", "failed", "simulated", "success"]
    for status in statuses:
        record = OperationRecord(
            timestamp=datetime.now(),
            intent_type="TestIntent",
            command="test command",
            status=status,
            output_summary="output"
        )
        history.add(record)
    
    # Filter by status
    failed_ops = history.get_by_status("failed")
    assert len(failed_ops) == 1
    assert failed_ops[0].status == "failed"
    
    success_ops = history.get_by_status("success")
    assert len(success_ops) == 2


def test_get_similar_failures(history):
    """Test finding similar failed operations."""
    # Add some failed operations
    failed_commands = [
        "apt install nonexistent-package",
        "apt install another-bad-pkg",
        "dnf install something",
    ]
    for cmd in failed_commands:
        record = OperationRecord(
            timestamp=datetime.now(),
            intent_type="InstallPackage",
            command=cmd,
            status="failed",
            output_summary="",
            error_message="Package not found"
        )
        history.add(record)
    
    # Add a successful operation
    record = OperationRecord(
        timestamp=datetime.now(),
        intent_type="InstallPackage",
        command="apt install curl",
        status="success",
        output_summary="Installed successfully"
    )
    history.add(record)
    
    # Search for similar failures
    similar = history.get_similar_failures("apt install")
    assert len(similar) == 2
    assert all(op.status == "failed" for op in similar)
    assert all("apt install" in op.command for op in similar)


def test_get_stats(history):
    """Test getting operation statistics."""
    # Add operations with different statuses
    operations = [
        ("InstallPackage", "success"),
        ("InstallPackage", "success"),
        ("InstallPackage", "failed"),
        ("RemovePackage", "success"),
        ("UpdateSystem", "simulated"),
    ]
    
    for intent, status in operations:
        record = OperationRecord(
            timestamp=datetime.now(),
            intent_type=intent,
            command=f"cmd for {intent}",
            status=status,
            output_summary="output"
        )
        history.add(record)
    
    # Get overall stats
    stats = history.get_stats()
    assert stats["total"] == 5
    assert stats["success"] == 3
    assert stats["failed"] == 1
    assert stats["simulated"] == 1
    
    # Get stats filtered by intent
    install_stats = history.get_stats(intent_type="InstallPackage")
    assert install_stats["total"] == 3
    assert install_stats["success"] == 2
    assert install_stats["failed"] == 1


def test_cleanup_old(history):
    """Test cleaning up old history entries."""
    # Add 10 records
    for i in range(10):
        record = OperationRecord(
            timestamp=datetime.now(),
            intent_type=f"Intent{i}",
            command=f"command{i}",
            status="success",
            output_summary="output"
        )
        history.add(record)
    
    # Keep only 5 most recent
    deleted = history.cleanup_old(keep_count=5)
    assert deleted == 5
    
    # Verify only 5 remain
    remaining = history.get_recent(limit=100)
    assert len(remaining) == 5


def test_log_operation_convenience_function(temp_db):
    """Test the convenience log_operation function."""
    # Need to initialize the singleton with our test db
    import tinyllamax.core.history as history_module
    history_module._history_instance = OperationHistory(db_path=temp_db)
    
    record_id = log_operation(
        intent_type="TestIntent",
        command="test command",
        status="success",
        output_summary="Test output"
    )
    
    assert record_id > 0
    
    # Verify it was recorded
    hist = get_history()
    recent = hist.get_recent(limit=1)
    assert len(recent) == 1
    assert recent[0].intent_type == "TestIntent"


def test_get_recent_operations_convenience_function(temp_db):
    """Test the convenience get_recent_operations function."""
    import tinyllamax.core.history as history_module
    history_module._history_instance = OperationHistory(db_path=temp_db)
    
    # Add some operations
    for i in range(3):
        log_operation(
            intent_type=f"Intent{i}",
            command=f"command{i}",
            status="success"
        )
    
    recent = get_recent_operations(limit=2)
    assert len(recent) == 2


def test_find_similar_failures_convenience_function(temp_db):
    """Test the convenience find_similar_failures function."""
    import tinyllamax.core.history as history_module
    history_module._history_instance = OperationHistory(db_path=temp_db)
    
    # Add a failed operation
    log_operation(
        intent_type="InstallPackage",
        command="apt install bad-package",
        status="failed",
        error_message="Package not found"
    )
    
    failures = find_similar_failures("apt install")
    assert len(failures) == 1
    assert failures[0].status == "failed"


def test_operation_record_with_error(history):
    """Test operation record with error message."""
    record = OperationRecord(
        timestamp=datetime.now(),
        intent_type="InstallPackage",
        command="apt install nonexistent",
        status="failed",
        output_summary="Failed to install",
        error_message="E: Unable to locate package nonexistent"
    )
    
    _ = history.add(record)
    retrieved = history.get_recent(limit=1)
    
    assert len(retrieved) == 1
    assert retrieved[0].status == "failed"
    assert retrieved[0].error_message == "E: Unable to locate package nonexistent"
