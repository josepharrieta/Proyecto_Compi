"""
Lector de Archivos Olympiac
============================

Este módulo coordina el flujo completo de análisis de archivos Olympiac:
1. Lee archivos .oly
2. Envía el contenido al explorador (analizador léxico)
3. Recibe los tokens del explorador
4. Envía los tokens al analizador sintáctico
5. Retorna el asa generado

Autores: [Kevin Núñez, Axel López, Felipe Murillo, Joseph Arrieta, Arturo Chavarría]
Fecha: Octubre 2025
Versión: 2.0

Dependencias:
- explorador: Módulo del analizador léxico
- analizador_sintactico: Módulo del analizador sintáctico
"""

import os
import sys
import json
from explorador import AnalizadorLexico
from analizador_sintactico import parse_from_tokens, asaNode
try:
    from verificador import Verifier
except Exception:
    Verifier = None
try:
    from generador import construir_codigo
except Exception:
    construir_codigo = None


def leer_archivo_olympiac(ruta_archivo):
    """
    Lee un archivo de código Olympiac y retorna sus líneas como lista de strings.
    
    Entradas:
        ruta_archivo (str): Ruta completa o relativa al archivo .oly
        
    Salida:
        list: Lista de strings, cada uno representando una línea del archivo
        
    Excepciones:
        FileNotFoundError: Si el archivo no existe
        Exception: Si hay error al leer el archivo
    """
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"El archivo no existe: {ruta_archivo}")
    
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            lineas = archivo.readlines()
        
        # Remover el salto de línea de cada línea
        lineas_limpias = [linea.rstrip('\n\r') for linea in lineas]
        
        return lineas_limpias
    
    except Exception as e:
        raise Exception(f"Error al leer el archivo {ruta_archivo}: {str(e)}")


def enviar_a_explorador(lineas_codigo):
    """
    Envía las líneas de código al explorador (analizador léxico) para obtener tokens.
    
    Entradas:
        lineas_codigo (list): Lista de líneas de código a analizar
        
    Salida:
        tuple: (tokens, analizador) - Lista de tokens y objeto analizador para acceso a errores
    """
    # Crear analizador léxico
    analizador = AnalizadorLexico(lineas_codigo)
    
    # Analizar código completo
    analizador.analizar_codigo_completo()
    
    # Obtener tokens (sin espacios en blanco)
    tokens = analizador.obtener_tokens(incluir_espacios=False)
    
    return tokens, analizador


def enviar_a_analizador_sintactico(tokens):
    """
    Envía los tokens al analizador sintáctico para construir el ASA.
    
    Entradas:
        tokens (list): Lista de tokens léxicos
        
    Salida:
        asaNode: Árbol de sintaxis abstracta (ASA) generado
    """
    # Parsear tokens y construir ASA
    asa = parse_from_tokens(tokens)
    parser_errors = []
    if hasattr(asa, 'atributos'):  # no cambia
        pass
    # obtener errores si parse_from_tokens retorna parser con errores (ajuste)
    # Cambiar parse_from_tokens para devolver parser? (Simplificación: inspeccionar luego)
    # Añadir extracción después de parseo si se expone Parser.errors
    
    return asa


def procesar_archivo_completo(ruta_archivo):
    """
    FUNCIÓN PRINCIPAL: Procesa un archivo Olympiac completo.
    
    Flujo:
    1. Lee el archivo .oly
    2. Envía líneas al explorador
    3. Recibe tokens del explorador
    4. Envía tokens al analizador sintáctico
    5. Retorna el asa
    
    Entradas:
        ruta_archivo (str): Ruta al archivo .oly a procesar
        
    Salida:
        dict: Diccionario con 'asa', 'tokens', 'errores_lexicos', 'resumen'
    """
    # Paso 1: Leer archivo
    lineas_codigo = leer_archivo_olympiac(ruta_archivo)
    
    # Paso 2 y 3: Enviar al explorador y recibir tokens
    tokens, analizador_lexico = enviar_a_explorador(lineas_codigo)
    
    # Paso 4: Enviar tokens al analizador sintáctico
    asa = enviar_a_analizador_sintactico(tokens)
    # ejecutar verificador (si está disponible)
    sem_result = None
    if Verifier:
        try:
            verifier = Verifier(asa)
            errores_sem = verifier.run()
            # captura una versión impresa del asa decorado (simple)
            import io
            buf = io.StringIO()
            # imprimir decorado a buffer
            # reusar método print_decorated but redirect stdout
            verifier.print_decorated()
            sem_result = {
                'errores': [ { 'mensaje': e.message, 'linea': e.line, 'col': e.column } for e in errores_sem ],
                'tabla_snapshot': verifier.table.snapshot(),
                'decorations_json': os.path.join(os.getcwd(), 'asa_decorated.json')
            }
        except Exception:
            sem_result = { 'errores': [ {'mensaje': 'Error interno en verificador'} ], 'tabla_snapshot': {} }

    # Preparar resultado completo
    resultado = {
        'asa': asa,
        'tokens': tokens,
        'errores_lexicos': analizador_lexico.obtener_errores(),
        'cantidad_errores': analizador_lexico.contador_errores_lexicos,
        'resumen': analizador_lexico.obtener_resumen(),
        'semantica': sem_result
    }
    
    return resultado


