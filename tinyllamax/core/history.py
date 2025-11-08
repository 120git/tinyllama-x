"""Session history tracking with SQLite.

Stores command history for troubleshooting, learning, and audit trails.
Logs intents, commands, results, and execution status.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field


class OperationRecord(BaseModel):
    """Record of a command execution."""
    
    id: int | None = None
    timestamp: datetime
    intent_type: str = Field(description="Type of intent executed")
    command: str = Field(description="Command that was executed")
    status: str = Field(description="Execution status: success, failed, cancelled, simulated")
    output_summary: str = Field(default="", description="Summary of command output")
    error_message: str | None = Field(default=None, description="Error message if failed")


class OperationHistory:
    """Manages operation history in SQLite database."""
    
    def __init__(self, db_path: str | None = None):
        """Initialize history database.
        
        Args:
            db_path: Path to SQLite database. 
                    Default: ~/.local/share/tinyllamax/history.sqlite
        """
        if db_path is None:
            data_dir = Path.home() / '.local' / 'share' / 'tinyllamax'
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(data_dir / 'history.sqlite')
        
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema with proper indexes."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    intent_type TEXT NOT NULL,
                    command TEXT NOT NULL,
                    status TEXT NOT NULL,
                    output_summary TEXT,
                    error_message TEXT
                )
            ''')
            
            # Create index on timestamp for faster queries
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON operations(timestamp DESC)
            ''')
            
            # Create index on intent_type for filtering
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_intent 
                ON operations(intent_type)
            ''')
            
            # Create index on status for filtering
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_status 
                ON operations(status)
            ''')
            
            conn.commit()
    
    def add(self, record: OperationRecord) -> int:
        """Add operation to history.
        
        Args:
            record: Operation record to add
            
        Returns:
            ID of inserted record
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                INSERT INTO operations 
                (timestamp, intent_type, command, status, output_summary, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                record.timestamp.isoformat(),
                record.intent_type,
                record.command,
                record.status,
                record.output_summary,
                record.error_message
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_recent(self, limit: int = 20) -> list[OperationRecord]:
        """Get recent operations.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of recent operation records
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM operations 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            return [self._row_to_record(row) for row in cursor.fetchall()]
    
    def get_by_intent(self, intent_type: str, limit: int = 10) -> list[OperationRecord]:
        """Get operations by intent type.
        
        Args:
            intent_type: Intent type to filter by
            limit: Maximum number of records to return
            
        Returns:
            List of matching operation records
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM operations 
                WHERE intent_type = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (intent_type, limit))
            
            return [self._row_to_record(row) for row in cursor.fetchall()]
    
    def get_by_status(self, status: str, limit: int = 20) -> list[OperationRecord]:
        """Get operations by status.
        
        Args:
            status: Status to filter by (success, failed, cancelled, simulated)
            limit: Maximum number of records to return
            
        Returns:
            List of matching operation records
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM operations 
                WHERE status = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (status, limit))
            
            return [self._row_to_record(row) for row in cursor.fetchall()]
    
    def get_similar_failures(self, command_pattern: str, limit: int = 5) -> list[OperationRecord]:
        """Find similar failed operations for troubleshooting.
        
        Args:
            command_pattern: Pattern to match against commands
            limit: Maximum number of results
        
        Returns:
            List of failed operation records
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM operations 
                WHERE status = 'failed' 
                AND command LIKE ?
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (f'%{command_pattern}%', limit))
            
            return [self._row_to_record(row) for row in cursor.fetchall()]
    
    def get_stats(self, intent_type: str | None = None) -> dict[str, int]:
        """Get operation statistics.
        
        Args:
            intent_type: Optional filter by intent type
        
        Returns:
            Dict with total, success, failed, cancelled, simulated counts
        """
        with sqlite3.connect(self.db_path) as conn:
            if intent_type:
                cursor = conn.execute('''
                    SELECT status, COUNT(*) as count 
                    FROM operations 
                    WHERE intent_type = ?
                    GROUP BY status
                ''', (intent_type,))
            else:
                cursor = conn.execute('''
                    SELECT status, COUNT(*) as count 
                    FROM operations 
                    GROUP BY status
                ''')
            
            stats: dict[str, int] = {
                'total': 0,
                'success': 0,
                'failed': 0,
                'cancelled': 0,
                'simulated': 0
            }
            
            for row in cursor.fetchall():
                status, count = row
                stats['total'] += count
                if status in stats:
                    stats[status] = count
            
            return stats
    
    def cleanup_old(self, keep_count: int = 1000) -> int:
        """Clean up old history entries, keeping only the most recent.
        
        Args:
            keep_count: Number of recent entries to keep
            
        Returns:
            Number of records deleted
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                DELETE FROM operations 
                WHERE id NOT IN (
                    SELECT id FROM operations 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                )
            ''', (keep_count,))
            deleted = cursor.rowcount
            conn.commit()
            return deleted
    
    def _row_to_record(self, row: sqlite3.Row) -> OperationRecord:
        """Convert database row to OperationRecord."""
        return OperationRecord(
            id=row['id'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            intent_type=row['intent_type'],
            command=row['command'],
            status=row['status'],
            output_summary=row['output_summary'] or "",
            error_message=row['error_message']
        )


# Singleton instance for convenient access
_history_instance: OperationHistory | None = None


def get_history(db_path: str | None = None) -> OperationHistory:
    """Get or create the singleton history instance.
    
    Args:
        db_path: Optional custom database path
        
    Returns:
        OperationHistory instance
    """
    global _history_instance
    if _history_instance is None:
        _history_instance = OperationHistory(db_path=db_path)
    return _history_instance


def log_operation(
    intent_type: str, 
    command: str, 
    status: str,
    output_summary: str = "", 
    error_message: str | None = None
) -> int:
    """Convenience function to log an operation.
    
    Args:
        intent_type: Type of intent executed
        command: Command that was executed
        status: Execution status (success, failed, cancelled, simulated)
        output_summary: Summary of command output
        error_message: Error message if failed
        
    Returns:
        ID of inserted record
    """
    record = OperationRecord(
        timestamp=datetime.now(),
        intent_type=intent_type,
        command=command,
        status=status,
        output_summary=output_summary,
        error_message=error_message
    )
    return get_history().add(record)


def get_recent_operations(limit: int = 20) -> list[OperationRecord]:
    """Convenience function to get recent operations.
    
    Args:
        limit: Maximum number of records to return
        
    Returns:
        List of recent operation records
    """
    return get_history().get_recent(limit)


def find_similar_failures(command_pattern: str, limit: int = 5) -> list[OperationRecord]:
    """Convenience function to find similar failures.
    
    Args:
        command_pattern: Pattern to match against commands
        limit: Maximum number of results
        
    Returns:
        List of failed operation records
    """
    return get_history().get_similar_failures(command_pattern, limit)


__all__ = [
    "OperationRecord",
    "OperationHistory",
    "get_history",
    "log_operation",
    "get_recent_operations",
    "find_similar_failures",
]
