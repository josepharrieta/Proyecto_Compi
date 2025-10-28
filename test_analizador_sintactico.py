import types
from explorador import TipoToken
from analizador_sintactico import parse_from_tokens

def tk(tipo, texto, linea=0, col=0):
    """Token ligero para pruebas (simula TokenLexico)."""
    t = types.SimpleNamespace()
    t.tipo_token = tipo
    t.texto_original = texto
    t.numero_linea = linea
    t.posicion_columna = col
    return t

def build_tokens_for_ejemplo():
    tokens = []
    linea = 1
    # Comentario inicial
    tokens.append(tk(TipoToken.COMENTARIO, "; Programa de gestion deportiva basico", linea)); linea += 1
    # Deportista atleta1 25 80 75 Futbol Argentina
    tokens += [
        tk(TipoToken.DECLARACION_ENTIDAD, "Deportista", linea),
        tk(TipoToken.NOMBRE_IDENTIFICADOR, "atleta1", linea),
        tk(TipoToken.NUMERO_ENTERO, "25", linea),
        tk(TipoToken.NUMERO_ENTERO, "80", linea),
        tk(TipoToken.NUMERO_ENTERO, "75", linea),
        tk(TipoToken.NOMBRE_IDENTIFICADOR, "Futbol", linea),
        tk(TipoToken.NOMBRE_IDENTIFICADOR, "Argentina", linea),
    ]; linea += 1
    # Deportista atleta2 ...
    tokens += [
        tk(TipoToken.DECLARACION_ENTIDAD, "Deportista", linea),
        tk(TipoToken.NOMBRE_IDENTIFICADOR, "atleta2", linea),
        tk(TipoToken.NUMERO_ENTERO, "28", linea),
        tk(TipoToken.NUMERO_ENTERO, "85", linea),
        tk(TipoToken.NUMERO_ENTERO, "78", linea),
        tk(TipoToken.NOMBRE_IDENTIFICADOR, "Basquet", linea),
        tk(TipoToken.NOMBRE_IDENTIFICADOR, "Brasil", linea),
    ]; linea += 1
    # Lista Deportista competidores
    tokens += [
        tk(TipoToken.DECLARACION_ENTIDAD, "Lista", linea),
        tk(TipoToken.DECLARACION_ENTIDAD, "Deportista", linea),
        tk(TipoToken.NOMBRE_IDENTIFICADOR, "competidores", linea),
    ]; linea += 1
    # si Comparar(atleta1, atleta2) > 0 entonces { narrar(atleta1) } sino { narrar(atleta2) } endif
    tokens += [
        tk(TipoToken.ESTRUCTURA_CONTROL_FLUJO, "si", linea),
        tk(TipoToken.INVOCACION_FUNCION, "Comparar(", linea),
        tk(TipoToken.NOMBRE_IDENTIFICADOR, "atleta1", linea),
        tk(TipoToken.SIMBOLO_PUNTUACION, ",", linea),
        tk(TipoToken.NOMBRE_IDENTIFICADOR, "atleta2", linea),
        tk(TipoToken.SIMBOLO_PUNTUACION, ")", linea),
        tk(TipoToken.OPERADOR_COMPARACION, ">", linea),
        tk(TipoToken.NUMERO_ENTERO, "0", linea),
        tk(TipoToken.ESTRUCTURA_CONTROL_FLUJO, "entonces", linea),
        tk(TipoToken.SIMBOLO_PUNTUACION, "{", linea),
        tk(TipoToken.INVOCACION_FUNCION, "narrar(", linea+1),
        tk(TipoToken.NOMBRE_IDENTIFICADOR, "atleta1", linea+1),
        tk(TipoToken.SIMBOLO_PUNTUACION, ")", linea+1),
        tk(TipoToken.SIMBOLO_PUNTUACION, "}", linea+1),
        tk(TipoToken.ESTRUCTURA_CONTROL_FLUJO, "sino", linea+1),
        tk(TipoToken.SIMBOLO_PUNTUACION, "{", linea+1),
        tk(TipoToken.INVOCACION_FUNCION, "narrar(", linea+2),
        tk(TipoToken.NOMBRE_IDENTIFICADOR, "atleta2", linea+2),
        tk(TipoToken.SIMBOLO_PUNTUACION, ")", linea+2),
        tk(TipoToken.SIMBOLO_PUNTUACION, "}", linea+2),
        tk(TipoToken.ESTRUCTURA_CONTROL_FLUJO, "endif", linea+2),
    ]; linea += 3
    # Repetir(3) [ input(entrenamiento) narrar(progreso) ] FinRep
    tokens += [
        tk(TipoToken.ESTRUCTURA_CONTROL_FLUJO, "Repetir", linea),
        tk(TipoToken.SIMBOLO_PUNTUACION, "(", linea),
        tk(TipoToken.NUMERO_ENTERO, "3", linea),
        tk(TipoToken.SIMBOLO_PUNTUACION, ")", linea),
        tk(TipoToken.SIMBOLO_PUNTUACION, "[", linea),
        tk(TipoToken.INVOCACION_FUNCION, "input(", linea+1),
        tk(TipoToken.NOMBRE_IDENTIFICADOR, "entrenamiento", linea+1),
        tk(TipoToken.SIMBOLO_PUNTUACION, ")", linea+1),
        tk(TipoToken.INVOCACION_FUNCION, "narrar(", linea+1),
        tk(TipoToken.NOMBRE_IDENTIFICADOR, "progreso", linea+1),
        tk(TipoToken.SIMBOLO_PUNTUACION, ")", linea+1),
        tk(TipoToken.SIMBOLO_PUNTUACION, "]", linea+2),
        tk(TipoToken.ESTRUCTURA_CONTROL_FLUJO, "FinRep", linea+2),
    ]
    return tokens

def test_parse_ejemplo_structure():
    tokens = build_tokens_for_ejemplo()
    ast = parse_from_tokens(tokens)
    # Root should be Programa
    assert ast.tipo == "Programa"
    # Check presence and order of some top-level node types
    tipos = [n.tipo for n in ast.hijos]
    assert "Comentario" in tipos
    assert "Deportista" in tipos
    assert "Lista" in tipos or "CargaDeportistas" in tipos
    # find a Deportista node and check its attributes
    deportistas = [n for n in ast.hijos if n.tipo == "Deportista"]
    assert len(deportistas) >= 2
    first = deportistas[0]
    assert first.contenido == "atleta1"
    assert first.atributos["estadisticas"] == ["25", "80", "75"]

def test_preorder_output_contains_narrar_and_repetir():
    tokens = build_tokens_for_ejemplo()
    ast = parse_from_tokens(tokens)
    lines = list(ast.preorder_lines())
    # Should contain Narrar nodes and Repetir node text
    assert any(' "Narrar",' in l or '<"Narrar",' in l or '<"Narrar"' in l for l in lines)
    assert any(' "Repetir",' in l or '<"Repetir",' in l or '<"Repetir"' in l for l in lines)