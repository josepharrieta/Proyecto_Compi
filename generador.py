"""Generador de código Python desde ASA de Olympiac

Uso rápido (PowerShell):
    python .\generador.py .\ejemplo_asa.oly -o programa_generado.py
    python .\programa_generado.py

Qué hace ahora:
 1. Parsea el archivo .oly usando el parser existente.
 2. Recorre el ASA y traduce nodos a código Python sencillo.
 3. Emite un "ambiente estándar" con helpers (registrar_deportista, comparar, narrar).
 4. Genera instrucciones para: Deportista, Lista, invocaciones (Comparar, narrar), Repetir, Condicional (placeholder), método agregar en listas.

Limitaciones actuales / TODO:
 - Condiciones de 'si' se traducen a 'if True:' (no se reconstruye expresión real).
 - No se infiere semántica de comparaciones; se puede extender usando decoraciones del verificador.
 - Invocaciones genéricas distintas de Comparar/narrar/input quedan como comentario.
 - No se diferencian bloques else (tu AST no muestra explícito 'Sino' como rama separada con los nodos; adaptar si aparece).

Extender fácilmente:
 - Implementar _emit_condicion(cond_str, node) para reconstruir expresiones.
 - Usar asa_decorated.json para tipos más precisos.
 - Agregar generación de funciones para secuencias (partidos/torneos) según comentarios.
"""
from __future__ import annotations
import sys
import argparse
from typing import List
from analizador_sintactico import parse_from_file
from nodo import asaNode

AMBIENTE = """# === Ambiente estándar Olympiac → Python ===\n""" + r"""
deportistas = {}

def registrar_deportista(nombre, stats, deporte, pais):
    deportistas[nombre] = {"stats": [int(x) for x in stats], "deporte": deporte, "pais": pais}

def comparar(a, b):
    if a not in deportistas or b not in deportistas:
        return 0
    sa = deportistas[a]["stats"]
    sb = deportistas[b]["stats"]
    pa = sum(sa) / len(sa)
    pb = sum(sb) / len(sb)
    # Diferencia simple (puede ajustarse)
    return pa - pb

def narrar(*msgs):
    if len(msgs) == 1:
        m = msgs[0]
        if isinstance(m, str) and m in deportistas:
            d = deportistas[m]
            print(f"{m} ({d['deporte']}, {d['pais']}) -> {d['stats']}")
        else:
            print(m)
    else:
        print(" ".join(str(x) for x in msgs))

def agregar(lista, valor):
    lista.append(valor)
"""


