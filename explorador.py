from enum import Enum, auto
import re

class TipoComponente(Enum):
    COMENTARIO = auto()
    PALABRA_CLAVE = auto()
    DECLARACION = auto()
    TIPO_DATO = auto()
    ESTRUCTURA_CONTROL = auto()
    FUNCION = auto()
    OPERADOR = auto()
    COMPARADOR = auto()
    TEXTO = auto()
    IDENTIFICADOR = auto()
    ENTERO = auto()
    FLOTANTE = auto()
    BOOLEANO = auto()
    PUNTUACION = auto()
    RESULTADO_EXTRA = auto()
    EMPATE = auto()
    BLANCOS = auto()
    NINGUNO = auto()

class ComponenteLexico:
    def __init__(self, tipo, texto):
        self.tipo = tipo
        self.texto = texto

    def __str__(self):
        return f'{self.tipo:30} <{self.texto}>'

class Explorador:
    descriptores_componentes = [
        (TipoComponente.COMENTARIO, r'^;.*'),
        (TipoComponente.DECLARACION, r'^(Deportista|Lista)'),
        (TipoComponente.TIPO_DATO, r'^(Pais|Deporte|Resultado)'),
        (TipoComponente.ESTRUCTURA_CONTROL, r'^(si|entonces|sino|endif|Repetir|RepetirHasta|FinRep|FinRepHast)'),
        (TipoComponente.FUNCION, r'^(narrar|Comparar\(|input\(|preparacion|finprep|InicioCarrera|correr|finCarr|InicioRutina|ejecutar|finRuti|finact)'),
        (TipoComponente.RESULTADO_EXTRA, r'^(listaRes)'),
        (TipoComponente.EMPATE, r'^(empate)'),
        (TipoComponente.COMPARADOR, r'^(==|!=|>|<|>=|<=)'),
        (TipoComponente.OPERADOR, r'^(\+|-|\*|/|%)'),
        (TipoComponente.TEXTO, r'^"([^"\\]*(\\.[^"\\]*)*)?"'),
        (TipoComponente.FLOTANTE, r'^(-?[0-9]+\.[0-9]+)'),
        (TipoComponente.ENTERO, r'^(-?[0-9]+)'),
        (TipoComponente.BOOLEANO, r'^(True|False)'),
        (TipoComponente.IDENTIFICADOR, r'^([a-zA-Z_][a-zA-Z0-9_]*)'),
        (TipoComponente.PUNTUACION, r'^([(),;:{}\[\]\-])'),
        (TipoComponente.BLANCOS, r'^(\s)+')
    ]

    def __init__(self, contenido_archivo):
        self.texto = contenido_archivo
        self.componentes = []

    def explorar(self):
        for linea in self.texto:
            resultado = self.procesar_linea(linea)
            self.componentes += resultado

    def imprimir_componentes(self):
        for componente in self.componentes:
            print(componente)

    def procesar_linea(self, linea):
        componentes = []
        posicion = 0
        linea = linea.rstrip()

        while posicion < len(linea):
            segmento = linea[posicion:]
            coincidencia_encontrada = False

            for tipo_componente, regex in self.descriptores_componentes:
                respuesta = re.match(regex, segmento)
                if respuesta:
                    texto = respuesta.group()
                    if tipo_componente not in [TipoComponente.BLANCOS, TipoComponente.COMENTARIO]:
                        componentes.append(ComponenteLexico(tipo_componente, texto))
                    posicion += respuesta.end()
                    coincidencia_encontrada = True
                    break

            if not coincidencia_encontrada:
                print(f"Error léxico: Carácter no reconocido '{segmento[0]}' en posición {posicion}")
                posicion += 1

        return componentes

# Ejemplo de uso
if __name__ == "__main__":
    codigo_ejemplo = [
        '; Inicio del programa',
        'Deportista atleta1 25 80 75 "Fútbol" "Argentina"',
        'Deportista atleta2 30 75 70 "Fútbol" "Brasil"',
        'Lista Deportista lista_competidores',
        'si Comparar(atleta1, atleta2) > 0 entonces {',
        '    narrar("El atleta1 tiene mejor rendimiento")',
        '} sino {',
        '    narrar("El atleta2 es superior")',
        '} endif',
        'Repetir(3) [',
        '    narrar("Entrenamiento diario")',
        '    input(Pais)',
        '] FinRep',
        'RepetirHasta(Comparar(atleta1, atleta2) == 0) [',
        '    narrar("Seguimos entrenando hasta igualar rendimiento")',
        '] FinRepHast',
        'Bloque',
        'Fútbol',
        '    Lista Deportista lista_partido',
        '    competencia',
        '        partido',
        '            Argentina vs Brasil',
        '            Comparar(Argentina, Brasil)',
        '            narrar(Deportista "vs" Deportista)',
        '            empate',
        '            Resultado 2 - 2',
        '            listaRes',
        '        finact',
        '    medallas',
        'narrar("Fin del bloque deportivo")'
    ]

    explorador = Explorador(codigo_ejemplo)
    explorador.explorar()
    explorador.imprimir_componentes()
