"""
Lector de Archivos Olympiac
============================

Este módulo lee archivos con código Olympiac (.oly) y los procesa usando
el analizador léxico.

Autores: [Kevin Núñez, Axel López, Felipe Murillo, Joseph Arrieta, Arturo Chavarría]
Fecha: Octubre 2025
Versión: 1.0

Dependencias:
- explorador: Módulo del analizador léxico
"""

import os
from explorador import AnalizadorLexico


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


def procesar_archivo(ruta_archivo):
    """
    Lee un archivo Olympiac y retorna los tokens encontrados por el analizador.
    
    Entradas:
        ruta_archivo (str): Ruta al archivo .oly a procesar
        
    Salida:
        list: Lista de tokens (objetos TokenLexico) encontrados por el explorador
    """
    # Leer el archivo
    lineas_codigo = leer_archivo_olympiac(ruta_archivo)
    
    # Crear analizador y procesar
    analizador = AnalizadorLexico(lineas_codigo)
    analizador.analizar_codigo_completo()
    
    # Retornar solo los tokens
    return analizador.obtener_tokens()


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
    
    # Crear analizador y procesar
    analizador = AnalizadorLexico(lineas_codigo)
    analizador.analizar_codigo_completo()
    
    # Retornar tokens como diccionarios
    return analizador.obtener_tokens_como_diccionarios()


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
    
    # Crear analizador y procesar
    analizador = AnalizadorLexico(lineas_codigo)
    analizador.analizar_codigo_completo()
    
    # Retornar tokens como tuplas
    return analizador.obtener_tokens_como_tuplas()


def main():
    """
    Función principal de demostración.
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
    
    print("=" * 60)
    print(f"PROCESANDO: {ruta}")
    print("=" * 60)
    
    try:
        # Procesar y obtener tokens
        tokens = procesar_archivo(ruta)
        
        # Mostrar tokens
        print(f"\nTotal de tokens encontrados: {len(tokens)}\n")
        for token in tokens:
            print(token)
        
        print("\n" + "=" * 60)
        print("PROCESO COMPLETADO")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
