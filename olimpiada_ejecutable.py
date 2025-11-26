# === Ambiente estándar Olympiac → Python ===

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

# === Código generado ===

# ; ============================================================================
# ; EJEMPLO LIMPIO: SISTEMA DE GESTIÓN OLIMPICA
# ; Demuestra características del lenguaje Olympiac SIN ERRORES
# ; ============================================================================
# ; ============================================================================
# ; FASE 1: DECLARACIÓN DE DEPORTISTAS
# ; ============================================================================
registrar_deportista('UsainBolt', ['98', '95', '96'], 'Atletismo', 'Jamaica')
registrar_deportista('MichaelPhelps', ['97', '96', '95'], 'Natacion', 'USA')
registrar_deportista('SimoneBiles', ['99', '97', '98'], 'Gimnasia', 'USA')
registrar_deportista('NovaLachance', ['94', '92', '94'], 'Badminton', 'Canada')
registrar_deportista('LuisaSonza', ['91', '88', '90'], 'Tenis', 'Brasil')
# ; ============================================================================
# ; FASE 2: NARRACIÓN - PRESENTACIÓN
# ; ============================================================================
narrar('UsainBolt')
narrar('MichaelPhelps')
narrar('SimoneBiles')
# ; ============================================================================
# ; FASE 3: COMPARACIONES MÚLTIPLES
# ; ============================================================================
comparar('UsainBolt', 'MichaelPhelps')  # resultado descartado
comparar('SimoneBiles', 'NovaLachance')  # resultado descartado
comparar('LuisaSonza', 'UsainBolt')  # resultado descartado
# ; ============================================================================
# ; FASE 4: CICLOS - REPETICIÓN SIMPLE
# ; ============================================================================
narrar('UsainBolt')
narrar('MichaelPhelps')
narrar('SimoneBiles')
# ; ============================================================================
# ; FASE 5: CICLOS CON NARRACIONES MÚLTIPLES
# ; ============================================================================
narrar('SimoneBiles')
narrar('LuisaSonza')
narrar('NovaLachance')
# ; ============================================================================
# ; FASE 6: MÁS COMPARACIONES EN SECUENCIA
# ; ============================================================================
comparar('UsainBolt', 'NovaLachance')  # resultado descartado
comparar('SimoneBiles', 'MichaelPhelps')  # resultado descartado
comparar('LuisaSonza', 'UsainBolt')  # resultado descartado
# ; ============================================================================
# ; FASE 7: OTRO CICLO DE COMPETENCIA
# ; ============================================================================
narrar('UsainBolt')
narrar('SimoneBiles')
# ; ============================================================================
# ; FIN DEL PROGRAMA
# ; ============================================================================
