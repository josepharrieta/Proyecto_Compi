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

# ; Programa: Torneo completo -- version corregida para el analizador
# ; Se mantiene la misma informacion pero con tokens seguros para el lexer
# ; Declaracion de deportistas
registrar_deportista('Kaka', ['91', '80', '90'], 'Futbol', 'Francia')
registrar_deportista('Mbappe', ['97', '95', '90'], 'Futbol', 'Inglaterra')
registrar_deportista('Jude', ['90', '89', '89'], 'Futbol', 'Brazil')
registrar_deportista('Musiala', ['87', '90', '92'], 'Futbol', 'Alemania')
# ; Lista de deportistas (coleccion)
List_est_dep = []  # lista declarada
# ; -- Torneo: partido 1 --
# ; Encuentro: Francia vs Inglaterra (representado como string para evitar token desconocido)
narrar("Encuentro: Francia vs Inglaterra")
# ; Duelo entre jugadores
narrar("Duelo: Mbappe contra Jude")
# ; Agregar resultado de comparacion a la lista de deportistas
comparar('Mbappe', 'Jude')  # resultado descartado
# ; Mostrar resultado (se usa narrar para evitar tokens problematicos con guiones/numeros)
narrar("Resultado: 1 - 0")
# ; -- Torneo: partido 2 --
narrar("Encuentro: Alemania vs Brazil")
narrar("Duelo: Musiala contra Kaka")
comparar('Musiala', 'Kaka')  # resultado descartado
narrar("Resultado: 7 - 0")
# ; Decisiones basadas en comparaciones (ejemplos)
if True:
    narrar('Mbappe')
if True:
    narrar('Jude')
if True:
    narrar('Musiala')
if True:
    narrar('Kaka')
# ; Repeticion de ejemplo
for _ in range(int(3)):
    narrar("Entrenamiento en curso")
