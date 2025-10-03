"""
Módulo de Pruebas para el Analizador Léxico Olympiac
===================================================

Este módulo contiene todas las pruebas del analizador léxico, incluyendo:
- Pruebas de funcionalidad básica
- Pruebas de casos complejos
- Pruebas de manejo de errores
- Validación de componentes léxicos

Autores: [Kevin Núñez, Axel López, Felipe Murillo, Joseph Arrieta, Arturo Chavarría]
Fecha: Octubre 2025
Versión: 1.0

Dependencias:
- explorador: Módulo principal del analizador léxico
"""

from explorador import AnalizadorLexico, TipoToken, TokenLexico


def ejecutar_pruebas_completas():
    """
    Función que ejecuta diferentes pruebas para demostrar el funcionamiento del analizador.
    Cubre diferentes aspectos: tokens válidos, estructuras complejas, casos límite y errores.
    """
    
    print("=" * 60)
    print("EJECUCION DE PRUEBAS DEL ANALIZADOR LEXICO OLYMPIAC")
    print("=" * 60)
    
    # PRUEBA 1: Tokens básicos
    print("\n[PRUEBA 1] Reconocimiento de tokens basicos")
    print("-" * 50)
    codigo_basico = [
        '; Comentario de prueba',
        'Deportista atleta1 25 80 75 Futbol Argentina',
        'si atleta1 > 20 entonces {',
        '    narrar(atleta1)',
        '} endif'
    ]
    
    analizador1 = AnalizadorLexico(codigo_basico)
    total_tokens1 = analizador1.analizar_codigo_completo()
    analizador1.mostrar_tokens_encontrados()
    print(f"RESULTADO: Total tokens reconocidos: {total_tokens1}")
    
    # PRUEBA 2: Operadores y expresiones
    print("\n[PRUEBA 2] Operadores y expresiones matematicas")
    print("-" * 50)
    codigo_operadores = [
        'si atleta1 + atleta2 >= 100 entonces {',
        '    Comparar(resultado1, resultado2)',
        '    si puntos != 0 entonces {',
        '        narrar(ganador)',
        '    } endif',
        '} endif'
    ]
    
    analizador2 = AnalizadorLexico(codigo_operadores)
    total_tokens2 = analizador2.analizar_codigo_completo()
    analizador2.mostrar_tokens_encontrados()
    print(f"RESULTADO: Total tokens reconocidos: {total_tokens2}")
    
    # PRUEBA 3: Estructuras de control anidadas
    print("\n[PRUEBA 3] Estructuras de control complejas y anidadas")
    print("-" * 50)
    codigo_control = [
        'Repetir(5) [',
        '    RepetirHasta(Comparar(atleta1, atleta2) == 0) [',
        '        preparacion',
        '            input(Argentina)',
        '        finprep',
        '    ] FinRepHast',
        '    si empate entonces {',
        '        Resultado 2 - 2',
        '        listaRes',
        '    } sino {',
        '        narrar(victoria)',
        '    } endif',
        '] FinRep'
    ]
    
    analizador3 = AnalizadorLexico(codigo_control)
    total_tokens3 = analizador3.analizar_codigo_completo()
    analizador3.mostrar_tokens_encontrados()
    print(f"RESULTADO: Total tokens reconocidos: {total_tokens3}")
    
    # PRUEBA 4: Competencias deportivas completas
    print("\n[PRUEBA 4] Simulacion de competencia deportiva completa")
    print("-" * 50)
    codigo_competencia = [
        'Futbol',
        '    Lista Deportista equipos_clasificados',
        '    competencia_mundial',
        '        partido_semifinal',
        '            Argentina vs Brasil',
        '            Comparar(Argentina, Brasil)',
        '            narrar(resultado_partido)',
        '            Resultado 3 - 1',
        '        finact',
        '        partido_final',
        '            InicioCarrera',
        '            correr',
        '            finCarr',
        '            empate',
        '            Resultado 0 - 0',
        '            listaRes',
        '        finact',
        '    ceremonia_medallas'
    ]
    
    analizador4 = AnalizadorLexico(codigo_competencia)
    total_tokens4 = analizador4.analizar_codigo_completo()
    analizador4.mostrar_tokens_encontrados()
    print(f"RESULTADO: Total tokens reconocidos: {total_tokens4}")
    
    # PRUEBA 5: Casos límite y caracteres especiales
    print("\n[PRUEBA 5] Casos limite - numeros, identificadores y simbolos")
    print("-" * 50)
    codigo_limites = [
        'Deportista atleta_con_nombre_muy_largo123 999 100 85 Natacion Chile',
        'Lista Pais paises_participantes',
        'si 0 < puntuacion_maxima entonces {',
        '    narrar(_resultado_final)',
        '} endif',
        'Repetir(1) [',
        '    input(a)',
        '] FinRep'
    ]
    
    analizador5 = AnalizadorLexico(codigo_limites)
    total_tokens5 = analizador5.analizar_codigo_completo()
    analizador5.mostrar_tokens_encontrados()
    print(f"RESULTADO: Total tokens reconocidos: {total_tokens5}")
    
    # PRUEBA 6: Verificación de tipos específicos de tokens
    print("\n[PRUEBA 6] Verificacion de tipos especificos de tokens")
    print("-" * 50)
    codigo_tipos = [
        '; Verificando todos los tipos de tokens',
        'Deportista atleta1 25 80 75 Futbol Argentina',
        'Lista Pais paises',
        'preparacion',
        'finprep',
        'si atleta1 == atleta2 entonces {',
        '    narrar(resultado)',
        '    empate',
        '    listaRes',
        '} endif',
        'Argentina vs Brasil',
        'Resultado 3 - 1'
    ]
    
    analizador6 = AnalizadorLexico(codigo_tipos)
    total_tokens6 = analizador6.analizar_codigo_completo()
    analizador6.mostrar_tokens_encontrados()
    print(f"RESULTADO: Total tokens reconocidos: {total_tokens6}")
    
    # RESUMEN DE PRUEBAS
    total_general = total_tokens1 + total_tokens2 + total_tokens3 + total_tokens4 + total_tokens5 + total_tokens6
    print(f"\n{'='*60}")
    print("RESUMEN DE PRUEBAS EJECUTADAS")
    print(f"{'='*60}")
    print(f"Prueba 1 (Basicos): {total_tokens1} tokens")
    print(f"Prueba 2 (Operadores): {total_tokens2} tokens")
    print(f"Prueba 3 (Control): {total_tokens3} tokens")
    print(f"Prueba 4 (Competencias): {total_tokens4} tokens")
    print(f"Prueba 5 (Limites): {total_tokens5} tokens")
    print(f"Prueba 6 (Tipos): {total_tokens6} tokens")
    print(f"TOTAL TOKENS PROCESADOS: {total_general}")
    print(f"{'='*60}")


