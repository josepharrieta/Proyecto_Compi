"""
Analizador Léxico para Olympiac
=========================================

Este módulo implementa un analizador léxico (lexer) para un lenguaje de dominio específico
orientado a la gestión de deportistas y competencias. El analizador identifica y clasifica
tokens en el código fuente, incluyendo declaraciones, tipos de datos, estructuras de control,
funciones y operadores.

Autores: [Kevin Núñez, Axel López, Felipe Murillo, Joseph Arrieta, Arturo Chavarría]
Fecha: Octubre 2025
Versión: 1.1

Dependencias:
- enum: Para definir tipos de componentes léxicos
- re: Para procesamiento de expresiones regulares

"""

from enum import Enum, auto
import re


class TipoToken(Enum):
    """
    Enumeración que define todos los tipos de tokens que puede reconocer el analizador léxico.
    
    Cada tipo representa una categoría sintáctica específica del lenguaje deportivo:
    - COMENTARIO: Líneas que inician con ';'
    - PALABRA_CLAVE: Palabras reservadas del lenguaje
    - DECLARACION_ENTIDAD: Declaraciones de entidades (Deportista, Lista)
    - TIPO_DATO_DOMINIO: Tipos específicos del dominio (Pais, Deporte, Resultado)
    - ESTRUCTURA_CONTROL_FLUJO: Elementos de control de flujo (si, entonces, repetir)
    - INVOCACION_FUNCION: Llamadas a funciones del sistema
    - OPERADOR_ARITMETICO: Operadores matemáticos (+, -, *, /, %)
    - OPERADOR_COMPARACION: Operadores de comparación (==, !=, >, <, >=, <=)
    - OPERADOR_ESPECIAL: Operadores especiales como 'vs'
    - LITERAL_CADENA: Cadenas de texto entre comillas
    - NOMBRE_IDENTIFICADOR: Nombres de variables y entidades
    - NUMERO_ENTERO: Valores numéricos enteros
    - NUMERO_DECIMAL: Valores numéricos con decimales
    - VALOR_BOOLEANO: Valores True/False
    - SIMBOLO_PUNTUACION: Símbolos de puntuación y delimitadores
    - RESULTADO_ADICIONAL: Tokens específicos para resultados (listaRes)
    - CONDICION_EMPATE: Token específico para empates
    - ESPACIOS_BLANCOS: Espacios, tabs y otros caracteres de espacio
    - TOKEN_NO_RECONOCIDO: Tokens que no coinciden con ningún patrón
    """
    COMENTARIO = auto()
    PALABRA_CLAVE = auto()
    DECLARACION_ENTIDAD = auto()
    TIPO_DATO_DOMINIO = auto()
    ESTRUCTURA_CONTROL_FLUJO = auto()
    INVOCACION_FUNCION = auto()
    OPERADOR_ARITMETICO = auto()
    OPERADOR_COMPARACION = auto()
    OPERADOR_ESPECIAL = auto()
    LITERAL_CADENA = auto()
    NOMBRE_IDENTIFICADOR = auto()
    NUMERO_ENTERO = auto()
    NUMERO_DECIMAL = auto()
    VALOR_BOOLEANO = auto()
    SIMBOLO_PUNTUACION = auto()
    RESULTADO_ADICIONAL = auto()
    CONDICION_EMPATE = auto()
    ESPACIOS_BLANCOS = auto()
    TOKEN_NO_RECONOCIDO = auto()