def procesar_archivo(ruta_archivo):
    """
    Lee un archivo Olympiac y retorna los tokens encontrados por el explorador.
    (Función legacy - mantiene compatibilidad)
    
    Entradas:
        ruta_archivo (str): Ruta al archivo .oly a procesar
        
    Salida:
        list: Lista de tokens (objetos TokenLexico) encontrados por el explorador
    """
    # Leer el archivo
    lineas_codigo = leer_archivo_olympiac(ruta_archivo)
    
    # Enviar al explorador y obtener tokens
    tokens, _ = enviar_a_explorador(lineas_codigo)
    
    return tokens


def procesar_archivo_dict(ruta_archivo):
    """
    Lee un archivo Olympiac y retorna los tokens como diccionarios.
    
    Entradas:
        ruta_archivo (str): Ruta al archivo .oly a procesar
        
    Salida:
        list: Lista de diccionarios con información de cada token
    """
    # Leer el archivo
    lineas_codigo = leer_archivo_olympiac(ruta_archivo)
    
    # Enviar al explorador
    tokens, _ = enviar_a_explorador(lineas_codigo)
    
    # Convertir a diccionarios
    return [token.to_dict() for token in tokens]


def procesar_archivo_tuplas(ruta_archivo):
    """
    Lee un archivo Olympiac y retorna los tokens como tuplas.
    
    Entradas:
        ruta_archivo (str): Ruta al archivo .oly a procesar
        
    Salida:
        list: Lista de tuplas (tipo, texto, info, linea, columna)
    """
    # Leer el archivo
    lineas_codigo = leer_archivo_olympiac(ruta_archivo)
    
    # Enviar al explorador
    tokens, _ = enviar_a_explorador(lineas_codigo)
    
    # Convertir a tuplas
    return [token.to_tuple() for token in tokens]


