# Explorador para el lenguaje Olympiac (scanner)
from enum import Enum, auto
import re

class TipoComponente(Enum):
    """
    Enum con los tipos de componentes disponibles para Olympiac
    """
    COMENTARIO = auto()
    PALABRA_CLAVE = auto()
    TIPO_DATO = auto()
    DECLARACION = auto()
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
    DEPORTE = auto()
    PAIS = auto()
    ACTIVIDAD = auto()
    RESULTADO = auto()
    BLANCOS = auto()
    NINGUNO = auto()

class ComponenteLéxico:
    """
    Clase que almacena la información de un componente léxico
    """

    tipo    : TipoComponente
    texto   : str 

    def __init__(self, tipo_nuevo: TipoComponente, texto_nuevo: str):
        self.tipo = tipo_nuevo
        self.texto = texto_nuevo

    def __str__(self):
        resultado = f'{self.tipo:30} <{self.texto}>'
        return resultado

class Explorador:
    """
    Explorador léxico para el lenguaje Olympiac
    """

    descriptores_componentes = [
        # Comentarios (deben ir primero)
        (TipoComponente.COMENTARIO, r'^;.*'),
        
        # Palabras clave y declaraciones
        (TipoComponente.DECLARACION, r'^(Deportista|Lista)'),
        (TipoComponente.TIPO_DATO, r'^(Pais|Deporte|Resultado)'),
        
        # Estructuras de control
        (TipoComponente.ESTRUCTURA_CONTROL, r'^(si|entonces|sino|endif|Repetir|RepetirHasta|FinRep|FinRepHast)'),
        
        # Funciones y acciones
        (TipoComponente.FUNCION, r'^(narrar|comparar|input|probabilidad|preparacion|finprep|InicioCarrera|correr|finCarr|InicioRutina|ejecutar|finRuti|finact)'),
        
        # Actividades deportivas
        (TipoComponente.ACTIVIDAD, r'^(partido|carrera|combate|rutina|competencia|medallas)'),
        
        # Operadores y comparadores
        (TipoComponente.COMPARADOR, r'^(==|!=|>|<|>=|<=|vs)'),
        (TipoComponente.OPERADOR, r'^(\+|-|\*|/|%)'),
        
        # Textos (entre comillas)
        (TipoComponente.TEXTO, r'^"([^"\\]*(\\.[^"\\]*)*)"'),
        
        # Números
        (TipoComponente.FLOTANTE, r'^(-?[0-9]+\.[0-9]+)'),
        (TipoComponente.ENTERO, r'^(-?[0-9]+)'),
        
        # Booleanos
        (TipoComponente.BOOLEANO, r'^(True|False)'),
        
        # Identificadores (nombres de variables, países, deportes, etc.)
        (TipoComponente.IDENTIFICADOR, r'^([a-zA-Z_][a-zA-Z0-9_]*)'),
        
        # Puntuación
        (TipoComponente.PUNTUACION, r'^([(),;:{}\[\]\-])'),
        
        # Blancos (deben ir al final)
        (TipoComponente.BLANCOS, r'^(\s)+')
    ]

    def __init__(self, contenido_archivo):
        self.texto = contenido_archivo
        self.componentes = []

    def explorar(self):
        """
        Itera sobre cada una de las líneas y las va procesando
        """
        for linea in self.texto:
            resultado = self.procesar_linea(linea)
            self.componentes = self.componentes + resultado

    def imprimir_componentes(self):
        """
        Imprime en pantalla los componentes léxicos
        """
        for componente in self.componentes:
            print(componente)

    def procesar_linea(self, linea):
        """
        Toma cada línea y la procesa extrayendo los componentes léxicos
        """
        componentes = []
        posicion = 0
        linea = linea.rstrip()  # Remover espacios al final

        while posicion < len(linea):
            segmento = linea[posicion:]
            coincidencia_encontrada = False

            for tipo_componente, regex in self.descriptores_componentes:
                respuesta = re.match(regex, segmento)
                
                if respuesta:
                    texto_coincidencia = respuesta.group()
                    
                    # Ignorar comentarios y blancos
                    if (tipo_componente is not TipoComponente.BLANCOS and 
                        tipo_componente is not TipoComponente.COMENTARIO):
                        
                        nuevo_componente = ComponenteLéxico(tipo_componente, texto_coincidencia)
                        componentes.append(nuevo_componente)
                    
                    posicion += respuesta.end()
                    coincidencia_encontrada = True
                    break
            
            if not coincidencia_encontrada:
                # Manejo de error: carácter no reconocido
                print(f"Error léxico: Carácter no reconocido '{segmento[0]}' en posición {posicion}")
                posicion += 1  # Saltar el carácter problemático

        return componentes

# Ejemplo de uso
if __name__ == "__main__":
    # Código de ejemplo en Olympiac
    codigo_ejemplo = [
        'Deportista atleta1 25 180 75 "Fútbol" "Argentina"',
        'Deportista atleta2 30 150 65 "Fútbol" "Alemania"',
        'si comparar(atleta1, atleta2) > 0 entonces',
        '    narrar("El atleta1 es mejor")',
        'endif;',
        'Lista Deportista lista_competidores',
        'Repetir(5)',
        '    narrar("Competencia")',
        'FinRep'
    ]
    
    explorador = Explorador(codigo_ejemplo)
    explorador.explorar()
    explorador.imprimir_componentes()
