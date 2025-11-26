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
# ; EJEMPLO LIMPIO: SISTEMA DE GESTIÓN OLIMPICA AVANZADO
# ; Demuestra: Deportistas, Narración, Comparaciones, Listas, Condicionales, Ciclos
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
# ; FASE 2: DECLARACIÓN DE LISTAS
# ; ============================================================================
medallistas = []  # lista declarada
competidores = []  # lista declarada
# ; ============================================================================
# ; FASE 3: NARRACIÓN INICIAL
# ; ============================================================================
narrar('UsainBolt')
narrar('MichaelPhelps')
narrar('SimoneBiles')
# ; ============================================================================
# ; FASE 4: COMPARACIONES Y AGREGACIÓN A LISTAS
# ; ============================================================================
if True:
    medallistas.append('UsainBolt')
if True:
    medallistas.append('SimoneBiles')
if True:
    medallistas.append('LuisaSonza')
# ; ============================================================================
# ; FASE 5: AGREGACIÓN A SEGUNDA LISTA
# ; ============================================================================
competidores.append('UsainBolt')
competidores.append('MichaelPhelps')
competidores.append('SimoneBiles')
# ; ============================================================================
# ; FASE 6: CICLO SIMPLE CON NARRACIÓN
# ; ============================================================================
for _i in range(3):
    narrar('UsainBolt')
    narrar('MichaelPhelps')
# ; ============================================================================
# ; FASE 7: CICLO CON NARRACIÓN MÚLTIPLE
# ; ============================================================================
for _i in range(2):
    narrar('SimoneBiles')
    narrar('LuisaSonza')
    narrar('NovaLachance')
# ; ============================================================================
# ; FASE 8: CONDICIONAL SIMPLE - SIN SINO
# ; ============================================================================
if True:
    narrar('UsainBolt')
# ; ============================================================================
# ; FASE 9: OTRO CONDICIONAL SIMPLE
# ; ============================================================================
if True:
    narrar('SimoneBiles')
# ; ============================================================================
# ; FASE 10: MÁS COMPARACIONES
# ; ============================================================================
comparar('UsainBolt', 'NovaLachance')  # resultado descartado
comparar('SimoneBiles', 'MichaelPhelps')  # resultado descartado
comparar('LuisaSonza', 'SimoneBiles')  # resultado descartado
# ; ============================================================================
# ; FASE 11: CONDICIONAL CON MÚLTIPLES ACCIONES
# ; ============================================================================
if True:
    narrar('UsainBolt')
    narrar('MichaelPhelps')
# ; ============================================================================
# ; FASE 12: CICLO HASTA CON CONDICIONAL
# ; ============================================================================
for _j in range(2):
    if True:
        narrar('SimoneBiles')
# ; ============================================================================
# ; FIN DEL PROGRAMA
# ; ============================================================================