def main():
    """
    Función principal de demostración del flujo completo.
    
    Uso:
        python lector_olympiac.py archivo.oly                    # Análisis completo
        python lector_olympiac.py archivo.oly -g salida.py       # Generar código Python
        python lector_olympiac.py archivo.oly --generate output.py
    """
    # Parsear argumentos
    generar = False
    salida_gen = None
    ruta = None
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ('-g', '--generate'):
            generar = True
            if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith('-'):
                salida_gen = sys.argv[i + 1]
                i += 1
        elif not arg.startswith('-'):
            ruta = arg
        i += 1
    
    if not ruta:
        # Buscar primer archivo .oly en el directorio
        archivos = [f for f in os.listdir('.') if f.endswith('.oly')]
        if archivos:
            ruta = archivos[0]
            print(f"Usando archivo encontrado: {ruta}")
        else:
            print("No se encontraron archivos .oly")
            print("Uso: python lector_olympiac.py archivo.oly")
            print("      python lector_olympiac.py archivo.oly -g salida.py")
            return
    
    print("=" * 80)
    print(f"LECTOR OLYMPIAC - PROCESAMIENTO COMPLETO")
    print("=" * 80)
    print(f"Archivo: {ruta}\n")
    
    try:
        # PASO 1: Leer archivo
        print("[PASO 1] Leyendo archivo...")
        lineas_codigo = leer_archivo_olympiac(ruta)
        print(f"     {len(lineas_codigo)} líneas leídas\n")
        
        # PASO 2: Enviar al explorador (analizador léxico)
        print("[PASO 2] Enviando código al explorador (analizador léxico)...")
        tokens, analizador = enviar_a_explorador(lineas_codigo)
        print(f"   {len(tokens)} tokens recibidos del explorador")
        
        # Mostrar errores léxicos SI EXISTEN
        if analizador.contador_errores_lexicos > 0:
            print(f"\n[ERRORES LÉXICOS] Se detectaron {analizador.contador_errores_lexicos} errores:")
            for err in analizador.obtener_errores():
                print(f"   - Línea {err['linea']} Col {err['columna']}: {err['tipo']} {err['caracter']}")
        else:
            print(f"    Sin errores léxicos")
        print()
        
        # Mostrar algunos tokens (opcional, más limpio)
        print("   Primeros 10 tokens:")
        for i, token in enumerate(tokens[:10]):
            print(f"      {token}")
        if len(tokens) > 10:
            print(f"      ... y {len(tokens) - 10} tokens más")
        print()
        
        # PASO 3: Enviar tokens al analizador sintáctico
        print("[PASO 3] Enviando tokens al analizador sintáctico...")
        asa = enviar_a_analizador_sintactico(tokens)
        
        # Mostrar errores sintácticos
        parser_errs = []
        if isinstance(asa.atributos, dict) and 'parser_errors' in asa.atributos:
            parser_errs = asa.atributos.get('parser_errors', [])
            if parser_errs:
                print(f"\n[ERRORES SINTÁCTICOS] Se detectaron {len(parser_errs)} errores:")
                for e in parser_errs:
                    linea = e.get('linea')
                    col = e.get('columna')
                    msg = e.get('mensaje')
                    print(f"   - Línea {linea} Col {col}: {msg}")
                print()  # línea en blanco después de errores
            else:
                print(f"    Sin errores sintácticos")
        
        print(f"    ASA generado exitosamente\n")

        # Si se solicita generación, hacer eso y terminar
        if generar:
            if construir_codigo:
                print("[PASO 4 (GENERACIÓN)] Generando código Python...")
                codigo_python = construir_codigo(asa)
                salida_final = salida_gen or 'salida.py'
                with open(salida_final, 'w', encoding='utf-8') as f:
                    f.write(codigo_python)
                print(f"Código generado en: {salida_final}")
                print(f"   Para ejecutar: python {salida_final}\n")
            else:
                print("Generador no disponible\n")
            return
        
        # ============================================================
        # PASO 4: VERIFICADOR SEMÁNTICO (ANÁLISIS PRINCIPAL)
        # ============================================================
        print("=" * 80)
        print("[PASO 4] ANÁLISIS SEMÁNTICO")
        print("=" * 80)
        
        if Verifier:
            try:
                print("\nEjecutando verificador semántico...\n")
                verifier = Verifier(asa)
                errores_sem = verifier.run()
                
                # ======== MOSTRAR ASA DECORADO ========
                print("-" * 80)
                print("ASA DECORADO (con anotaciones semánticas):")
                print("-" * 80)
                def imprimir_decorado(n: asaNode, nivel: int = 0):
                    indent = '  ' * nivel
                    print(f"{indent}<\"{n.tipo}\", \"{n.contenido}\", {n.atributos}>")
                    dec = verifier.decorations.get(id(n))
                    if dec:
                        print(f"{indent}  Decorado: {dec}")
                    for h in n.hijos:
                        imprimir_decorado(h, nivel + 1)
                
                imprimir_decorado(asa)
                print()
                
                # ======== MOSTRAR ERRORES SEMÁNTICOS ========
                if errores_sem:
                    print("-" * 80)
                    print(f"ERRORES SEMÁNTICOS DETECTADOS ({len(errores_sem)}):")
                    print("-" * 80)
                    for e in errores_sem:
                        print(f"  {e}")
                    print()
                else:
                    print("-" * 80)
                    print("Sin errores semánticos detectados.")
                    print("-" * 80)
                    print()
                
                # ======== MOSTRAR TABLA DE SÍMBOLOS ========
                print("-" * 80)
                print("TABLA DE SÍMBOLOS (snapshot final):")
                print("-" * 80)
                print(verifier.table)
                print()
                
                # ======== EXPORTAR A JSON ========
                ruta_json = os.path.join(os.getcwd(), 'asa_decorated.json')
                decorations_export = {
                    'decorations': {str(k): v for k, v in verifier.decorations.items()},
                    'errors': [{'mensaje': e.message, 'linea': e.line, 'columna': e.column, 'severidad': e.severity} for e in errores_sem],
                    'snapshots': verifier.snapshots
                }
                with open(ruta_json, 'w', encoding='utf-8') as f:
                    json.dump(decorations_export, f, ensure_ascii=False, indent=2)
                print(f"Decoraciones exportadas a: {ruta_json}\n")
                
            except Exception as ex:
                print(f"Error al ejecutar el verificador: {ex}")
                import traceback
                traceback.print_exc()
        else:
            print("⚠ Verificador semántico no disponible (módulo no cargado)\n")
        
        # ============================================================
        # RESUMEN FINAL
        # ============================================================
        print("=" * 80)
        print("PROCESAMIENTO COMPLETADO")
        print("=" * 80)
        print(f"Líneas procesadas: {len(lineas_codigo)}")
        print(f"Tokens generados: {len(tokens)}")
        print(f"Errores léxicos: {analizador.contador_errores_lexicos}")
        print(f"Errores sintácticos: {len(parser_errs)}")
        if Verifier and 'errores_sem' in locals():
            print(f"Errores semánticos: {len(errores_sem)}")
        print(f"ASA nodos raíz: {asa.tipo}")
        print("=" * 80)
        
    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