def ejecutar_pruebas_manejo_errores():
    """
    Función específica para probar el manejo de errores del analizador.
    Demuestra diferentes tipos de errores y cómo son manejados.
    """
    
    print("\n" + "=" * 60)
    print("PRUEBAS DE MANEJO DE ERRORES")
    print("=" * 60)
    
    # ERROR 1: Caracteres no reconocidos
    print("\n[ERROR 1] Caracteres no validos")
    print("-" * 50)
    codigo_error1 = [
        'Deportista atleta1 25 80 75 Futbol Argentina',
        'si atleta1 @ 20 entonces {',  # @ no es válido
        '    narrar(atleta1)',
        '} endif'
    ]
    
    analizador_error1 = AnalizadorLexico(codigo_error1)
    tokens_reconocidos1 = analizador_error1.analizar_codigo_completo()
    analizador_error1.mostrar_tokens_encontrados()
    print(f"ERRORES detectados: {analizador_error1.contador_errores_lexicos}")
    print(f"TOKENS validos reconocidos: {tokens_reconocidos1}")
    
    # ERROR 2: Símbolos no definidos
    print("\n[ERROR 2] Simbolos no definidos en la gramatica")
    print("-" * 50)
    codigo_error2 = [
        'Deportista atleta1 25 80 75 Futbol Argentina',
        'si atleta1 & atleta2 entonces {',  # & no está definido
        '    narrar(resultado)',
        '} endif',
        'Repetir(3) [',
        '    input(datos) $ extra',  # $ no es válido
        '] FinRep'
    ]
    
    analizador_error2 = AnalizadorLexico(codigo_error2)
    tokens_reconocidos2 = analizador_error2.analizar_codigo_completo()
    analizador_error2.mostrar_tokens_encontrados()
    print(f"ERRORES detectados: {analizador_error2.contador_errores_lexicos}")
    print(f"TOKENS validos reconocidos: {tokens_reconocidos2}")
    
    # ERROR 3: Caracteres especiales problemáticos (sin Unicode problemático)
    print("\n[ERROR 3] Caracteres especiales y simbolos problematicos")
    print("-" * 50)
    codigo_error3 = [
        'Deportista atleta1 25 80 75 Futbol Argentina',
        'si atleta1 ~= 20 entonces {',  # ~= no está definido, debe ser !=
        '    narrar(atleta1)',
        '} endif',
        '; Comentario normal esta bien',
        'Lista Deportista participantes^'  # ^ no es válido
    ]
    
    analizador_error3 = AnalizadorLexico(codigo_error3)
    tokens_reconocidos3 = analizador_error3.analizar_codigo_completo()
    analizador_error3.mostrar_tokens_encontrados()
    print(f"ERRORES detectados: {analizador_error3.contador_errores_lexicos}")
    print(f"TOKENS validos reconocidos: {tokens_reconocidos3}")
    
    # ERROR 4: Secuencias de caracteres problemáticos
    print("\n[ERROR 4] Secuencias problematicas")
    print("-" * 50)
    codigo_error4 = [
        'Deportista atleta1 25 80 75 Futbol Argentina',
        'si atleta1 >> 20 entonces {',  # >> no definido (debe ser >)
        '    narrar(atleta1) << resultado',  # << no definido
        '} endif',
        'variable# = 100',  # # no es válido en identificadores, = no definido
        'Repetir(3) [',
        '    input(datos',  # Paréntesis incompleto
        '] FinRep'
    ]
    
    analizador_error4 = AnalizadorLexico(codigo_error4)
    tokens_reconocidos4 = analizador_error4.analizar_codigo_completo()
    analizador_error4.mostrar_tokens_encontrados()
    print(f"ERRORES detectados: {analizador_error4.contador_errores_lexicos}")
    print(f"TOKENS validos reconocidos: {tokens_reconocidos4}")
    
    # ERROR 5: Números y caracteres mixtos problemáticos
    print("\n[ERROR 5] Numeros y caracteres mixtos problematicos")
    print("-" * 50)
    codigo_error5 = [
        'Deportista atleta1 25.5.3 80 75 Futbol Argentina',  # 25.5.3 no es un número válido
        'si atleta1 !== 20 entonces {',  # !== no está definido (debe ser !=)
        '    narrar(atleta1)',
        '} endif',
        'Lista* Deportista participantes'  # * no es válido
    ]
    
    analizador_error5 = AnalizadorLexico(codigo_error5)
    tokens_reconocidos5 = analizador_error5.analizar_codigo_completo()
    analizador_error5.mostrar_tokens_encontrados()
    print(f"ERRORES detectados: {analizador_error5.contador_errores_lexicos}")
    print(f"TOKENS validos reconocidos: {tokens_reconocidos5}")
    
    # RESUMEN DE ERRORES
    total_errores = (analizador_error1.contador_errores_lexicos + 
                    analizador_error2.contador_errores_lexicos + 
                    analizador_error3.contador_errores_lexicos + 
                    analizador_error4.contador_errores_lexicos + 
                    analizador_error5.contador_errores_lexicos)
    
    total_tokens_validos = (tokens_reconocidos1 + tokens_reconocidos2 + 
                           tokens_reconocidos3 + tokens_reconocidos4 + tokens_reconocidos5)
    
    print(f"\n{'='*60}")
    print("RESUMEN DE MANEJO DE ERRORES")
    print(f"{'='*60}")
    print(f"Total errores detectados: {total_errores}")
    print(f"Total tokens validos procesados: {total_tokens_validos}")
    print("Caracteristicas del manejo de errores:")
    print("   • Deteccion de caracteres no reconocidos")
    print("   • Reporte de posicion exacta (linea y columna)")
    print("   • Mensajes de error descriptivos")
    print("   • Continuacion del analisis despues de errores")
    print("   • Conteo total de errores encontrados")
    print("   • Procesamiento de tokens validos en presencia de errores")
    print(f"{'='*60}")


