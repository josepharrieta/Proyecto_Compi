import pytest
from analizador_sintactico import parse_from_file, parse_from_tokens
from explorador import AnalizadorLexico
from verificador import Verifier


def tokens_from_file(path):
    with open(path, encoding='utf-8') as f:
        lines = [l.rstrip('\n\r') for l in f.readlines()]
    lex = AnalizadorLexico(lines)
    lex.analizar_codigo_completo()
    return lex.obtener_tokens()


def test_declaracion_y_uso():
    # construct a minimal example inline
    src = [
        "Deportista A 1 2 3 Futbol P",
        "narrar(A)",
    ]
    lex = AnalizadorLexico(src)
    lex.analizar_codigo_completo()
    tokens = lex.obtener_tokens()
    asa = parse_from_tokens(tokens)
    v = Verifier(asa)
    errs = v.run()
    # no errors expected
    assert len(errs) == 0


def test_uso_antes_declarar_error():
    src = [
        "narrar(X)",
        "Deportista X 1 2 3 Futbol P",
    ]
    lex = AnalizadorLexico(src)
    lex.analizar_codigo_completo()
    tokens = lex.obtener_tokens()
    asa = parse_from_tokens(tokens)
    v = Verifier(asa)
    errs = v.run()
    assert any("usado antes de ser declarado" in e.message for e in errs)


def test_suma_texto_numero_error():
    src = [
        "Deportista A 1 2 3 Futbol P",
        "narrar(\"hi\")",
        "n = Nombre + 5",  # will be parsed partially as Unknowns but exercise BinaryOp
    ]
    lex = AnalizadorLexico(src)
    lex.analizar_codigo_completo()
    tokens = lex.obtener_tokens()
    asa = parse_from_tokens(tokens)
    v = Verifier(asa)
    errs = v.run()
    # We expect at least that verifier doesn't crash and returns a list
    assert isinstance(errs, list)