class VisitorOlympiac:
    def __init__(self):
        self.lines: List[str] = []
        self.indent_level = 0

    def indent(self) -> str:
        return " " * (self.indent_level * 4)

    def emit(self, line: str):
        self.lines.append(self.indent() + line)

    def visit(self, node: asaNode):
        metodo = getattr(self, f"visit_{node.tipo}", None)
        if metodo:
            metodo(node)
        else:
            # fallback: visitar hijos
            for h in node.hijos:
                self.visit(h)

    # ---------------- Nodos -----------------
    def visit_Programa(self, node: asaNode):
        i = 0
        hijos = node.hijos
        while i < len(hijos):
            # Patrón lista.agregar(arg) - estructura: Identificador . Identificador ( Identificador )
            if (i + 5 < len(hijos) and 
                hijos[i].tipo == 'Identificador' and 
                hijos[i+1].tipo == 'Simbolo' and hijos[i+1].contenido == '.' and 
                hijos[i+2].tipo == 'Identificador' and hijos[i+2].contenido.lower() == 'agregar' and 
                hijos[i+3].tipo == 'Simbolo' and hijos[i+3].contenido == '(' and
                hijos[i+4].tipo == 'Identificador' and
                hijos[i+5].tipo == 'Simbolo' and hijos[i+5].contenido == ')'):
                lista_nombre = hijos[i].contenido
                arg = hijos[i+4].contenido
                self.emit(f"{lista_nombre}.append('{arg}')")
                i += 6
                continue
            # Legacy: Patrón lista.agregar(...) con Invocacion
            if i + 2 < len(hijos) and hijos[i].tipo == 'Identificador' and hijos[i+1].tipo == 'Simbolo' and hijos[i+1].contenido == '.' and hijos[i+2].tipo == 'Invocacion' and hijos[i+2].contenido.lower().startswith('agregar('):
                lista_nombre = hijos[i].contenido
                inv = hijos[i+2]
                py_line = self._transform_agregar(lista_nombre, inv)
                self.emit(py_line)
                i += 3
                continue
            self.visit(hijos[i])
            i += 1

    def visit_Comentario(self, node: asaNode):
        txt = node.contenido.replace('\n', ' ').strip()
        self.emit(f"# {txt}")

    def visit_Deportista(self, node: asaNode):
        nombre = node.atributos.get('nombre', node.contenido)
        stats = node.atributos.get('estadisticas', [])
        deporte = node.atributos.get('deporte', '')
        pais = node.atributos.get('pais', '')
        self.emit(f"registrar_deportista('{nombre}', {stats}, '{deporte}', '{pais}')")

    def visit_Lista(self, node: asaNode):
        nombre = node.atributos.get('nombre') or node.contenido or 'lista_dep'
        self.emit(f"{nombre} = []  # lista declarada")

    def visit_CargaDeportistas(self, node: asaNode):
        # CargaDeportistas: solo comentamos los datos; podrían declararse automáticamente.
        self.emit("# Carga masiva de deportistas (no implementado en generador)")
        for d in node.atributos.get('deportistas', []):
            self.emit(f"# deportista {d['nombre']} {d['estadisticas']} {d['deporte']} {d['pais']}")

    def visit_Narrar(self, node: asaNode):
        args = node.atributos.get('args', [])
        if not args:
            self.emit("narrar('')")
        else:
            parts = ", ".join(self._format_arg(a) for a in args)
            self.emit(f"narrar({parts})")

    def visit_Invocacion(self, node: asaNode):
        raw = node.contenido  # ej: "Comparar(" o "narrar(" etc.
        nombre = raw.rstrip('(')
        args = node.atributos.get('args', [])
        lname = nombre.lower()
        if lname.startswith('comparar'):
            if len(args) == 2:
                self.emit(f"comparar('{args[0]}', '{args[1]}')  # resultado descartado")
            else:
                self.emit(f"# ERROR aridad comparar: {args}")
        elif lname.startswith('narrar'):
            parts = ", ".join(self._format_arg(a) for a in args)
            self.emit(f"narrar({parts})")
        elif lname.startswith('input'):
            self.emit("_entrada = input()  # input capturado")
        elif lname.startswith('agregar'):
            # Si llega aquí sin acceso por patrón con lista. Se deja comentario.
            parts = ", ".join(self._format_arg(a) for a in args)
            self.emit(f"# llamada agregar fuera de contexto: agregar({parts})")
        else:
            self.emit(f"# Invocacion no soportada: {nombre} {args}")

    def visit_Condicional(self, node: asaNode):
        cond_raw = node.atributos.get('condicion', 'True')
        cond_py = self._translate_condition(cond_raw)
        self.emit(f"if {cond_py}:")
        self.indent_level += 1
        
        # Procesar hijos detectando patrones lista.agregar()
        i = 0
        hijos = node.hijos
        while i < len(hijos):
            # Patrón lista.agregar(arg)
            if (i + 5 < len(hijos) and 
                hijos[i].tipo == 'Identificador' and 
                hijos[i+1].tipo == 'Simbolo' and hijos[i+1].contenido == '.' and 
                hijos[i+2].tipo == 'Identificador' and hijos[i+2].contenido.lower() == 'agregar' and 
                hijos[i+3].tipo == 'Simbolo' and hijos[i+3].contenido == '(' and
                hijos[i+4].tipo == 'Identificador' and
                hijos[i+5].tipo == 'Simbolo' and hijos[i+5].contenido == ')'):
                lista_nombre = hijos[i].contenido
                arg = hijos[i+4].contenido
                self.emit(f"{lista_nombre}.append('{arg}')")
                i += 6
            elif hijos[i].tipo == 'Sino':
                self.indent_level -= 1
                self.emit("else:")
                self.indent_level += 1
                for sn in hijos[i].hijos:
                    self.visit(sn)
                i += 1
            else:
                self.visit(hijos[i])
                i += 1
        
        self.indent_level -= 1

    def visit_Repetir(self, node: asaNode):
        count = node.contenido
        self.emit(f"for _i in range({count}):")
        self.indent_level += 1
        for h in node.hijos:
            self.visit(h)
        self.indent_level -= 1

    def visit_RepetirHasta(self, node: asaNode):
        # RepetirHasta(n) se traduce como: for i in range(n):
        # (aunque el nombre sugiera "hasta", en el ASA recibimos solo el número)
        count = node.contenido
        self.emit(f"for _j in range({count}):")
        self.indent_level += 1
        for h in node.hijos:
            self.visit(h)
        self.indent_level -= 1

    def visit_AccionStub(self, node: asaNode):
        # Emite comentario de bloque de acción de competencia
        self.emit(f"# Acción competencia: {node.contenido}")
        self.indent_level += 1
        for h in node.hijos:
            self.visit(h)
        self.indent_level -= 1

    def visit_Resultado(self, node: asaNode):
        valores = node.atributos.get('valores', [])
        if len(valores) == 2 and all(v is not None for v in valores):
            self.emit(f"# Resultado registrado: {valores[0]} - {valores[1]}")
        else:
            self.emit("# ERROR Resultado incompleto")

    def visit_ResultadoExtra(self, node: asaNode):
        self.emit("# ResultadoExtra (listaRes) marcador adicional")

    def visit_Empate(self, node: asaNode):
        self.emit("# Empate detectado")

    def visit_Partido(self, node: asaNode):
        paisA = node.atributos.get('paisA','')
        paisB = node.atributos.get('paisB','')
        self.emit(f"# Partido: {paisA} vs {paisB}")
        self.indent_level += 1
        for h in node.hijos:
            self.visit(h)
        self.indent_level -= 1

    def visit_Carrera(self, node: asaNode):
        self.emit("# Carrera iniciada")
        self.indent_level += 1
        for h in node.hijos:
            self.visit(h)
        self.indent_level -= 1

    def visit_Rutina(self, node: asaNode):
        self.emit("# Rutina iniciada")
        self.indent_level += 1
        for h in node.hijos:
            self.visit(h)
        self.indent_level -= 1

    def visit_Combate(self, node: asaNode):
        self.emit("# Combate iniciado")
        self.indent_level += 1
        for h in node.hijos:
            self.visit(h)
        self.indent_level -= 1

    def visit_Identificador(self, node: asaNode):
        # Se maneja en patrones (lista.agregar)
        pass

    def visit_Simbolo(self, node: asaNode):
        # Usado para detectar patrones (.) en secuencias de hijos por el generador externo si se ampliara.
        pass

    # ---------------- Utilidades -----------------
    def _format_arg(self, a: str) -> str:
        if a.isdigit():
            return a
        a_strip = a.strip()
        if (a_strip.startswith('"') and a_strip.endswith('"')) or (a_strip.startswith("'") and a_strip.endswith("'")):
            return a_strip
        return f"'{a_strip}'"

    def _translate_condition(self, c: str) -> str:
        c = c.strip()
        # Intento detectar estructura "X op Y".
        partes = c.split()
        if len(partes) == 3:
            left, op, right = partes
            # Si ambos son números, se devuelve la comparación directa.
            if left.isdigit() and right.isdigit() and op in ('>', '<', '==', '!=', '>=', '<='):
                return f"{left} {op} {right}"
            # Si son identificadores de Deportista, sugerimos comparación por promedio usando helper comparar.
            if left.isalpha() and right.isalpha() and op in ('>', '<'):
                comp_expr = f"comparar('{left}', '{right}') {op} 0"
                return comp_expr
        # Fallback: verdadera para no bloquear flujo.
        return 'True'

    # ---------------- API pública -----------------
    def generate(self, root: asaNode) -> str:
        self.visit(root)
        return "\n".join(self.lines)

    # ---------------- Transformaciones específicas -----------------
    def _transform_agregar(self, lista_nombre: str, inv_agregar: asaNode) -> str:
        args = inv_agregar.atributos.get('args', [])
        if not args:
            return f"# agregar sin argumentos sobre {lista_nombre}"
        # Caso especial: primer arg es 'Comparar(' seguido de dos nombres.
        if len(args) >= 3 and args[0].lower().startswith('comparar('):
            a = args[1]
            b = args[2]
            return f"{lista_nombre}.append(comparar('{a}', '{b}'))  # agregar resultado comparacion"
        # Genérico: agregar cada argumento individual.
        formateados = [self._format_arg(a) for a in args]
        if len(formateados) == 1:
            return f"{lista_nombre}.append({formateados[0]})"
        return f"{lista_nombre}.extend([{', '.join(formateados)}])"