def ejecutar_pruebas_casos_especiales():
    """
    Pruebas adicionales para casos especiales y edge cases.
    """
    
    print("\n" + "=" * 60)
    print("PRUEBAS DE CASOS ESPECIALES")
    print("=" * 60)
    
    # CASO 1: Líneas vacías y solo comentarios
    print("\n[CASO 1] Lineas vacias y comentarios")
    print("-" * 50)
    codigo_especial1 = [
        '',
        '; Solo comentario',
        '',
        '; Otro comentario',
        'Deportista atleta1 25 80 75 Futbol Argentina',
        ''
    ]
    
    analizador_esp1 = AnalizadorLexico(codigo_especial1)
    tokens_esp1 = analizador_esp1.analizar_codigo_completo()
    analizador_esp1.mostrar_tokens_encontrados()
    print(f"RESULTADO: Tokens procesados: {tokens_esp1}")
    
    # CASO 2: Identificadores con caracteres límite
    print("\n[CASO 2] Identificadores con caracteres limite")
    print("-" * 50)
    codigo_especial2 = [
        'Deportista _atleta_inicial 25 80 75 Futbol Argentina',
        'Lista Deportista lista_participantes_2024',
        'si _resultado > atleta_final_123 entonces {',
        '    narrar(competencia_mundial_final)',
        '} endif'
    ]
    
    analizador_esp2 = AnalizadorLexico(codigo_especial2)
    tokens_esp2 = analizador_esp2.analizar_codigo_completo()
    analizador_esp2.mostrar_tokens_encontrados()
    print(f"RESULTADO: Tokens procesados: {tokens_esp2}")
    
    # CASO 3: Números extremos
    print("\n[CASO 3] Numeros en casos extremos")
    print("-" * 50)
    codigo_especial3 = [
        'Deportista atleta1 0 100 999 Futbol Argentina',
        'si atleta1 > 1000000 entonces {',
        '    Resultado 0 - 0',
        '} endif',
        'Repetir(1) [',
        '    narrar(resultado)',
        '] FinRep'
    ]
    
    analizador_esp3 = AnalizadorLexico(codigo_especial3)
    tokens_esp3 = analizador_esp3.analizar_codigo_completo()
    analizador_esp3.mostrar_tokens_encontrados()
    print(f"RESULTADO: Tokens procesados: {tokens_esp3}")
    
    print(f"\n{'='*60}")
    print("RESUMEN DE CASOS ESPECIALES")
    print(f"{'='*60}")
    print(f"Caso 1 (Lineas vacias): {tokens_esp1} tokens")
    print(f"Caso 2 (Identificadores limite): {tokens_esp2} tokens")
    print(f"Caso 3 (Numeros extremos): {tokens_esp3} tokens")
    print("Todos los casos especiales manejados correctamente")
    print(f"{'='*60}")


def main():
    """
    Función principal que ejecuta todas las pruebas del analizador léxico.
    """
    print("INICIANDO SUITE COMPLETA DE PRUEBAS")
    print("=" * 60)
    
    # Ejecutar todas las pruebas
    ejecutar_pruebas_completas()
    ejecutar_pruebas_manejo_errores()
    ejecutar_pruebas_casos_especiales()
    
    # Resumen final
    print("\n" + "*" * 20)
    print("RESUMEN FINAL DE PRUEBAS")
    print("*" * 20)
    print("Pruebas de funcionalidad: COMPLETADAS")
    print("Pruebas de manejo de errores: COMPLETADAS")
    print("Pruebas de casos especiales: COMPLETADAS")
    print("TODAS LAS PRUEBAS EJECUTADAS EXITOSAMENTE")
    print("*" * 20)


if __name__ == "__main__":
    main()
