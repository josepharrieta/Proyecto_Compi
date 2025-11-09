"""Symbol table with nested scopes for the Proyecto_Compi verifier.

Provides a simple API: enter_scope, exit_scope, declare, lookup and snapshot.
"""
from typing import Dict, Any, Optional, List


class SymbolEntry:
    def __init__(self, name: str, typ: str, defined_node: Any = None, defined_line: int = 0, scope_level: int = 0):
        self.name = name
        self.type = typ
        self.defined_node = defined_node
        self.defined_line = defined_line
        self.scope_level = scope_level

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "defined_line": self.defined_line,
            "scope_level": self.scope_level,
        }


class SymbolTable:
    def __init__(self):
        # scopes: list of dicts; index 0 = global
        self.scopes: List[Dict[str, SymbolEntry]] = [{}]

    def current_level(self) -> int:
        return len(self.scopes) - 1

    def enter_scope(self) -> int:
        self.scopes.append({})
        return self.current_level()

    def exit_scope(self) -> int:
        if len(self.scopes) > 1:
            self.scopes.pop()
        return self.current_level()

    def declare(self, name: str, typ: str, node: Any = None, line: int = 0) -> Optional[str]:
        """Declare a symbol in the current scope.

        Returns an error message if duplicate in same scope, otherwise None.
        """
        scope = self.scopes[-1]
        if name in scope:
            return f"Declaración duplicada: '{name}' ya existe en el scope actual (nivel {self.current_level()})"
        entry = SymbolEntry(name, typ, node, line, self.current_level())
        scope[name] = entry
        return None

    def lookup(self, name: str) -> Optional[SymbolEntry]:
        # search from inner to outer
        for s in reversed(self.scopes):
            if name in s:
                return s[name]
        return None

    def snapshot(self) -> Dict[str, Any]:
        """Return a compact snapshot of the whole table for printing."""
        out = {}
        for lvl, s in enumerate(self.scopes):
            out[f"scope_{lvl}"] = {k: v.to_dict() for k, v in s.items()}
        return out

    def __str__(self) -> str:
        parts = []
        for lvl, s in enumerate(self.scopes):
            parts.append(f"[scope {lvl}]:")
            for name, entry in s.items():
                parts.append(f"  - {name}: {entry.type} (line {entry.defined_line})")
        return "\n".join(parts)
