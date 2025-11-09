"""
Analizador sintáctico por descenso recursivo para Olympiac.
Consume tokens producidos por explorador.AnalizadorLexico y construye un asa usando nodo.asaNode.

Uso:
    from analizador_sintactico import parse_from_file
    asa = parse_from_file("ejemplo1.oly")
    for linea in asa.preorder_lines():
        print(linea)
"""
from typing import List, Optional
from explorador import AnalizadorLexico, TokenLexico, TipoToken
from nodo import asaNode


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, tokens: List[TokenLexico]):
        self.tokens = tokens
        self.pos = 0

    # helpers
    def peek(self) -> Optional[TokenLexico]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self) -> Optional[TokenLexico]:
        t = self.peek()
        if t:
            self.pos += 1
        return t

    def expect(self, tipo: Optional[TipoToken] = None, texto: Optional[str] = None, mensaje: str = "Token inesperado") -> TokenLexico:
        t = self.peek()
        if not t:
            raise ParserError(f"{mensaje}: fin de archivo")
        if tipo and t.tipo_token != tipo:
            raise ParserError(f"{mensaje}: se esperaba tipo {tipo.name} pero se encontró {t.tipo_token.name} ('{t.texto_original}') en línea {t.numero_linea}, col {t.posicion_columna}")
        if texto and t.texto_original.lower() != texto.lower():
            raise ParserError(f"{mensaje}: se esperaba '{texto}' pero se encontró '{t.texto_original}' en línea {t.numero_linea}, col {t.posicion_columna}")
        return self.advance()

    def match_text(self, texto: str) -> bool:
        t = self.peek()
        return bool(t and t.texto_original.lower() == texto.lower())

    # entrada principal
    def parse_program(self) -> asaNode:
        raiz = asaNode("Programa", "root")
        while self.peek():
            nodo = self.parse_comando()
            if nodo:
                raiz.agregar_hijo(nodo)
            else:
                break
        return raiz

    # Comando ::= Declarar | Condicional | Repetir | RepetirHasaa | Narrar | Bloque | Dirigir | Comentario
    def parse_comando(self) -> Optional[asaNode]:
        t = self.peek()
        if not t:
            return None

        if t.tipo_token == TipoToken.COMENTARIO:
            tok = self.advance()
            return asaNode("Comentario", tok.texto_original, {"linea": tok.numero_linea})

        if t.tipo_token == TipoToken.DECLARACION_ENTIDAD:
            if t.texto_original.lower() == "deportista":
                return self.parse_deportista()
            if t.texto_original.lower() == "lista":
                return self.parse_lista_o_carga()
            # fallback
            tok = self.advance()
            return asaNode("Declaracion", tok.texto_original, {"linea": tok.numero_linea})

        if t.tipo_token == TipoToken.ESTRUCTURA_CONTROL_FLUJO:
            txt = t.texto_original.lower()
            if txt == "si":
                return self.parse_condicional()
            if txt == "repetir":
                return self.parse_repetir()
            if txt == "repetirhasaa":
                return self.parse_repetir_hasaa()
            # cierres sueltos
            if txt in ("finrep", "finrephasa", "endif"):
                tok = self.advance()
                return asaNode("Cierre", tok.texto_original, {"linea": tok.numero_linea})

        if t.tipo_token == TipoToken.INVOCACION_FUNCION:
            txt = t.texto_original.lower()
            if txt.startswith("narrar"):
                return self.parse_narrar()
            if txt.startswith("input"):
                return self.parse_dirigir()
            # Comparar u otra invocación suelta
            return self.parse_invocacion_generica()

        if t.tipo_token == TipoToken.NOMBRE_IDENTIFICADOR:
            tok = self.advance()
            return asaNode("Identificador", tok.texto_original, {"linea": tok.numero_linea})

        if t.tipo_token == TipoToken.SIMBOLO_PUNTUACION:
            tok = self.advance()
            return asaNode("Simbolo", tok.texto_original, {"linea": tok.numero_linea})

        # fallback
        tok = self.advance()
        return asaNode("Unknown", tok.texto_original, {"linea": tok.numero_linea})

    # Declaraciones
    def parse_deportista(self) -> asaNode:
        tok_decl = self.expect(TipoToken.DECLARACION_ENTIDAD, texto="Deportista")
        nombre = self.expect(TipoToken.NOMBRE_IDENTIFICADOR)
        est = []
        for _ in range(3):
            num = self.expect(TipoToken.NUMERO_ENTERO)
            est.append(num.texto_original)
        deporte = self.expect(TipoToken.NOMBRE_IDENTIFICADOR)
        pais = self.expect(TipoToken.NOMBRE_IDENTIFICADOR)
        atributos = {"nombre": nombre.texto_original, "estadisticas": est, "deporte": deporte.texto_original, "pais": pais.texto_original, "linea": tok_decl.numero_linea}
        return asaNode("Deportista", nombre.texto_original, atributos)

    def parse_lista_o_carga(self) -> asaNode:
        tok = self.expect(TipoToken.DECLARACION_ENTIDAD, texto="Lista")
        siguiente = self.peek()
        if siguiente and siguiente.tipo_token == TipoToken.DECLARACION_ENTIDAD and siguiente.texto_original.lower() == "deportista":
            # Carga: Lista Deportista deportista+ (heurística)
            self.advance()
            deportistas = []
            # If the next token is an identifier but not followed by 3 numbers,
            # treat it as a named list declaration: 'Lista Deportista List_est_dep'
            p = self.peek()
            if p and p.tipo_token == TipoToken.NOMBRE_IDENTIFICADOR:
                # lookahead to see if a full deportista entry follows (name + 3 numbers)
                lookahead_ok = True
                for i in range(3):
                    la_pos = self.pos + i
                    if la_pos >= len(self.tokens) or self.tokens[la_pos].tipo_token != TipoToken.NUMERO_ENTERO:
                        lookahead_ok = False
                        break
                if not lookahead_ok:
                    # treat as named list declaration
                    nombre = self.advance()
                    atributos = {"tipo": "Deportista", "nombre": nombre.texto_original, "linea": tok.numero_linea}
                    return asaNode("Lista", atributos.get("nombre", ""), atributos)

            # intentar parsear bloques tipo: Nombre 3nums Deporte Pais repetidos
            while True:
                p = self.peek()
                if p and p.tipo_token == TipoToken.NOMBRE_IDENTIFICADOR:
                    try:
                        nombre = self.advance()
                        est = [self.expect(TipoToken.NUMERO_ENTERO).texto_original for _ in range(3)]
                        deporte = self.expect(TipoToken.NOMBRE_IDENTIFICADOR)
                        pais = self.expect(TipoToken.NOMBRE_IDENTIFICADOR)
                        deportistas.append({"nombre": nombre.texto_original, "estadisticas": est, "deporte": deporte.texto_original, "pais": pais.texto_original})
                    except ParserError:
                        break
                else:
                    break
            return asaNode("CargaDeportistas", "Lista Deportista", {"deportistas": deportistas, "linea": tok.numero_linea})
        else:
            tipo = None
            if self.peek() and self.peek().tipo_token in (TipoToken.NOMBRE_IDENTIFICADOR, TipoToken.DECLARACION_ENTIDAD):
                tipo = self.advance()
            nombre = None
            if self.peek() and self.peek().tipo_token == TipoToken.NOMBRE_IDENTIFICADOR:
                nombre = self.advance()
            atributos = {"tipo": tipo.texto_original if tipo else None, "nombre": nombre.texto_original if nombre else None, "linea": tok.numero_linea}
            return asaNode("Lista", atributos.get("nombre", ""), atributos)

    # Invocaciones y funciones
    def parse_narrar(self) -> asaNode:
        tok = self.expect(TipoToken.INVOCACION_FUNCION)
        args = []
        # leer hasaa ')'
        while (p := self.peek()) and p.texto_original != ")":
            if p.tipo_token == TipoToken.SIMBOLO_PUNTUACION and p.texto_original == ",":
                self.advance(); continue
            args.append(self.advance().texto_original)
        if self.peek() and self.peek().texto_original == ")":
            self.advance()
        return asaNode("Narrar", tok.texto_original, {"args": args, "linea": tok.numero_linea})

    def parse_dirigir(self) -> asaNode:
        tok = self.expect(TipoToken.INVOCACION_FUNCION)  # input(
        args = []
        while (p := self.peek()) and p.texto_original != ")":
            if p.tipo_token == TipoToken.SIMBOLO_PUNTUACION and p.texto_original == ",":
                self.advance(); continue
            args.append(self.advance().texto_original)
        if self.peek() and self.peek().texto_original == ")":
            self.advance()
        return asaNode("Dirigir", tok.texto_original, {"args": args, "linea": tok.numero_linea})

    def parse_invocacion_generica(self) -> asaNode:
        tok = self.expect(TipoToken.INVOCACION_FUNCION)
        nombre = tok.texto_original
        args = []
        while (p := self.peek()) and p.texto_original != ")":
            if p.tipo_token == TipoToken.SIMBOLO_PUNTUACION and p.texto_original == ",":
                self.advance(); continue
            args.append(self.advance().texto_original)
        if self.peek() and self.peek().texto_original == ")":
            self.advance()
        return asaNode("Invocacion", nombre, {"args": args, "linea": tok.numero_linea})

    # Condicional
    def parse_condicional(self) -> asaNode:
        si_tok = self.expect(TipoToken.ESTRUCTURA_CONTROL_FLUJO, texto="si")
        condicion = self.parse_condicion_expresion()
        if self.peek() and self.peek().texto_original.lower() == "entonces":
            self.advance()
        if self.peek() and self.peek().texto_original == "{":
            self.advance()
        cuerpo = []
        while (p := self.peek()) and p.texto_original.lower() not in ("}", "sino", "endif"):
            nodo = self.parse_comando()
            if nodo:
                cuerpo.append(nodo)
            else:
                break
        sino_bloque = None
        if self.peek() and self.peek().texto_original.lower() == "sino":
            self.advance()
            if self.peek() and self.peek().texto_original == "{":
                self.advance()
            sino_bloque = []
            while (p := self.peek()) and p.texto_original.lower() not in ("}", "endif"):
                s = self.parse_comando()
                if s:
                    sino_bloque.append(s)
                else:
                    break
        if self.peek() and self.peek().texto_original == "}":
            self.advance()
        if self.peek() and self.peek().texto_original.lower() == "endif":
            self.advance()
        nodo = asaNode("Condicional", "si", {"condicion": condicion.contenido, "linea": si_tok.numero_linea})
        nodo.hijos = cuerpo
        if sino_bloque:
            nodo.agregar_hijo(asaNode("Sino", "", {}, sino_bloque))
        return nodo

    def parse_condicion_expresion(self) -> asaNode:
        left = self.parse_expression()
        if (p := self.peek()) and p.tipo_token == TipoToken.OPERADOR_COMPARACION:
            op = self.advance()
            right = self.parse_expression()
            node = asaNode("Condicion", f"{left.contenido} {op.texto_original} {right.contenido}", {}, [left, asaNode("Op", op.texto_original), right])
            return node
        return left

    # Repetir y RepetirHasaa
    def parse_repetir(self) -> asaNode:
        tok = self.expect(TipoToken.ESTRUCTURA_CONTROL_FLUJO, texto="Repetir")
        # aceptar '(' opcional (lex puede haber incluido en INVOCACION_FUNCION o SIMBOLO)
        if self.peek() and self.peek().texto_original == "(":
            self.advance()
        count = self.parse_expression()
        if self.peek() and self.peek().texto_original == ")":
            self.advance()
        if self.peek() and self.peek().texto_original == "[":
            self.advance()
        cuerpo = []
        while (p := self.peek()) and p.texto_original.lower() not in ("finrep", "]"):
            n = self.parse_comando()
            if n:
                cuerpo.append(n)
            else:
                break
        if self.peek() and self.peek().texto_original == "]":
            self.advance()
        if self.peek() and self.peek().texto_original.lower() == "finrep":
            self.advance()
        return asaNode("Repetir", count.contenido, {}, cuerpo)

    def parse_repetir_hasaa(self) -> asaNode:
        tok = self.expect(TipoToken.ESTRUCTURA_CONTROL_FLUJO, texto="RepetirHasaa")
        if self.peek() and self.peek().texto_original == "(":
            self.advance()
        condicion = self.parse_condicion_expresion()
        if self.peek() and self.peek().texto_original == ")":
            self.advance()
        if self.peek() and self.peek().texto_original == "[":
            self.advance()
        cuerpo = []
        while (p := self.peek()) and p.texto_original.lower() not in ("finrephasa", "]"):
            n = self.parse_comando()
            if n:
                cuerpo.append(n)
            else:
                break
        if self.peek() and self.peek().texto_original == "]":
            self.advance()
        if self.peek() and self.peek().texto_original.lower() == "finrephasa":
            self.advance()
        return asaNode("RepetirHasaa", condicion.contenido, {}, cuerpo)

    # Expresiones (precedencia)
    def parse_expression(self) -> asaNode:
        return self.parse_comparison()

    def parse_comparison(self) -> asaNode:
        node = self.parse_add()
        while (p := self.peek()) and p.tipo_token == TipoToken.OPERADOR_COMPARACION:
            op = self.advance()
            right = self.parse_add()
            node = asaNode("BinaryOp", op.texto_original, {}, [node, right])
        return node

    def parse_add(self) -> asaNode:
        node = self.parse_mul()
        while (p := self.peek()) and p.tipo_token == TipoToken.OPERADOR_ARITMETICO and p.texto_original in ("+", "-"):
            op = self.advance()
            right = self.parse_mul()
            node = asaNode("BinaryOp", op.texto_original, {}, [node, right])
        return node

    def parse_mul(self) -> asaNode:
        node = self.parse_unary()
        while (p := self.peek()) and p.tipo_token == TipoToken.OPERADOR_ARITMETICO and p.texto_original in ("*", "/", "%"):
            op = self.advance()
            right = self.parse_unary()
            node = asaNode("BinaryOp", op.texto_original, {}, [node, right])
        return node

    def parse_unary(self) -> asaNode:
        if (p := self.peek()) and p.tipo_token == TipoToken.OPERADOR_ARITMETICO and p.texto_original in ("+", "-"):
            op = self.advance()
            node = self.parse_unary()
            return asaNode("UnaryOp", op.texto_original, {}, [node])
        return self.parse_primary()

    def parse_primary(self) -> asaNode:
        p = self.peek()
        if not p:
            raise ParserError("Expresión incompleta: EOF")
        if p.tipo_token == TipoToken.NUMERO_ENTERO:
            n = self.advance()
            return asaNode("Numero", n.texto_original, {"linea": n.numero_linea})
        if p.tipo_token == TipoToken.NOMBRE_IDENTIFICADOR:
            v = self.advance()
            return asaNode("Nombre", v.texto_original, {"linea": v.numero_linea})
        if p.tipo_token == TipoToken.INVOCACION_FUNCION:
            inv = self.parse_invocacion_generica()
            return inv
        if p.tipo_token == TipoToken.SIMBOLO_PUNTUACION and p.texto_original == "(":
            self.advance()
            node = self.parse_expression()
            if self.peek() and self.peek().texto_original == ")":
                self.advance()
            return node
        # fallback
        tok = self.advance()
        return asaNode("PrimaryUnknown", tok.texto_original, {"linea": tok.numero_linea})

# Integración con explorador
def parse_from_tokens(tokens: List[TokenLexico]) -> asaNode:
    parser = Parser(tokens)
    return parser.parse_program()


def parse_from_file(path: str) -> asaNode:
    with open(path, encoding="utf-8") as f:
        lineas = [l.rstrip("\n\r") for l in f.readlines()]
    lex = AnalizadorLexico(lineas)
    lex.analizar_codigo_completo()
    tokens = lex.obtener_tokens()
    return parse_from_tokens(tokens)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python analizador_sintactico.py archivo.oly")
    else:
        asa = parse_from_file(sys.argv[1])
        for linea in asa.preorder_lines():
            print(linea)