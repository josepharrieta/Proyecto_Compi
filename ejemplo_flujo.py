"""
Ejemplo de uso del flujo completo del Lector Olympiac
======================================================

Este script demuestra cómo usar el lector para procesar archivos .oly
siguiendo el flujo:
  Lector → Explorador → Analizador Sintáctico

Autores: [Kevin Núñez, Axel López, Felipe Murillo, Joseph Arrieta, Arturo Chavarría]
Fecha: Octubre 2025
"""

from lector_olympiac import (
    leer_archivo_olympiac,
    enviar_a_explorador,
    enviar_a_analizador_sintactico,
    procesar_archivo_completo
)


def ejemplo_flujo_paso_a_paso():
    """
    Demuestra el flujo completo paso a paso.
    """
    print("=" * 80)
    print("EJEMPLO: FLUJO PASO A PASO")
    print("=" * 80)
    
    archivo = "ejemplo1.oly"
    
    # PASO 1: Lector lee el archivo
    print("\n[PASO 1] LECTOR: Lee el archivo .oly")
    print("-" * 80)
    lineas = leer_archivo_olympiac(archivo)
    print(f"Archivo leído: {archivo}")
    print(f"Líneas cargadas: {len(lineas)}")
    print(f"Primera línea: {lineas[0]}")
    
    # PASO 2: Lector envía al Explorador (Analizador Léxico)
    print("\n[PASO 2] LECTOR → EXPLORADOR: Envía líneas al analizador léxico")
    print("-" * 80)
    tokens, analizador = enviar_a_explorador(lineas)
    print(f"Tokens recibidos del explorador: {len(tokens)}")
    print(f"Errores léxicos detectados: {analizador.contador_errores_lexicos}")
    print(f"\nPrimeros 5 tokens:")
    for i, token in enumerate(tokens[:5], 1):
        print(f"  {i}. {token.tipo_token.name}: '{token.texto_original}'")
    
    # PASO 3: Lector envía tokens al Analizador Sintáctico
    print("\n[PASO 3] LECTOR → ANALIZADOR SINTÁCTICO: Envía tokens para generar AST")
    print("-" * 80)
    ast = enviar_a_analizador_sintactico(tokens)
    print(f"AST generado con éxito")
    print(f"Nodo raíz: {ast.tipo}")
    print(f"Número de hijos directos: {len(ast.hijos)}")
    
    print("\n[RESULTADO] AST Completo:")
    print("-" * 80)
    for linea in ast.preorder_lines():
        print(linea)
    
    print("\n" + "=" * 80)
    print("FLUJO COMPLETADO")
    print("=" * 80)


def ejemplo_flujo_automatico():
    """
    Demuestra el uso de la función que procesa todo automáticamente.
    """
    print("\n\n")
    print("=" * 80)
    print("EJEMPLO: FLUJO AUTOMÁTICO (FUNCIÓN INTEGRADA)")
    print("=" * 80)
    
    archivo = "ejemplo1.oly"
    
    print(f"\nProcesando archivo: {archivo}")
    print("La función procesar_archivo_completo() ejecuta todos los pasos automáticamente")
    
    # Procesar todo de una vez
    resultado = procesar_archivo_completo(archivo)
    
    print("\n[RESULTADO COMPLETO]")
    print("-" * 80)
    print(f"AST generado: {resultado['ast'].tipo}")
    print(f"Total de tokens: {len(resultado['tokens'])}")
    print(f"Errores léxicos: {resultado['cantidad_errores']}")
    
    print("\n[RESUMEN DEL ANÁLISIS]")
    print("-" * 80)
    resumen = resultado['resumen']
    print(f"Total líneas: {resumen['total_lineas']}")
    print(f"Total tokens: {resumen['total_tokens']}")
    print(f"¿Tiene errores?: {resumen['tiene_errores']}")
    
    print("\n[DISTRIBUCIÓN DE TOKENS POR TIPO]")
    print("-" * 80)
    for tipo, cantidad in sorted(resumen['tokens_por_tipo'].items()):
        print(f"  {tipo}: {cantidad}")
    
    print("\n" + "=" * 80)
    print("PROCESAMIENTO AUTOMÁTICO COMPLETADO")
    print("=" * 80)


def ejemplo_acceso_a_componentes():
    """
    Demuestra cómo acceder a diferentes componentes del resultado.
    """
    print("\n\n")
    print("=" * 80)
    print("EJEMPLO: ACCESO A COMPONENTES INDIVIDUALES")
    print("=" * 80)
    
    archivo = "ejemplo1.oly"
    resultado = procesar_archivo_completo(archivo)
    
    # Acceder al AST
    print("\n[1] Acceso al AST:")
    print("-" * 80)
    ast = resultado['ast']
    print(f"Tipo de nodo raíz: {ast.tipo}")
    print(f"Contenido: {ast.contenido}")
    print(f"Número de hijos: {len(ast.hijos)}")
    
    # Acceder a los tokens
    print("\n[2] Acceso a los Tokens:")
    print("-" * 80)
    tokens = resultado['tokens']
    print(f"Total de tokens: {len(tokens)}")
    print("Tipos de tokens únicos:")
    tipos_unicos = set(t.tipo_token.name for t in tokens)
    for tipo in sorted(tipos_unicos):
        print(f"  - {tipo}")
    
    # Acceder a errores
    print("\n[3] Acceso a Errores Léxicos:")
    print("-" * 80)
    errores = resultado['errores_lexicos']
    if errores:
        print(f"Se encontraron {len(errores)} errores:")
        for error in errores:
            print(f"  Línea {error['linea']}, Col {error['columna']}: {error['tipo']}")
    else:
        print("No se encontraron errores léxicos ✓")
    
    # Acceder al resumen
    print("\n[4] Acceso al Resumen:")
    print("-" * 80)
    resumen = resultado['resumen']
    print(f"Líneas analizadas: {resumen['total_lineas']}")
    print(f"Tokens procesados: {resumen['total_tokens']}")
    print(f"Estado: {'CON ERRORES' if resumen['tiene_errores'] else 'EXITOSO'}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    # Ejecutar todos los ejemplos
    ejemplo_flujo_paso_a_paso()
    ejemplo_flujo_automatico()
    ejemplo_acceso_a_componentes()
    
    print("\n\n")
    print("*" * 80)
    print("TODOS LOS EJEMPLOS EJECUTADOS CORRECTAMENTE")
    print("*" * 80)
    print("\nFLUJO DEL SISTEMA:")
    print("  1. LECTOR lee archivo .oly")
    print("  2. LECTOR envía líneas → EXPLORADOR")
    print("  3. EXPLORADOR analiza y retorna tokens → LECTOR")
    print("  4. LECTOR envía tokens → ANALIZADOR SINTÁCTICO")
    print("  5. ANALIZADOR SINTÁCTICO genera AST → LECTOR")
    print("  6. LECTOR retorna resultado completo")
    print("*" * 80)