class TokenLexico:
    """
    Representa un token léxico individual encontrado durante el análisis.
    
    Atributos:
        tipo_token (TipoToken): El tipo de token identificado
        texto_original (str): El texto exacto del token en el código fuente
        informacion_adicional (str): Información semántica adicional sobre el token
        numero_linea (int): Línea donde se encontró el token (opcional)
        posicion_columna (int): Columna donde inicia el token (opcional)
    """
    
    def __init__(self, tipo_token, texto_original, informacion_adicional="", numero_linea=0, posicion_columna=0):
        """
        Inicializa un nuevo token léxico.
        
        Argumentos:
            tipo_token (TipoToken): El tipo de token identificado
            texto_original (str): El texto exacto del token
            informacion_adicional (str, optional): Información semántica adicional. Por defecto "".
            numero_linea (int, optional): Número de línea. Por defecto 0.
            posicion_columna (int, optional): Posición de columna. Por defecto 0.
        """
        self.tipo_token = tipo_token
        self.texto_original = texto_original
        self.informacion_adicional = informacion_adicional
        self.numero_linea = numero_linea
        self.posicion_columna = posicion_columna

    def __str__(self):
        """
        Representación en cadena del token para depuración y visualización.
        
        Salida:
            str: Representación formateada del token en el formato requerido
        """
        return f'<"{self.tipo_token.name}", "{self.texto_original}", "{self.informacion_adicional}">'

    def __repr__(self):
        """
        Representación técnica del token para depuración.
        
        Salida:
            str: Representación técnica del token
        """
        return f"TokenLexico({self.tipo_token}, '{self.texto_original}', '{self.informacion_adicional}')"
    
    def to_dict(self):
        """
        Convierte el token a un diccionario para fácil acceso y serialización.
        
        Salida:
            dict: Diccionario con toda la información del token
        """
        return {
            'tipo': self.tipo_token.name,
            'texto': self.texto_original,
            'info': self.informacion_adicional,
            'linea': self.numero_linea,
            'columna': self.posicion_columna
        }
    
    def to_tuple(self):
        """
        Convierte el token a una tupla para estructuras de datos ligeras.
        
        Salida:
            tuple: Tupla con (tipo, texto, info, linea, columna)
        """
        return (self.tipo_token.name, self.texto_original, self.informacion_adicional, 
                self.numero_linea, self.posicion_columna)


