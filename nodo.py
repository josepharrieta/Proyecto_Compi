"""
Nodo AST y utilidades para impresión en preorden.
Formato de salida por línea:
<"Tipo", "Contenido", "Atributos">
"""
from typing import List, Dict, Any, Iterator


class ASTNode:
    def __init__(self, tipo: str, contenido: str = "", atributos: Dict[str, Any] = None, hijos: List['ASTNode'] = None):
        self.tipo = tipo
        self.contenido = contenido or ""
        self.atributos = atributos or {}
        self.hijos = hijos or []

    def agregar_hijo(self, nodo: 'ASTNode'):
        self.hijos.append(nodo)

    def preorder_lines(self, nivel: int = 0) -> Iterator[str]:
        indent = "  " * nivel
        # Atributos se presentan como diccionario legible
        yield f'{indent}<"{self.tipo}", "{self.contenido}", {self.atributos}>'
        for h in self.hijos:
            yield from h.preorder_lines(nivel + 1)

    def __str__(self) -> str:
        return "\n".join(self.preorder_lines())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tipo": self.tipo,
            "contenido": self.contenido,
            "atributos": self.atributos,
            "hijos": [h.to_dict() for h in self.hijos]
        }