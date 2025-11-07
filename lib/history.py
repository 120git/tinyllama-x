#!/usr/bin/env python3
"""
Operation history tracking with SQLite.
Stores command history for troubleshooting and learning.
"""

import sqlite3
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from pathlib import Path


@dataclass
class OperationRecord:
    """Record of a command execution."""
    id: Optional[int]
    timestamp: datetime
    intent_type: str
    command: str
    status: str  # 'success', 'failed', 'cancelled'
    output_summary: str
    error_message: Optional[str] = None


class OperationHistory:
    """Manages operation history in SQLite."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize history database.
        
        Args:
            db_path: Path to SQLite database (default: ~/.cache/tinyllama-x/history.db)
        """
        if db_path is None:
            cache_dir = Path.home() / '.cache' / 'tinyllama-x'
            cache_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(cache_dir / 'history.db')
        
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
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
            
            conn.commit()
    
    def add(self, record: OperationRecord) -> int:
        """
        Add operation to history.
        
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
    
    def get_recent(self, limit: int = 20) -> List[OperationRecord]:
        """Get recent operations."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM operations 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            return [self._row_to_record(row) for row in cursor.fetchall()]
    
    def get_by_intent(self, intent_type: str, limit: int = 10) -> List[OperationRecord]:
        """Get operations by intent type."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM operations 
                WHERE intent_type = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (intent_type, limit))
            
            return [self._row_to_record(row) for row in cursor.fetchall()]
    
    def get_similar_failures(self, command_pattern: str, limit: int = 5) -> List[OperationRecord]:
        """
        Find similar failed operations for troubleshooting.
        
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
    
    def get_success_rate(self, intent_type: Optional[str] = None) -> dict:
        """
        Get success rate statistics.
        
        Args:
            intent_type: Optional filter by intent type
        
        Returns:
            Dict with total, successful, failed, cancelled counts
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
            
            stats = {
                'total': 0,
                'success': 0,
                'failed': 0,
                'cancelled': 0
            }
            
            for row in cursor.fetchall():
                status, count = row
                stats['total'] += count
                stats[status] = count
            
            return stats
    
    def cleanup_old(self, keep_count: int = 100):
        """
        Clean up old history entries, keeping only the most recent.
        
        Args:
            keep_count: Number of recent entries to keep
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                DELETE FROM operations 
                WHERE id NOT IN (
                    SELECT id FROM operations 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                )
            ''', (keep_count,))
            conn.commit()
    
    def _row_to_record(self, row: sqlite3.Row) -> OperationRecord:
        """Convert database row to OperationRecord."""
        return OperationRecord(
            id=row['id'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            intent_type=row['intent_type'],
            command=row['command'],
            status=row['status'],
            output_summary=row['output_summary'],
            error_message=row['error_message']
        )


# Singleton instance
_history = OperationHistory()


def log_operation(intent_type: str, command: str, status: str, 
                 output_summary: str = "", error_message: Optional[str] = None) -> int:
    """Convenience function to log an operation."""
    record = OperationRecord(
        id=None,
        timestamp=datetime.now(),
        intent_type=intent_type,
        command=command,
        status=status,
        output_summary=output_summary,
        error_message=error_message
    )
    return _history.add(record)


def get_recent_operations(limit: int = 20) -> List[OperationRecord]:
    """Convenience function to get recent operations."""
    return _history.get_recent(limit)


def find_similar_failures(command_pattern: str) -> List[OperationRecord]:
    """Convenience function to find similar failures."""
    return _history.get_similar_failures(command_pattern)