class AnalizadorLexico:
    """
    Analizador léxico principal para el lenguaje deportivo.
    
    Este analizador procesa código fuente línea por línea, identificando y clasificando
    cada token según patrones de expresiones regulares predefinidos. Mantiene una lista
    de todos los tokens encontrados y proporciona métodos para su análisis y visualización.
    
    Atributos:
        codigo_fuente_lineas (list): Lista de líneas del código fuente a analizar
        tokens_encontrados (list): Lista de todos los tokens identificados
        patrones_reconocimiento (list): Patrones regex para cada tipo de token
        contador_errores_lexicos (int): Número de errores léxicos encontrados
    """
    
    # Patrones de expresiones regulares para cada tipo de token
    # Ordenados por prioridad de coincidencia (más específicos primero)
    patrones_reconocimiento = [
        (TipoToken.COMENTARIO, r'^;.*', "Comentario de línea completa"),
        (TipoToken.DECLARACION_ENTIDAD, r'^(Deportista|Lista)', "Declaración de entidad del dominio"),
        (TipoToken.TIPO_DATO_DOMINIO, r'^(Pais|Deporte|Resultado)', "Tipo de dato específico del dominio"),
        (TipoToken.ESTRUCTURA_CONTROL_FLUJO, r'^(si|entonces|sino|endif|Repetir|RepetirHasta|FinRep|FinRepHast)', "Estructura de control de flujo"),
        (TipoToken.INVOCACION_FUNCION, r'^(narrar\(|Comparar\(|input\()', "Invocación de función del sistema"),
        (TipoToken.PALABRA_CLAVE, r'^(preparacion|finprep|InicioCarrera|correr|finCarr|InicioRutina|ejecutar|finRuti|finact|ceremonia_medallas|competencia_oficial|partido_clasificatorio)', "Palabras clave del dominio"),
        (TipoToken.RESULTADO_ADICIONAL, r'^(listaRes)', "Token específico para listas de resultados"),
        (TipoToken.CONDICION_EMPATE, r'^(empate)', "Token específico para condiciones de empate"),
        (TipoToken.OPERADOR_COMPARACION, r'^(==|!=|>=|<=|>|<)', "Operador de comparación lógica"),
        (TipoToken.OPERADOR_ESPECIAL, r'^(vs)', "Operador especial vs"),
        (TipoToken.OPERADOR_ARITMETICO, r'^(\+|-|\*|/|%)', "Operador aritmético básico"),
        (TipoToken.NUMERO_ENTERO, r'^([0-9]+)', "Número entero positivo"),
        (TipoToken.VALOR_BOOLEANO, r'^(True|False)', "Valor lógico booleano"),
        (TipoToken.NOMBRE_IDENTIFICADOR, r'^([a-zA-Z_][a-zA-Z0-9_]*)', "Identificador válido"),
        (TipoToken.SIMBOLO_PUNTUACION, r'^([(),;:{}\[\]\.-])', "Símbolo de puntuación o delimitador"),
        (TipoToken.ESPACIOS_BLANCOS, r'^(\s)+', "Espacios en blanco y caracteres de formato")
    ]

    def __init__(self, codigo_fuente_lineas):
        """
        Inicializa el analizador léxico con el código fuente a procesar.
        
        Entradas:
            codigo_fuente_lineas (list): Lista de cadenas, cada una representando una línea de código
        """
        self.codigo_fuente_lineas = codigo_fuente_lineas
        self.tokens_encontrados = []
        self.contador_errores_lexicos = 0
        self.errores_detallados = []

    def analizar_codigo_completo(self):
        """
        Realiza el análisis léxico completo de todas las líneas del código fuente.
        
        Procesa cada línea secuencialmente, identifica todos los tokens y los almacena
        en la lista de tokens encontrados. También cuenta los errores léxicos encontrados.
        
        Salida:
            int: Número total de tokens válidos encontrados (excluyendo espacios en blanco)
        """
        self.tokens_encontrados.clear()
        self.contador_errores_lexicos = 0
        self.errores_detallados.clear()
        
        for numero_linea, linea_codigo in enumerate(self.codigo_fuente_lineas, 1):
            tokens_linea = self._procesar_linea_individual(linea_codigo, numero_linea)
            self.tokens_encontrados.extend(tokens_linea)
        
        tokens_validos = [t for t in self.tokens_encontrados if t.tipo_token != TipoToken.ESPACIOS_BLANCOS]
        return len(tokens_validos)

    def obtener_tokens(self, incluir_espacios=False):
        """
        Retorna la lista de tokens encontrados.
        
        Entradas:
            incluir_espacios (bool): Si True, incluye tokens de espacios en blanco. Por defecto False.
            
        Salida:
            list: Lista de objetos TokenLexico
        """
        if incluir_espacios:
            return self.tokens_encontrados.copy()
        else:
            return [t for t in self.tokens_encontrados if t.tipo_token != TipoToken.ESPACIOS_BLANCOS]

    def obtener_tokens_como_diccionarios(self, incluir_espacios=False):
        """
        Retorna los tokens como lista de diccionarios.
        
        Entradas:
            incluir_espacios (bool): Si True, incluye tokens de espacios en blanco. Por defecto False.
            
        Salida:
            list: Lista de diccionarios con información de cada token
        """
        tokens = self.obtener_tokens(incluir_espacios)
        return [token.to_dict() for token in tokens]

    def obtener_tokens_como_tuplas(self, incluir_espacios=False):
        """
        Retorna los tokens como lista de tuplas.
        
        Entradas:
            incluir_espacios (bool): Si True, incluye tokens de espacios en blanco. Por defecto False.
            
        Salida:
            list: Lista de tuplas (tipo, texto, info, linea, columna)
        """
        tokens = self.obtener_tokens(incluir_espacios)
        return [token.to_tuple() for token in tokens]

    def obtener_errores(self):
        """
        Retorna la lista de errores léxicos encontrados.
        
        Salida:
            list: Lista de diccionarios con información de cada error
        """
        return self.errores_detallados.copy()

    def obtener_resumen(self):
        """
        Retorna un resumen del análisis léxico realizado.
        
        Salida:
            dict: Diccionario con estadísticas del análisis
        """
        tokens_validos = self.obtener_tokens()
        
        resumen = {
            'total_lineas': len(self.codigo_fuente_lineas),
            'total_tokens': len(tokens_validos),
            'total_errores': self.contador_errores_lexicos,
            'tokens_por_tipo': {},
            'tiene_errores': self.contador_errores_lexicos > 0
        }
        
        for token in tokens_validos:
            tipo_nombre = token.tipo_token.name
            resumen['tokens_por_tipo'][tipo_nombre] = resumen['tokens_por_tipo'].get(tipo_nombre, 0) + 1
        
        return resumen

    def _procesar_linea_individual(self, linea_codigo, numero_linea):
        """
        Procesa una línea individual del código fuente y extrae todos sus tokens.
        VERSIÓN MEJORADA con manejo de Unicode y errores.
        
        Entradas:
            linea_codigo (str): La línea de código a procesar
            numero_linea (int): Número de línea para referencia de errores
            
        Salida:
            list: Lista de tokens encontrados en la línea
        """
        tokens_linea = []
        posicion_actual = 0
        linea_limpia = linea_codigo.rstrip()

        while posicion_actual < len(linea_limpia):
            segmento_restante = linea_limpia[posicion_actual:]
            token_encontrado = False

            for tipo_token, patron_regex, descripcion in self.patrones_reconocimiento:
                coincidencia = re.match(patron_regex, segmento_restante)
                
                if coincidencia:
                    texto_token = coincidencia.group()
                    
                    if tipo_token != TipoToken.ESPACIOS_BLANCOS:
                        informacion_semantica = self._extraer_informacion_semantica(tipo_token, texto_token)
                        nuevo_token = TokenLexico(
                            tipo_token, 
                            texto_token, 
                            informacion_semantica,
                            numero_linea,
                            posicion_actual + 1
                        )
                        tokens_linea.append(nuevo_token)
                    
                    posicion_actual += coincidencia.end()
                    token_encontrado = True
                    break

            if not token_encontrado:
                caracter_problematico = segmento_restante[0]
                
                try:
                    if ord(caracter_problematico) < 128:
                        caracter_mostrable = f"'{caracter_problematico}'"
                    else:
                        caracter_mostrable = f"Unicode U+{ord(caracter_problematico):04X}"
                    
                    if ord(caracter_problematico) > 127:
                        tipo_error = "caracter Unicode no soportado"
                    elif caracter_problematico in '@#$%&^*=~':
                        tipo_error = "simbolo no definido en la gramatica"
                    else:
                        tipo_error = "caracter no reconocido"
                    
                    # Guardar error en lista
                    error_info = {
                        'tipo': tipo_error,
                        'caracter': caracter_mostrable,
                        'linea': numero_linea,
                        'columna': posicion_actual + 1,
                        'mensaje': f"ERROR LEXICO: {tipo_error} {caracter_mostrable} en linea {numero_linea}, columna {posicion_actual + 1}"
                    }
                    self.errores_detallados.append(error_info)
                    
                except Exception as e:
                    error_info = {
                        'tipo': 'error desconocido',
                        'caracter': f"ord({ord(caracter_problematico)})",
                        'linea': numero_linea,
                        'columna': posicion_actual + 1,
                        'mensaje': f"ERROR LEXICO: caracter problematico (ord={ord(caracter_problematico)}) en linea {numero_linea}, columna {posicion_actual + 1}"
                    }
                    self.errores_detallados.append(error_info)
                
                self.contador_errores_lexicos += 1
                posicion_actual += 1

        return tokens_linea

    def _extraer_informacion_semantica(self, tipo_token, texto_token):
        """
        Extrae información semántica adicional basada en el tipo y contenido del token.
        
        Entradas:
            tipo_token (TipoToken): El tipo de token identificado
            texto_token (str): El texto original del token
            
        Salida:
            str: Información semántica adicional sobre el token
        """
        if tipo_token == TipoToken.NUMERO_ENTERO:
            try:
                valor_numerico = int(texto_token)
                return f"Valor numérico: {valor_numerico}"
            except ValueError:
                return "Error al convertir número entero"
                
        elif tipo_token == TipoToken.NUMERO_DECIMAL:
            try:
                valor_decimal = float(texto_token)
                return f"Valor decimal: {valor_decimal}"
            except ValueError:
                return "Error al convertir número decimal"
                
        elif tipo_token == TipoToken.LITERAL_CADENA:
            contenido_cadena = texto_token.strip('"')
            return f"Contenido de cadena: '{contenido_cadena}'"
            
        elif tipo_token == TipoToken.NOMBRE_IDENTIFICADOR:
            return "Identificador válido de usuario"
            
        elif tipo_token == TipoToken.INVOCACION_FUNCION:
            return "Función del sistema invocada"
            
        elif tipo_token == TipoToken.OPERADOR_ARITMETICO:
            operadores_descripcion = {
                '+': 'suma', '-': 'resta', '*': 'multiplicación', 
                '/': 'división', '%': 'módulo'
            }
            return f"Operador de {operadores_descripcion.get(texto_token, 'desconocido')}"
            
        elif tipo_token == TipoToken.OPERADOR_COMPARACION:
            comparadores_descripcion = {
                '==': 'igualdad', '!=': 'desigualdad', '>': 'mayor que',
                '<': 'menor que', '>=': 'mayor o igual', '<=': 'menor o igual'
            }
            return f"Comparador de {comparadores_descripcion.get(texto_token, 'desconocido')}"
            
        elif tipo_token == TipoToken.OPERADOR_ESPECIAL:
            return f"Operador especial: {texto_token}"
            
        elif tipo_token == TipoToken.VALOR_BOOLEANO:
            return f"Valor lógico: {texto_token}"
            
        elif tipo_token == TipoToken.DECLARACION_ENTIDAD:
            return f"Declaración de entidad del tipo: {texto_token}"
            
        elif tipo_token == TipoToken.TIPO_DATO_DOMINIO:
            return f"Tipo de dato del dominio deportivo: {texto_token}"
            
        elif tipo_token == TipoToken.PALABRA_CLAVE:
            return f"Palabra clave del dominio: {texto_token}"
            
        else:
            return "Token reconocido"

if __name__ == "__main__":
    print("MODULO ANALIZADOR LEXICO OLYMPIAC")
