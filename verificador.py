"""Verificador semántico minimal para Proyecto_Compi.

Detecta: declaración antes de uso, duplicados, suma texto+numero, y mantiene la tabla de símbolos.
Genera impresión ASA decorado en pre-orden y snapshots de la tabla cada vez que cambia.
"""
from typing import Any, Dict, List, Optional
from nodo import asaNode
from symbol_table import SymbolTable
import json
import os
from datetime import datetime


class SemanticError:
    def __init__(self, message: str, line: int = 0, column: int = 0, severity: str = "ERROR"):
        self.message = message
        self.line = line
        self.column = column
        self.severity = severity

    def __str__(self):
        return f"[{self.severity}] {self.line}:{self.column} - {self.message}"


class Verifier:
    def __init__(self, asa_root: asaNode):
        self.root = asa_root
        self.table = SymbolTable()
        self.errors: List[SemanticError] = []
        # map node id to decoration info
        self.decorations: Dict[int, Dict[str, Any]] = {}
        # snapshots log: list of (step, description, snapshot)
        self.snapshots: List[Dict[str, Any]] = []
        # built-in functions/heuristics
        self.builtins = {
            'comparar': {'args': 2, 'arg_types': ['entity', 'entity'], 'ret': 'int'},
            'narrar': {'args': None, 'arg_types': None, 'ret': 'void'},
            'input': {'args': 1, 'arg_types': None, 'ret': 'void'}
        }
        # Pila para marcar contexto de nodos sintácticamente erróneos (ErrorSintactico)
        # Dentro de estos no se reportan errores de "uso antes de declarar" para reducir ruido.
        self.error_context_stack: List[bool] = []

    def run(self) -> List[SemanticError]:
        # start at global scope
        self.table = SymbolTable()
        self._visit(self.root)
        return self.errors

    # Helpers
    def _add_error(self, msg: str, node: Optional[asaNode] = None, column: int = 0):
        line = 0
        if node and isinstance(node.atributos, dict) and 'linea' in node.atributos:
            line = node.atributos.get('linea', 0)
        # Unificar formato de mensajes semánticos
        if not msg.startswith('[SEM]'):
            msg = f"[SEM] {msg}"
        self.errors.append(SemanticError(msg, line, column))

    def _identificador_no_declarado(self, nombre: str, node: Optional[asaNode] = None):
        self._add_error(f"Identificador no declarado '{nombre}' antes de su uso", node)

    def _decorate(self, node: asaNode, info: Dict[str, Any]):
        self.decorations[id(node)] = info
        # record snapshot when decorations are added for some declaration-like nodes
        if node.tipo in ("Deportista", "Lista", "CargaDeportistas"):
            self.snapshots.append({
                'when': datetime.utcnow().isoformat(),
                'node': node.tipo,
                'line': node.atributos.get('linea') if isinstance(node.atributos, dict) else None,
                'table': self.table.snapshot()
            })

    # Traversal
    def _visit(self, node: asaNode, parent: Optional[asaNode] = None, idx: int = 0):
        method = getattr(self, f"_visit_{node.tipo.lower()}", None)
        # before visiting children, call enter scope for compound nodes
        # enter scope for compound nodes (update: RepetirHasta nombre corregido)
        if node.tipo in ("Condicional", "Repetir", "RepetirHasta"):
            lvl = self.table.enter_scope()
            print(f"[TABLA] Enter scope -> nivel {lvl}")
        # Marcar entrada a contexto de error sintáctico
        if node.tipo == "ErrorSintactico":
            self.error_context_stack.append(True)
        if method:
            method(node, parent, idx) if self._accepts_context(method) else method(node)
        else:
            # default: descend
            self._default_visit(node)

        # after children
        if node.tipo in ("Condicional", "Repetir", "RepetirHasta"):
            lvl = self.table.exit_scope()
            print(f"[TABLA] Exit scope -> nivel {lvl}")
        # Salir de contexto de error sintáctico si corresponde
        if node.tipo == "ErrorSintactico" and self.error_context_stack:
            self.error_context_stack.pop()

    def _in_error_context(self) -> bool:
        return any(self.error_context_stack)

    def _default_visit(self, node: asaNode):
        # visit children with context (parent and index)
        for i, c in enumerate(node.hijos):
            self._visit(c, node, i)

    def _accepts_context(self, method) -> bool:
        # helper: detect if the visitor method accepts (node, parent, idx) signature
        try:
            return method.__code__.co_argcount >= 3
        except Exception:
            return False

    # Specific visitors
    def _visit_deportista(self, node: asaNode):
        name = node.atributos.get('nombre', node.contenido)
        line = node.atributos.get('linea', 0)
        err = self.table.declare(name, f"entity:Deportista", node, line)
        if err:
            self._add_error(err, node)
        else:
            print(f"\n[TABLA] [OK] DECLARADO: Deportista '{name}'")
            print(f"        Tipo: entity:Deportista | Línea: {line}")
            print(f"        {self.table}")
        self._decorate(node, {"definicion": name, "tipo": "entity:Deportista"})

    def _visit_cargadeportistas(self, node: asaNode, parent: Optional[asaNode] = None, idx: int = 0):
        # declare a synthetic list variable? We'll register no variable, but mark children
        cantidad = len(node.atributos.get('deportistas', []))
        print(f"\n[TABLA] ✓ CARGA: {cantidad} deportistas cargados")
        self._decorate(node, {"tipo": "list:Deportista", "cantidad": cantidad})
        for i, c in enumerate(node.hijos):
            self._visit(c, node, i)

    def _visit_lista(self, node: asaNode, parent: Optional[asaNode] = None, idx: int = 0):
        # node.atributos may contain 'nombre'
        nombre = node.atributos.get('nombre')
        tipo = node.atributos.get('tipo') or 'unknown'
        if nombre:
            err = self.table.declare(nombre, f"list:{tipo}", node, node.atributos.get('linea', 0))
            if err:
                self._add_error(err, node)
            else:
                print(f"\n[TABLA] [OK] DECLARADO: Lista '{nombre}'")
                print(f"        Tipo: list:{tipo}")
                print(f"        {self.table}")
        self._decorate(node, {"tipo": f"list:{tipo}", "nombre": nombre})
        self._default_visit(node)

    def _visit_narrar(self, node: asaNode, parent: Optional[asaNode] = None, idx: int = 0):
        # narrar accepts anything; however if args contain unknown names we flag
        args = node.atributos.get('args', [])
        local_types = []
        for a in args:
            t = self._resolve_arg_type(a)
            if t == 'unknown' and isinstance(a, str) and ' ' not in a and not a.startswith('"') and not a.isdigit():
                # identificador sin declaración previa
                if not self._in_error_context():
                    self._identificador_no_declarado(a, node)
            local_types.append(t)
        self._decorate(node, {"tipo": "void", "args_types": local_types})
        self._default_visit(node)

    def _visit_dirigir(self, node: asaNode, parent: Optional[asaNode] = None, idx: int = 0):
        # input - may declare domain usage; just decorate args
        args = node.atributos.get('args', [])
        self._decorate(node, {"tipo": "input", "args": args})

    def _visit_identificador(self, node: asaNode, parent: Optional[asaNode] = None, idx: int = 0):
        name = node.contenido
        # if this identifier is a method name (obj . method ), and obj exists as list/entity,
        # treat method as a method reference and don't flag it as undeclared
        if parent and idx > 0:
            prev = parent.hijos[idx - 1]
            if prev.tipo == 'Simbolo' and prev.contenido == '.' and idx > 1:
                obj = parent.hijos[idx - 2]
                if obj.tipo == 'Identificador':
                    entry = self.table.lookup(obj.contenido)
                    if entry and entry.type.startswith('list'):
                        # method call on list; decorate and skip declaration error
                        self._decorate(node, {"method_of": obj.contenido, "is_method": True})
                        return
        # Also check if this is a known built-in method name
        if name.lower() in ('agregar', 'append', 'add'):
            # These are known methods; check if the previous tokens form a valid object.method pattern
            if parent and idx > 0:
                prev = parent.hijos[idx - 1]
                if prev.tipo == 'Simbolo' and prev.contenido == '.' and idx > 1:
                    obj = parent.hijos[idx - 2]
                    if obj.tipo == 'Identificador':
                        entry = self.table.lookup(obj.contenido)
                        if entry:
                            self._decorate(node, {"method_of": obj.contenido, "is_method": True, "method_name": name})
                            return
        
        entry = self.table.lookup(name)
        if not entry:
            if not self._in_error_context():
                self._identificador_no_declarado(name, node)
            self._decorate(node, {"ref": None})
        else:
            self._decorate(node, {"ref": entry.to_dict()})

    def _visit_invocacion(self, node: asaNode, parent: Optional[asaNode] = None, idx: int = 0):
        name = node.contenido
        args = node.atributos.get('args', [])
        # Use builtins if available
        lname = name.lower()
        if lname in self.builtins:
            b = self.builtins[lname]
            # validate arity if fixed
            if b['args'] is not None and len(args) != b['args']:
                self._add_error(f"Llamada a {name} con aridad incorrecta: esperado {b['args']}, encontrado {len(args)}", node)
            # resolve arg types
            arg_types = [self._resolve_arg_type(a) for a in args]
            # specific check for comparar: require entity args
            if lname == 'comparar':
                for i, t in enumerate(arg_types):
                    if not (isinstance(t, str) and t.startswith('entity')):
                        self._add_error(f"Argumento {i+1} de Comparar debe ser una entidad; encontrado '{t}'", node)
            # mark decorations with resolved arg types
            self._decorate(node, {"tipo": b['ret'], "name": name, "args": args, "arg_types": arg_types})
        else:
            # generic invocation
            arg_types = [self._resolve_arg_type(a) for a in args]
            for a, t in zip(args, arg_types):
                if t == 'unknown' and isinstance(a, str) and not a.startswith('"') and not a.isdigit():
                    if not self._in_error_context():
                        self._identificador_no_declarado(a, node)
            self._decorate(node, {"tipo": "unknown_call", "name": name, "args": args, "arg_types": arg_types})
        self._default_visit(node)

    def _resolve_arg_type(self, a: str) -> str:
        """Resolve el tipo de un argumento tokenizado.

        - cadenas entre comillas -> 'string'
        - dígitos -> 'int'
        - identificadores -> lookup en tabla, devolver entry.type o 'unknown'
        """
        if not isinstance(a, str):
            return 'unknown'
        s = a.strip()
        # quoted string
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            return 'string'
        # numeric literal
        if s.isdigit():
            return 'int'
        # lookup
        entry = self.table.lookup(s)
        if entry:
            return entry.type
        return 'unknown'

    def _visit_condicional(self, node: asaNode):
        # condicion stored in atributos['condicion'] or as children
        self._decorate(node, {"tipo": "condicional"})
        # visit children (enter_scope handled by caller)
        for i, c in enumerate(node.hijos):
            self._visit(c, node, i)

    def _visit_repetir(self, node: asaNode):
        self._decorate(node, {"tipo": "repetir", "count": node.contenido})
        for i, c in enumerate(node.hijos):
            self._visit(c, node, i)

    def _visit_repetirhasta(self, node: asaNode):
        self._decorate(node, {"tipo": "repetir_hasta", "condicion": node.contenido})
        for i, c in enumerate(node.hijos):
            self._visit(c, node, i)

    def _visit_binaryop(self, node: asaNode):
        # binary arithmetic or comparison
        if len(node.hijos) >= 2:
            left = node.hijos[0]
            right = node.hijos[1]
            # infer types by visiting operands first
            self._visit(left)
            self._visit(right)
            # determine types from decorations if present
            lt = self._infer_type_from_node(left)
            rt = self._infer_type_from_node(right)
            op = node.contenido
            # check for string + number
            if op == '+' and ((lt == 'string' and rt == 'int') or (lt == 'int' and rt == 'string')):
                self._add_error("No se puede sumar texto con número", node)
            # set result
            if lt == 'int' and rt == 'int' and op in ('+', '-', '*', '/', '%'):
                res = 'int'
            elif lt == 'string' and rt == 'string' and op == '+':
                res = 'string'
            else:
                res = 'unknown'
            self._decorate(node, {"tipo": res, "op": op, "left": lt, "right": rt})
        else:
            self._default_visit(node)

    def _visit_numero(self, node: asaNode):
        self._decorate(node, {"tipo": "int", "valor": node.contenido})

    def _visit_nombre(self, node: asaNode):
        # name in expression
        name = node.contenido
        entry = self.table.lookup(name)
        if entry:
            self._decorate(node, {"tipo": entry.type, "ref": entry.to_dict()})
        else:
            # unknown: mark and error
            self._decorate(node, {"tipo": "unknown", "ref": None})
            if not self._in_error_context():
                self._identificador_no_declarado(name, node)

    def _infer_type_from_node(self, node: asaNode) -> str:
        dec = self.decorations.get(id(node))
        if dec and 'tipo' in dec:
            return dec['tipo']
        # number nodes
        if node.tipo == 'Numero':
            return 'int'
        if node.tipo == 'Nombre':
            # attempt lookup
            entry = self.table.lookup(node.contenido)
            if entry:
                return entry.type
        return 'unknown'

    # Nodos adicionales de la gramática avanzada
    def _visit_resultado(self, node: asaNode, parent: Optional[asaNode] = None, idx: int = 0):
        valores = node.atributos.get('valores', [])
        completo = True
        if len(valores) != 2:
            self._add_error("Resultado requiere dos números", node)
            completo = False
        else:
            # valores[0] y valores[1] pueden ser None si parser falló
            if valores[0] is None:
                self._add_error("Resultado incompleto: falta primer número", node)
                completo = False
            if valores[1] is None:
                self._add_error("Resultado incompleto: falta segundo número", node)
                completo = False
        self._decorate(node, {"tipo": "resultado", "valores": valores, "completo": completo})

    def _visit_resultadoextra(self, node: asaNode, parent: Optional[asaNode] = None, idx: int = 0):
        self._decorate(node, {"tipo": "resultado_extra"})

    def _visit_empate(self, node: asaNode, parent: Optional[asaNode] = None, idx: int = 0):
        self._decorate(node, {"tipo": "empate"})

    def _visit_accionstub(self, node: asaNode, parent: Optional[asaNode] = None, idx: int = 0):
        # Decorar acción genérica (Partido/Carrera/Combate/Rutina stub)
        self._decorate(node, {"tipo": "accion_stub", "nombre": node.contenido})
        for i, c in enumerate(node.hijos):
            self._visit(c, node, i)

    def _visit_partido(self, node: asaNode, parent: Optional[asaNode] = None, idx: int = 0):
        paisA = node.atributos.get('paisA')
        paisB = node.atributos.get('paisB')
        if not paisA or not paisB:
            self._add_error("Partido requiere ambos países", node)
        self._decorate(node, {"tipo": "partido", "paisA": paisA, "paisB": paisB})
        resultado_detectado = None
        for i, c in enumerate(node.hijos):
            self._visit(c, node, i)
            if c.tipo == 'Resultado':
                resultado_detectado = c
        if resultado_detectado and resultado_detectado.atributos.get('valores', [None, None])[1] is None:
            self._add_error("Resultado en Partido antes de cierre está incompleto (segundo número faltante)", resultado_detectado)

    def _visit_carrera(self, node: asaNode, parent: Optional[asaNode] = None, idx: int = 0):
        self._decorate(node, {"tipo": "carrera"})
        resultado_detectado = None
        for i, c in enumerate(node.hijos):
            self._visit(c, node, i)
            if c.tipo == 'Resultado':
                resultado_detectado = c
        if resultado_detectado and resultado_detectado.atributos.get('valores', [None, None])[1] is None:
            self._add_error("Resultado en Carrera antes de cierre está incompleto (segundo número faltante)", resultado_detectado)

    def _visit_rutina(self, node: asaNode, parent: Optional[asaNode] = None, idx: int = 0):
        self._decorate(node, {"tipo": "rutina"})
        resultado_detectado = None
        for i, c in enumerate(node.hijos):
            self._visit(c, node, i)
            if c.tipo == 'Resultado':
                resultado_detectado = c
        if resultado_detectado and resultado_detectado.atributos.get('valores', [None, None])[1] is None:
            self._add_error("Resultado en Rutina antes de cierre está incompleto (segundo número faltante)", resultado_detectado)

    def _visit_combate(self, node: asaNode, parent: Optional[asaNode] = None, idx: int = 0):
        self._decorate(node, {"tipo": "combate"})
        resultado_detectado = None
        for i, c in enumerate(node.hijos):
            self._visit(c, node, i)
            if c.tipo == 'Resultado':
                resultado_detectado = c
        if resultado_detectado and resultado_detectado.atributos.get('valores', [None, None])[1] is None:
            self._add_error("Resultado en Combate antes de cierre está incompleto (segundo número faltante)", resultado_detectado)

    # Public printing utility
    def print_decorated(self):
        def print_node(n: asaNode, level: int = 0):
            indent = '  ' * level
            print(f"{indent}<\"{n.tipo}\", \"{n.contenido}\", {n.atributos}>")
            dec = self.decorations.get(id(n))
            if dec:
                print(f"{indent}  Decorado: {dec}")
            for h in n.hijos:
                print_node(h, level + 1)

        # print to stdout
        print("\n" + "=" * 80)
        print("[VERIFICACION SEMANTICA] RESUMEN DE ANÁLISIS")
        print("=" * 80)
        print(f"\nTabla de Símbolos Final (Scope Global):")
        print(self.table)
        
        print("\n" + "=" * 80)
        print("[RESULTADO] ASA DECORADO:")
        print("=" * 80)
        print_node(self.root)
        
        print("\n" + "=" * 80)
        print("[ERRORES SEMANTICOS]")
        print("=" * 80)
        if self.errors:
            print(f"Total de errores: {len(self.errors)}\n")
            for e in self.errors:
                print(f"  {e}")
        else:
            print("[OK] Sin errores semanticos detectados.")

        # also export decorations + errors + snapshots to JSON in cwd
        out = {
            'decorations': { str(k): v for k, v in self.decorations.items() },
            'errors': [ {'message': e.message, 'line': e.line, 'col': e.column, 'severity': e.severity} for e in self.errors ],
            'snapshots': self.snapshots
        }
        try:
            path = os.path.join(os.getcwd(), 'asa_decorated.json')
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(out, f, ensure_ascii=False, indent=2)
            print(f"\n✓ Decorations exported to: {path}")
        except Exception as ex:
            print(f"Error exporting decorations: {ex}")
