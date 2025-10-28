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
from explorador import AnalizadorLexico
from analizador_sintactico import parse_from_tokens


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
    
    # Preparar resultado completo
    resultado = {
        'asa': asa,
        'tokens': tokens,
        'errores_lexicos': analizador_lexico.obtener_errores(),
        'cantidad_errores': analizador_lexico.contador_errores_lexicos,
        'resumen': analizador_lexico.obtener_resumen()
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
    """
    import sys
    
    if len(sys.argv) > 1:
        ruta = sys.argv[1]
    else:
        # Buscar primer archivo .oly en el directorio
        archivos = [f for f in os.listdir('.') if f.endswith('.oly')]
        if archivos:
            ruta = archivos[0]
            print(f"Usando archivo encontrado: {ruta}")
        else:
            print("No se encontraron archivos .oly")
            print("Uso: python lector_olympiac.py archivo.oly")
            return
    
    print("=" * 80)
    print(f"LECTOR OLYMPIAC - PROCESAMIENTO COMPLETO")
    print("=" * 80)
    print(f"Archivo: {ruta}\n")
    
    try:
        # PASO 1: Leer archivo
        print("[PASO 1] Leyendo archivo...")
        lineas_codigo = leer_archivo_olympiac(ruta)
        print(f"   ✓ {len(lineas_codigo)} líneas leídas\n")
        
        # PASO 2: Enviar al explorador (analizador léxico)
        print("[PASO 2] Enviando código al explorador (analizador léxico)...")
        tokens, analizador = enviar_a_explorador(lineas_codigo)
        print(f"   ✓ {len(tokens)} tokens recibidos del explorador")
        if analizador.contador_errores_lexicos > 0:
            print(f"   ⚠ {analizador.contador_errores_lexicos} errores léxicos detectados")
        print()
        
        # Mostrar algunos tokens
        print("   Primeros tokens encontrados:")
        for i, token in enumerate(tokens[:10]):
            print(f"      {token}")
        if len(tokens) > 10:
            print(f"      ... y {len(tokens) - 10} tokens más")
        print()
        
        # PASO 3: Enviar tokens al analizador sintáctico
        print("[PASO 3] Enviando tokens al analizador sintáctico...")
        asa = enviar_a_analizador_sintactico(tokens)
        print(f"   ✓ asa generado exitosamente\n")
        
        # Mostrar asa
        print("[RESULTADO] Árbol de Sintaxis Abstracta (asa):")
        print("-" * 80)
        for linea in asa.preorder_lines():
            print(linea)
        
        print("\n" + "=" * 80)
        print("PROCESAMIENTO COMPLETADO EXITOSAMENTE")
        print("=" * 80)
        print(f"Líneas procesadas: {len(lineas_codigo)}")
        print(f"Tokens generados: {len(tokens)}")
        print(f"Errores léxicos: {analizador.contador_errores_lexicos}")
        print(f"asa nodos raíz: {asa.tipo}")
        print("=" * 80)
        
    except FileNotFoundError as e:
        print(f"\n ERROR: {e}")
    except Exception as e:
        print(f"\n ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