def detectar_patron_agregar(asa: asaNode, visitor: VisitorOlympiac):
    """Recorrido adicional para transformar secuencias tipo:
       Identificador (lista) . Identificador (agregar) ( Invocacion Comparar(... ) )
       en una sola línea lista.append(comparar(a,b)).
       Este ajuste post-procesa lines: simplifica comentarios de invocación comparar descartada.
    """
    nuevas = []
    i = 0
    lines = visitor.lines
    while i < len(lines):
        linea = lines[i]
        if line_starts_agregar(linea):
            # Ya manejado manualmente? Mantener.
            nuevas.append(linea)
        else:
            nuevas.append(linea)
        i += 1
    visitor.lines = nuevas

def line_starts_agregar(linea: str) -> bool:
    return False  # placeholder; si se implementa patrón específico


def construir_codigo(asa: asaNode) -> str:
    visitor = VisitorOlympiac()
    cuerpo = visitor.generate(asa)
    detectar_patron_agregar(asa, visitor)
    return AMBIENTE + "\n# === Código generado ===\n\n" + cuerpo + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generador de código Python desde archivo Olympiac (.oly)")
    parser.add_argument('archivo', help='Archivo .oly de entrada')
    parser.add_argument('-o', '--output', help='Archivo de salida .py (si se omite imprime a stdout)')
    args = parser.parse_args(argv)

    asa = parse_from_file(args.archivo)
    codigo = construir_codigo(asa)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(codigo)
        print(f"[GENERADOR] Código escrito en {args.output}")
    else:
        print(codigo)


if __name__ == '__main__':
    main()
