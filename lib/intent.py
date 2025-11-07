#!/usr/bin/env python3
"""
Intent classification for TinyLlama-X terminal assistant.
Detects user intent from natural language queries.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import re


class IntentType(Enum):
    """Supported user intent types."""
    PACKAGE_INSTALL = "package_install"
    PACKAGE_REMOVE = "package_remove"
    SYSTEM_UPDATE = "system_update"
    FILE_OPERATION = "file_operation"
    COMMAND_EXPLAIN = "command_explain"
    SYSTEM_INFO = "system_info"
    GENERAL_CHAT = "general_chat"


@dataclass
class Intent:
    """Detected intent with extracted parameters."""
    type: IntentType
    confidence: float  # 0.0-1.0
    entities: dict  # Extracted entities (package names, file paths, commands)
    original_query: str


class IntentClassifier:
    """
    Rule-based + pattern-based intent classifier.
    Uses keyword matching for high-confidence cases,
    can optionally fall back to LLM for ambiguous queries.
    """
    
    # Pattern definitions for each intent
    PATTERNS = {
        IntentType.PACKAGE_INSTALL: [
            r'\b(install|add|get|setup)\b.*\b(package|pkg|app|software|program)\b',
            r'\b(apt|dnf|yum|pacman|zypper)\s+install\b',
            r'\binstall\s+(\w+)',
            r'\bhow\s+do\s+i\s+install\b',
            r'\bneed\s+to\s+install\b',
        ],
        IntentType.PACKAGE_REMOVE: [
            r'\b(remove|uninstall|delete|purge)\b.*\b(package|pkg|app|software)\b',
            r'\b(apt|dnf|yum|pacman)\s+(remove|uninstall|purge)\b',
            r'\buninstall\s+(\w+)',
        ],
        IntentType.SYSTEM_UPDATE: [
            r'\b(update|upgrade)\b.*\b(system|packages|everything)\b',
            r'\b(apt|dnf|yum|pacman)\s+(update|upgrade)\b',
            r'\bhow\s+do\s+i\s+update\b',
            r'\bupdate\s+my\s+(system|os|packages)\b',
        ],
        IntentType.FILE_OPERATION: [
            r'\b(copy|move|delete|create|rename|chmod|chown)\b.*\b(file|directory|folder)\b',
            r'\b(cp|mv|rm|mkdir|touch|chmod|chown)\s+',
            r'\bhow\s+to\s+(copy|move|delete|create)\s+',
        ],
        IntentType.COMMAND_EXPLAIN: [
            r'\bwhat\s+(does|is)\s+(\w+)\s+(do|command|mean)\b',
            r'\bexplain\s+(\w+)\s+command\b',
            r'\bhow\s+to\s+use\s+(\w+)\b',
            r'\bhelp\s+with\s+(\w+)\b',
            r'\btell\s+me\s+about\s+(\w+)\s+command\b',
        ],
        IntentType.SYSTEM_INFO: [
            r'\bwhat\s+(is|are)\s+my\s+(os|distro|system|specs)\b',
            r'\bshow\s+me\s+(system|distro|os)\s+info\b',
            r'\b(check|display)\s+system\s+information\b',
            r'\bwhich\s+(distro|distribution|os)\s+am\s+i\s+using\b',
        ],
    }
    
    # Keyword boosters (increase confidence)
    KEYWORDS = {
        IntentType.PACKAGE_INSTALL: ['install', 'add', 'setup', 'apt-get', 'dnf', 'pacman'],
        IntentType.PACKAGE_REMOVE: ['remove', 'uninstall', 'purge', 'delete'],
        IntentType.SYSTEM_UPDATE: ['update', 'upgrade', 'refresh', 'patch'],
        IntentType.FILE_OPERATION: ['copy', 'move', 'delete', 'create', 'chmod', 'chown', 'cp', 'mv', 'rm'],
        IntentType.COMMAND_EXPLAIN: ['explain', 'what', 'how', 'help', 'usage'],
        IntentType.SYSTEM_INFO: ['distro', 'system info', 'os version', 'uname'],
    }
    
    def classify(self, query: str) -> Intent:
        """
        Classify user query into an intent.
        Returns Intent with type, confidence, and extracted entities.
        """
        query_lower = query.lower().strip()
        
        # Try pattern matching first (high confidence)
        for intent_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, query_lower)
                if match:
                    entities = self._extract_entities(query_lower, intent_type, match)
                    confidence = 0.85 + (0.1 if self._has_keywords(query_lower, intent_type) else 0)
                    return Intent(
                        type=intent_type,
                        confidence=min(confidence, 0.95),
                        entities=entities,
                        original_query=query
                    )
        
        # Keyword-based fallback (medium confidence)
        best_intent = None
        best_score = 0
        
        for intent_type, keywords in self.KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > best_score:
                best_score = score
                best_intent = intent_type
        
        if best_intent and best_score > 0:
            return Intent(
                type=best_intent,
                confidence=0.6 + (best_score * 0.05),
                entities=self._extract_entities(query_lower, best_intent),
                original_query=query
            )
        
        # Default to general chat
        return Intent(
            type=IntentType.GENERAL_CHAT,
            confidence=0.5,
            entities={},
            original_query=query
        )
    
    def _has_keywords(self, query: str, intent_type: IntentType) -> bool:
        """Check if query contains keywords for given intent."""
        keywords = self.KEYWORDS.get(intent_type, [])
        return any(kw in query for kw in keywords)
    
    def _extract_entities(self, query: str, intent_type: IntentType, 
                         match: Optional[re.Match] = None) -> dict:
        """Extract relevant entities based on intent type."""
        entities = {}
        
        if intent_type in (IntentType.PACKAGE_INSTALL, IntentType.PACKAGE_REMOVE):
            # Extract package names
            # Look for words after install/remove that aren't common words
            words = query.split()
            stop_words = {'the', 'a', 'an', 'to', 'from', 'in', 'on', 'at', 'how', 'do', 'i', 'my'}
            for i, word in enumerate(words):
                if word in ['install', 'remove', 'uninstall', 'add', 'get']:
                    # Next non-stop-word might be the package
                    for j in range(i+1, len(words)):
                        candidate = words[j].strip('?,.')
                        if candidate not in stop_words and len(candidate) > 2:
                            entities['package'] = candidate
                            break
                    break
        
        elif intent_type == IntentType.COMMAND_EXPLAIN:
            # Extract command name
            if match and match.groups():
                entities['command'] = match.group(1)
            else:
                # Try to find command-like word
                words = query.split()
                for word in words:
                    clean = word.strip('?,.')
                    if len(clean) > 1 and clean not in ['what', 'how', 'the', 'command']:
                        entities['command'] = clean
                        break
        
        elif intent_type == IntentType.FILE_OPERATION:
            # Extract operation and paths if present
            ops = ['copy', 'move', 'delete', 'create', 'rename', 'cp', 'mv', 'rm', 'mkdir']
            for op in ops:
                if op in query:
                    entities['operation'] = op
                    break
            
            # Look for file paths (simple heuristic: contains / or ends with common extensions)
            words = query.split()
            for word in words:
                if '/' in word or any(word.endswith(ext) for ext in ['.txt', '.log', '.conf', '.sh']):
                    if 'source' not in entities:
                        entities['source'] = word
                    else:
                        entities['target'] = word
        
        return entities


# Singleton instance
_classifier = IntentClassifier()


def classify_intent(query: str) -> Intent:
    """Convenience function to classify a query."""
    return _classifier.classify(query)
