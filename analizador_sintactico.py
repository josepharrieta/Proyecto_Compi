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
        self.errors: List[dict] = []  # acumulación de errores sintácticos
        self.sync_tokens = {"deportista","lista","si","repetir","repetirhasta","finrep","finrephast","endif","sino","narrar","input","finact","fincarr","finruti"}
        # Conjunto para deduplicar errores (mensaje, linea, columna)
        self._error_keys = set()

    # helpers
    def peek(self) -> Optional[TokenLexico]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self) -> Optional[TokenLexico]:
        t = self.peek()
        if t:
            self.pos += 1
        return t

    def expect(self, tipo: Optional[TipoToken] = None, texto: Optional[str] = None, mensaje: str = "Token inesperado") -> Optional[TokenLexico]:
        t = self.peek()
        if not t:
            self._report_error(f"{mensaje}: fin de archivo (EOF)", None)
            return None
        if tipo and t.tipo_token != tipo:
            self._report_error(f"{mensaje}: se esperaba tipo {tipo.name} y llegó {t.tipo_token.name} ('{t.texto_original}')", t)
            self.synchronize()
            return None
        if texto and t.texto_original.lower() != texto.lower():
            self._report_error(f"{mensaje}: se esperaba '{texto}' y llegó '{t.texto_original}'", t)
            self.synchronize()
            return None
        return self.advance()

    def match_text(self, texto: str) -> bool:
        t = self.peek()
        return bool(t and t.texto_original.lower() == texto.lower())

    def _report_error(self, msg: str, tok: Optional[TokenLexico]):
        linea = tok.numero_linea if tok else None
        columna = tok.posicion_columna if tok else None
        key = (msg, linea, columna)
        # Evitar duplicados consecutivos exactos
        if key in self._error_keys:
            return
        self._error_keys.add(key)
        self.errors.append({
            "mensaje": msg,
            "linea": linea,
            "columna": columna
        })

    def synchronize(self):
        """Recuperación tras error.

        Estrategia B mejorada:
        1. Avanzar tokens hasta encontrar un "ancla" sintáctica:
           - Declaración (DECLARACION_ENTIDAD)
           - Control de flujo (ESTRUCTURA_CONTROL_FLUJO)
           - Palabra clave (PALABRA_CLAVE)
           - Invocación de función (INVOCACION_FUNCION) al inicio de una nueva línea
           - Símbolos de cierre de bloque } ] )
        2. Si no se encuentra ancla en la misma línea del error, saltar a la siguiente línea y buscar allí.
        3. Limitar el número de pasos para evitar loops.
        """
        if not self.peek():
            return
        start_line = self.peek().numero_linea
        max_steps = 500
        steps = 0
        anchor_types = {TipoToken.DECLARACION_ENTIDAD, TipoToken.ESTRUCTURA_CONTROL_FLUJO, TipoToken.PALABRA_CLAVE}
        closing_symbols = {'}', ']', ')'}
        while self.peek() and steps < max_steps:
            t = self.peek()
            # Condición de ancla por tipo
            if t.tipo_token in anchor_types:
                break
            # Invocación como inicio potencial (si cambia de línea respecto al error)
            if t.tipo_token == TipoToken.INVOCACION_FUNCION and t.numero_linea != start_line:
                break
            # Símbolo de cierre como frontera natural
            if t.tipo_token == TipoToken.SIMBOLO_PUNTUACION and t.texto_original in closing_symbols:
                break
            # Token manual listado en sync_tokens y cambio de línea
            if t.texto_original.lower() in self.sync_tokens and t.numero_linea != start_line:
                break
            self.pos += 1
            steps += 1
        # Si se alcanzó el límite, consumir todo para evitar bloqueo
        if steps >= max_steps:
            while self.peek():
                self.pos += 1

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
        # Comentario
        if t.tipo_token == TipoToken.COMENTARIO:
            tok = self.advance()
            return asaNode("Comentario", tok.texto_original, {"linea": tok.numero_linea})
        # Declaraciones
        if t.tipo_token == TipoToken.DECLARACION_ENTIDAD:
            txt = t.texto_original.lower()
            if txt == "deportista":
                return self.parse_deportista()
            if txt == "lista":
                return self.parse_lista_o_carga()
        # Control de flujo
        if t.tipo_token == TipoToken.ESTRUCTURA_CONTROL_FLUJO:
            txt = t.texto_original.lower()
            if txt == "si":
                return self.parse_condicional()
            if txt == "repetir":
                return self.parse_repetir()
            if txt == "repetirhasta":
                return self.parse_repetir_hasta()
            if txt in ("finrep","finrephast","endif"):
                tok = self.advance()
                return asaNode("Cierre", tok.texto_original, {"linea": tok.numero_linea})
        # Invocaciones
        if t.tipo_token == TipoToken.INVOCACION_FUNCION:
            low = t.texto_original.lower()
            if low.startswith("narrar"):
                return self.parse_narrar()
            if low.startswith("input"):
                return self.parse_dirigir()
            if low.startswith("comparar"):
                return self.parse_invocacion_generica()
            return self.parse_invocacion_generica()
        # Acciones y palabras clave de competencia (Partido, Carrera, Combate, Rutina, preparacion, finact, etc.)
        if t.tipo_token == TipoToken.PALABRA_CLAVE:
            clave = t.texto_original
            low = clave.lower()
            # Cierres simples
            if low == 'finact':
                tok = self.advance()
                return asaNode("FinAct", tok.texto_original, {"linea": tok.numero_linea})
            if low == 'fincarr':
                tok = self.advance()
                return asaNode("FinCarr", tok.texto_original, {"linea": tok.numero_linea})
            if low == 'finruti':
                tok = self.advance()
                return asaNode("FinRuti", tok.texto_original, {"linea": tok.numero_linea})
            if low == 'fincomb':
                tok = self.advance()
                return asaNode("FinComb", tok.texto_original, {"linea": tok.numero_linea})
            # Entradas a estructuras
            if low == 'iniciocarrera':
                return self.parse_carrera()
            if low == 'iniciorutina':
                return self.parse_rutina()
            if low == 'iniciocombate':
                return self.parse_combate()
            # Otros keywords se devuelven como nodos simples (preparacion, ejecutar, correr, finprep etc.)
            if low in ('preparacion','ejecutar','correr','finprep'):
                tok = self.advance()
                return asaNode("Clave", tok.texto_original, {"linea": tok.numero_linea})
            # Stub para cualquier otra acción compleja aún no modelada
            return self.parse_accion_stub()
        # Resultado ::= "Resultado" Numero "-" Numero
        if t.tipo_token == TipoToken.TIPO_DATO_DOMINIO and t.texto_original == "Resultado":
            return self.parse_resultado()
        # ResultadoExtra ::= "listaRes"
        if t.tipo_token == TipoToken.RESULTADO_ADICIONAL:
            return self.parse_resultado_extra()
        # Empate ::= "empate"
        if t.tipo_token == TipoToken.CONDICION_EMPATE:
            return self.parse_empate()
        # Partido: patrón Identificador 'vs' Identificador al inicio de línea
        if t.tipo_token == TipoToken.NOMBRE_IDENTIFICADOR and self.pos + 1 < len(self.tokens):
            nxt = self.tokens[self.pos + 1]
            if nxt.tipo_token == TipoToken.OPERADOR_ESPECIAL and nxt.texto_original.lower() == 'vs':
                return self.parse_partido()
        # Identificador / símbolo para patrones avanzados (lista.agregar) aislados
        if t.tipo_token == TipoToken.NOMBRE_IDENTIFICADOR:
            tok = self.advance()
            return asaNode("Identificador", tok.texto_original, {"linea": tok.numero_linea})
        if t.tipo_token == TipoToken.SIMBOLO_PUNTUACION:
            tok = self.advance()
            return asaNode("Simbolo", tok.texto_original, {"linea": tok.numero_linea})
        # Fallback
        tok = self.advance()
        self._report_error("Token fuera de producción Comando", tok)
        return asaNode("Unknown", tok.texto_original, {"linea": tok.numero_linea})

    # Declaraciones
    def parse_deportista(self) -> asaNode:
        tok_decl = self.expect(TipoToken.DECLARACION_ENTIDAD, texto="Deportista")
        nombre = self.expect(TipoToken.NOMBRE_IDENTIFICADOR)
        est = []
        for _ in range(3):
            num = self.expect(TipoToken.NUMERO_ENTERO)
            # proteger acceso si num es None
            est.append(num.texto_original if num else None)
        deporte = self.expect(TipoToken.NOMBRE_IDENTIFICADOR)
        pais = self.expect(TipoToken.NOMBRE_IDENTIFICADOR)

        # Si la declaración base 'Deportista' faltó, reportar y devolver nodo de error
        if not tok_decl:
            self._report_error("Declaración 'Deportista' inválida o incompleta", nombre)
            return asaNode("ErrorSintactico", "Deportista", {"linea": nombre.numero_linea if nombre else None})

        atributos = {
            "nombre": nombre.texto_original if nombre else None,
            "estadisticas": est,
            "deporte": deporte.texto_original if deporte else None,
            "pais": pais.texto_original if pais else None,
            "linea": tok_decl.numero_linea
        }

        # Si faltan elementos críticos, reportar pero no lanzar excepción
        if not nombre or not deporte or not pais or any(x is None for x in est):
            self._report_error("Declaración 'Deportista' incompleta (faltan campos)", tok_decl)
            return asaNode("ErrorSintactico", "DeportistaIncompleto", atributos)

        return asaNode("Deportista", atributos["nombre"], atributos)

    def parse_lista_o_carga(self) -> asaNode:
        tok_lista = self.expect(TipoToken.DECLARACION_ENTIDAD, texto="Lista")
        if not tok_lista:
            return asaNode("ErrorSintactico", "Lista", {"linea": None})
        
        # Lookahead para decidir: ¿Es declaración simple o carga masiva?
        if self.peek() and self.peek().tipo_token == TipoToken.DECLARACION_ENTIDAD and self.peek().texto_original.lower() == "deportista":
            # Peek ahead: después de Deportista, ¿viene un nombre simple o nombre+números?
            saved_pos = self.pos
            tipo_token = self.advance()  # consume 'Deportista'
            
            # Si el siguiente token es nombre, puede ser carga masiva o declaración simple
            if (self.peek() and self.peek().tipo_token == TipoToken.NOMBRE_IDENTIFICADOR):
                nombre_token = self.peek()
                # Intentar mirar un token más adelante para detectar carga masiva
                # Carga masiva: nombre NUMERO NUMERO NUMERO ...
                # Declaración simple: nombre (y luego EOF o comentario o siguiente comando)
                
                # Hacemos lookahead: si después del nombre viene un número, es carga masiva
                self.advance()  # consume el nombre
                es_carga_masiva = False
                if self.peek() and self.peek().tipo_token == TipoToken.NUMERO_ENTERO:
                    es_carga_masiva = True
                
                # Restaurar posición a después de 'Deportista'
                self.pos = saved_pos
                
                if es_carga_masiva:
                    # Parsear carga masiva
                    deportistas = []
                    while self.peek() and self.peek().tipo_token == TipoToken.NOMBRE_IDENTIFICADOR:
                        start_pos = self.pos
                        nombre = self.advance()
                        numeros = []
                        for _ in range(3):
                            if self.peek() and self.peek().tipo_token == TipoToken.NUMERO_ENTERO:
                                numeros.append(self.advance().texto_original)
                            else:
                                self.pos = start_pos
                                break
                        if len(numeros) != 3:
                            break
                        deporte = self.expect(TipoToken.NOMBRE_IDENTIFICADOR)
                        pais = self.expect(TipoToken.NOMBRE_IDENTIFICADOR)
                        if not (deporte and pais):
                            break
                        deportistas.append({
                            "nombre": nombre.texto_original,
                            "estadisticas": numeros,
                            "deporte": deporte.texto_original,
                            "pais": pais.texto_original
                        })
                    
                    if deportistas:
                        return asaNode("CargaDeportistas", "Lista Deportista", {"deportistas": deportistas, "linea": tok_lista.numero_linea})
                    else:
                        # No era carga masiva válida, retroceder a posición original
                        self.pos = saved_pos
                else:
                    # Es declaración simple: ya estamos en saved_pos (después de Deportista)
                    pass
        
        # Declaración simple: Lista Tipo Nombre
        # El tipo puede ser DECLARACION_ENTIDAD (Deportista) o NOMBRE_IDENTIFICADOR
        tipo = None
        if self.peek() and self.peek().tipo_token == TipoToken.DECLARACION_ENTIDAD and self.peek().texto_original.lower() == "deportista":
            tipo = self.advance()
        else:
            tipo = self.expect(TipoToken.NOMBRE_IDENTIFICADOR, mensaje="Tipo de lista inválido")
        
        nombre = self.expect(TipoToken.NOMBRE_IDENTIFICADOR, mensaje="Nombre de lista faltante")
        atributos = {
            "tipo": tipo.texto_original if tipo else None,
            "nombre": nombre.texto_original if nombre else None,
            "linea": tok_lista.numero_linea
        }
        return asaNode("Lista", atributos.get("nombre", ""), atributos)

    # Invocaciones y funciones
    def parse_narrar(self) -> asaNode:
        tok = self.expect(TipoToken.INVOCACION_FUNCION)
        # esperamos narrar( Nombre )
        args = []
        while self.peek() and self.peek().texto_original != ")":
            if self.peek().tipo_token == TipoToken.NOMBRE_IDENTIFICADOR:
                args.append(self.advance().texto_original)
            else:
                self._report_error("Argumento de narrar debe ser identificador (Nombre)", self.peek())
                self.advance()
        if self.peek() and self.peek().texto_original == ")":
            self.advance()
        # validar aridad 1
        if len(args) != 1:
            self._report_error(f"narrar requiere exactamente 1 Nombre, se encontró {len(args)}", tok)
        # proteger atributos si tok es None
        contenido = (tok.texto_original[:-1] if tok and tok.texto_original.endswith('(') else (tok.texto_original if tok else "narrar"))
        linea = tok.numero_linea if tok else None
        return asaNode("Narrar", contenido, {"args": args, "linea": linea})

    def parse_dirigir(self) -> asaNode:
        tok = self.expect(TipoToken.INVOCACION_FUNCION)  # input(
        args = []
        while (p := self.peek()) and p.texto_original != ")":
            if p.tipo_token == TipoToken.SIMBOLO_PUNTUACION and p.texto_original == ",":
                self.advance(); continue
            args.append(self.advance().texto_original)
        if self.peek() and self.peek().texto_original == ")":
            self.advance()
        contenido = (tok.texto_original[:-1] if tok and tok.texto_original.endswith('(') else (tok.texto_original if tok else "input"))
        linea = tok.numero_linea if tok else None
        return asaNode("Dirigir", contenido, {"args": args, "linea": linea})

    def parse_invocacion_generica(self) -> asaNode:
        tok = self.expect(TipoToken.INVOCACION_FUNCION)
        nombre = (tok.texto_original[:-1] if tok and tok.texto_original.endswith('(') else (tok.texto_original if tok else "invocacion"))
        args = []
        while (p := self.peek()) and p.texto_original != ")":
            if p.tipo_token == TipoToken.SIMBOLO_PUNTUACION and p.texto_original == ",":
                self.advance(); continue
            args.append(self.advance().texto_original)
        if self.peek() and self.peek().texto_original == ")":
            self.advance()
        linea = tok.numero_linea if tok else None
        return asaNode("Invocacion", nombre, {"args": args, "linea": linea})

    # Resultado ::= "Resultado" Numero "-" Numero
    def parse_resultado(self) -> asaNode:
        tok_res = self.expect(TipoToken.TIPO_DATO_DOMINIO, texto="Resultado", mensaje="Se esperaba 'Resultado'")
        num1 = self.expect(TipoToken.NUMERO_ENTERO, mensaje="Resultado requiere primer número")
        self.expect(TipoToken.SIMBOLO_PUNTUACION, texto="-", mensaje="Resultado requiere '-' entre números")
        num2 = self.expect(TipoToken.NUMERO_ENTERO, mensaje="Resultado requiere segundo número")
        atributos = {
            "linea": tok_res.numero_linea if tok_res else None,
            "valores": [num1.texto_original if num1 else None, num2.texto_original if num2 else None]
        }
        return asaNode("Resultado", "Resultado", atributos)

    # ResultadoExtra ::= "listaRes"
    def parse_resultado_extra(self) -> asaNode:
        tok = self.expect(TipoToken.RESULTADO_ADICIONAL, texto="listaRes", mensaje="Se esperaba 'listaRes'")
        return asaNode("ResultadoExtra", tok.texto_original if tok else "listaRes", {"linea": tok.numero_linea if tok else None})

    # Empate ::= "empate"
    def parse_empate(self) -> asaNode:
        tok = self.expect(TipoToken.CONDICION_EMPATE, texto="empate", mensaje="Se esperaba 'empate'")
        return asaNode("Empate", tok.texto_original if tok else "empate", {"linea": tok.numero_linea if tok else None})

    # Partido ::= PaisA 'vs' PaisB Accion* [Empate] Resultado ResultadoExtra* 'finact'
    def parse_partido(self) -> asaNode:
        paisA = self.expect(TipoToken.NOMBRE_IDENTIFICADOR, mensaje="Partido requiere primer país")
        self.expect(TipoToken.OPERADOR_ESPECIAL, texto="vs", mensaje="Partido requiere 'vs' entre países")
        paisB = self.expect(TipoToken.NOMBRE_IDENTIFICADOR, mensaje="Partido requiere segundo país")
        acciones = []
        empate_node = None
        resultado_node = None
        extras = []
        # Consumir acciones hasta ver Resultado / finact
        while self.peek():
            p = self.peek()
            low = p.texto_original.lower()
            # Resultado marca transición a etapa final
            if p.tipo_token == TipoToken.TIPO_DATO_DOMINIO and low == 'resultado':
                resultado_node = self.parse_resultado()
                # Posibles extras y/o empate después del resultado
                while self.peek() and self.peek().texto_original.lower() in ("listares","empate"):
                    if self.peek().tipo_token == TipoToken.RESULTADO_ADICIONAL:
                        extras.append(self.parse_resultado_extra())
                        continue
                    if self.peek().tipo_token == TipoToken.CONDICION_EMPATE:
                        # Si aparece empate después del resultado lo aceptamos pero advertimos
                        if not empate_node:
                            empate_node = self.parse_empate()
                        else:
                            self._report_error("Empate duplicado en Partido", self.peek())
                        continue
                    break
                break  # tras resultado y extras pasamos a cierre
            if p.tipo_token == TipoToken.CONDICION_EMPATE and low == 'empate':
                if not empate_node:
                    empate_node = self.parse_empate()
                else:
                    self._report_error("Empate duplicado en Partido", p)
                continue
            if p.tipo_token == TipoToken.PALABRA_CLAVE and low == 'finact':
                break
            # Acción interna genérica: reutilizamos parse_comando para nodos contenidos
            acc = self.parse_comando()
            if acc:
                acciones.append(acc)
            else:
                break
        # Cierre obligatorio finact
        if self.peek() and self.peek().tipo_token == TipoToken.PALABRA_CLAVE and self.peek().texto_original.lower() == 'finact':
            self.advance()  # consume finact
        else:
            self._report_error("Se esperaba 'finact' al final de Partido", self.peek())
        if not resultado_node:
            self._report_error("Partido requiere 'Resultado' antes de 'finact'", self.peek())
        atributos = {
            "paisA": paisA.texto_original if paisA else None,
            "paisB": paisB.texto_original if paisB else None,
            "linea": paisA.numero_linea if paisA else (paisB.numero_linea if paisB else None)
        }
        nodo = asaNode("Partido", f"{atributos['paisA']} vs {atributos['paisB']}", atributos)
        for a in acciones:
            nodo.agregar_hijo(a)
        if empate_node:
            nodo.agregar_hijo(empate_node)
        if resultado_node:
            nodo.agregar_hijo(resultado_node)
        for e in extras:
            nodo.agregar_hijo(e)
        return nodo

    # Carrera ::= 'InicioCarrera' Accion* Resultado ResultadoExtra* 'finCarr'
    def parse_carrera(self) -> asaNode:
        inicio = self.expect(TipoToken.PALABRA_CLAVE, texto="InicioCarrera", mensaje="Se esperaba 'InicioCarrera'")
        acciones = []
        resultado_node = None
        extras = []
        while self.peek():
            p = self.peek()
            low = p.texto_original.lower()
            if p.tipo_token == TipoToken.TIPO_DATO_DOMINIO and low == 'resultado':
                resultado_node = self.parse_resultado()
                while self.peek() and self.peek().texto_original.lower() == 'listares':
                    extras.append(self.parse_resultado_extra())
                break
            if p.tipo_token == TipoToken.PALABRA_CLAVE and low == 'fincarr':
                break
            acc = self.parse_comando()
            if acc:
                acciones.append(acc)
            else:
                break
        if self.peek() and self.peek().tipo_token == TipoToken.PALABRA_CLAVE and self.peek().texto_original.lower() == 'fincarr':
            self.advance()
        else:
            self._report_error("Se esperaba 'finCarr' al final de Carrera", self.peek())
        if not resultado_node:
            self._report_error("Carrera requiere 'Resultado' antes de 'finCarr'", self.peek())
        atributos = {"linea": inicio.numero_linea if inicio else None}
        nodo = asaNode("Carrera", "InicioCarrera", atributos)
        for a in acciones:
            nodo.agregar_hijo(a)
        if resultado_node:
            nodo.agregar_hijo(resultado_node)
        for e in extras:
            nodo.agregar_hijo(e)
        return nodo

    # Rutina ::= 'InicioRutina' Accion* Resultado ResultadoExtra* 'finRuti'
    def parse_rutina(self) -> asaNode:
        inicio = self.expect(TipoToken.PALABRA_CLAVE, texto="InicioRutina", mensaje="Se esperaba 'InicioRutina'")
        acciones = []
        resultado_node = None
        extras = []
        while self.peek():
            p = self.peek()
            low = p.texto_original.lower()
            if p.tipo_token == TipoToken.TIPO_DATO_DOMINIO and low == 'resultado':
                resultado_node = self.parse_resultado()
                while self.peek() and self.peek().texto_original.lower() == 'listares':
                    extras.append(self.parse_resultado_extra())
                break
            if p.tipo_token == TipoToken.PALABRA_CLAVE and low == 'finruti':
                break
            acc = self.parse_comando()
            if acc:
                acciones.append(acc)
            else:
                break
        if self.peek() and self.peek().tipo_token == TipoToken.PALABRA_CLAVE and self.peek().texto_original.lower() == 'finruti':
            self.advance()
        else:
            self._report_error("Se esperaba 'finRuti' al final de Rutina", self.peek())
        if not resultado_node:
            self._report_error("Rutina requiere 'Resultado' antes de 'finRuti'", self.peek())
        atributos = {"linea": inicio.numero_linea if inicio else None}
        nodo = asaNode("Rutina", "InicioRutina", atributos)
        for a in acciones:
            nodo.agregar_hijo(a)
        if resultado_node:
            nodo.agregar_hijo(resultado_node)
        for e in extras:
            nodo.agregar_hijo(e)
        return nodo

    # Combate ::= 'InicioCombate' Accion* Resultado ResultadoExtra* 'finComb'
    def parse_combate(self) -> asaNode:
        inicio = self.expect(TipoToken.PALABRA_CLAVE, texto="InicioCombate", mensaje="Se esperaba 'InicioCombate'")
        acciones = []
        resultado_node = None
        extras = []
        while self.peek():
            p = self.peek()
            low = p.texto_original.lower()
            if p.tipo_token == TipoToken.TIPO_DATO_DOMINIO and low == 'resultado':
                resultado_node = self.parse_resultado()
                while self.peek() and self.peek().texto_original.lower() == 'listares':
                    extras.append(self.parse_resultado_extra())
                break
            if p.tipo_token == TipoToken.PALABRA_CLAVE and low == 'fincomb':
                break
            acc = self.parse_comando()
            if acc:
                acciones.append(acc)
            else:
                break
        if self.peek() and self.peek().tipo_token == TipoToken.PALABRA_CLAVE and self.peek().texto_original.lower() == 'fincomb':
            self.advance()
        else:
            self._report_error("Se esperaba 'finComb' al final de Combate", self.peek())
        if not resultado_node:
            self._report_error("Combate requiere 'Resultado' antes de 'finComb'", self.peek())
        atributos = {"linea": inicio.numero_linea if inicio else None}
        nodo = asaNode("Combate", "InicioCombate", atributos)
        for a in acciones:
            nodo.agregar_hijo(a)
        if resultado_node:
            nodo.agregar_hijo(resultado_node)
        for e in extras:
            nodo.agregar_hijo(e)
        return nodo

    # Stub general para acciones de competencia (Partido, Carrera, Combate, Rutina)
    def parse_accion_stub(self) -> asaNode:
        inicio = self.advance()
        if not inicio:
            # Nothing to consume, return an error node
            self._report_error("AccionStub incompleta: token de inicio ausente", None)
            return asaNode("ErrorSintactico", "AccionStub", {"linea": None})
        hijos = []
        # Recolectar tokens hasta encontrar un terminador conocido o cierre de bloque
        terminadores = {"finact","fincarr","finruti","finprep"}
        while self.peek() and self.peek().texto_original.lower() not in terminadores:
            # detener si vemos resultado/empate ya manejado afuera (permitir parse_comando trate esos)
            if self.peek().texto_original.lower() in ("resultado","listares","empate"):
                break
            child = self.parse_comando()
            if child:
                hijos.append(child)
            else:
                break
        return asaNode("AccionStub", inicio.texto_original if inicio else "AccionStub", {"linea": inicio.numero_linea if inicio else None}, hijos)

    # Condicional
    def parse_condicional(self) -> asaNode:
        si_tok = self.expect(TipoToken.ESTRUCTURA_CONTROL_FLUJO, texto="si")
        condicion = self.parse_condicion_expresion()
        entonces_tok = self.expect(TipoToken.ESTRUCTURA_CONTROL_FLUJO, texto="entonces", mensaje="Falta 'entonces' en condicional")
        llave_ap = self.expect(TipoToken.SIMBOLO_PUNTUACION, texto="{", mensaje="Falta '{' de apertura en condicional")
        cuerpo = []
        while self.peek() and self.peek().texto_original.lower() not in ("}", "sino", "endif"):
            n = self.parse_comando()
            if n:
                cuerpo.append(n)
            else:
                break
        sino_bloque = None
        if self.peek() and self.peek().texto_original.lower() == "sino":
            self.advance()
            self.expect(TipoToken.SIMBOLO_PUNTUACION, texto="{", mensaje="Falta '{' después de 'sino'")
            sino_bloque = []
            while self.peek() and self.peek().texto_original.lower() not in ("}", "endif"):
                s = self.parse_comando()
                if s: sino_bloque.append(s)
                else: break
            self.expect(TipoToken.SIMBOLO_PUNTUACION, texto="}", mensaje="Falta '}' de cierre en bloque 'sino'")
        self.expect(TipoToken.SIMBOLO_PUNTUACION, texto="}", mensaje="Falta '}' de cierre en condicional principal")
        self.expect(TipoToken.ESTRUCTURA_CONTROL_FLUJO, texto="endif", mensaje="Falta 'endif' al final de condicional")
        nodo = asaNode("Condicional", "si", {"condicion": condicion.contenido, "linea": si_tok.numero_linea if si_tok else None})
        nodo.hijos = cuerpo
        if sino_bloque:
            nodo.agregar_hijo(asaNode("Sino","",{},sino_bloque))
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
        self.expect(TipoToken.SIMBOLO_PUNTUACION, texto="(", mensaje="Falta '(' en Repetir")
        count = self.expect(TipoToken.NUMERO_ENTERO, mensaje="Repetir requiere un número entero")
        self.expect(TipoToken.SIMBOLO_PUNTUACION, texto=")", mensaje="Falta ')' en Repetir")
        self.expect(TipoToken.SIMBOLO_PUNTUACION, texto="[", mensaje="Falta '[' en bloque Repetir")
        cuerpo = []
        while self.peek() and self.peek().texto_original.lower() not in ("finrep", "]"):
            n = self.parse_comando()
            if n: cuerpo.append(n)
            else: break
        self.expect(TipoToken.SIMBOLO_PUNTUACION, texto="]", mensaje="Falta ']' en Repetir")
        self.expect(TipoToken.ESTRUCTURA_CONTROL_FLUJO, texto="FinRep", mensaje="Falta 'FinRep' después del bloque Repetir")
        return asaNode("Repetir", count.texto_original if count else "", {}, cuerpo)

    def parse_repetir_hasta(self) -> asaNode:
        tok = self.expect(TipoToken.ESTRUCTURA_CONTROL_FLUJO, texto="RepetirHasta")
        self.expect(TipoToken.SIMBOLO_PUNTUACION, texto="(", mensaje="Falta '(' en RepetirHasta")
        condicion = self.parse_condicion_expresion()
        self.expect(TipoToken.SIMBOLO_PUNTUACION, texto=")", mensaje="Falta ')' en RepetirHasta")
        self.expect(TipoToken.SIMBOLO_PUNTUACION, texto="[", mensaje="Falta '[' en bloque RepetirHasta")
        cuerpo = []
        while self.peek() and self.peek().texto_original.lower() not in ("finrephast", "]"):
            n = self.parse_comando()
            if n: cuerpo.append(n)
            else: break
        self.expect(TipoToken.SIMBOLO_PUNTUACION, texto="]", mensaje="Falta ']' en RepetirHasta")
        self.expect(TipoToken.ESTRUCTURA_CONTROL_FLUJO, texto="FinRepHast", mensaje="Falta 'FinRepHast' en RepetirHasta")
        return asaNode("RepetirHasta", condicion.contenido, {}, cuerpo)

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
            # No hay token: reportar error y devolver nodo de error en lugar de lanzar
            self._report_error("Expresión incompleta: EOF", None)
            return asaNode("PrimaryUnknown", "", {"linea": None})
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
        if not tok:
            self._report_error("Token inesperado en expresión primaria", None)
            return asaNode("PrimaryUnknown", "", {"linea": None})
        return asaNode("PrimaryUnknown", tok.texto_original, {"linea": tok.numero_linea})

# Integración con explorador
def parse_from_tokens(tokens: List[TokenLexico]) -> asaNode:
    parser = Parser(tokens)
    raiz = parser.parse_program()
    # adjuntar errores sintácticos en atributos del root
    if isinstance(raiz.atributos, dict):
        raiz.atributos['parser_errors'] = parser.errors
    else:
        raiz.atributos = {'parser_errors': parser.errors}
    return raiz


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