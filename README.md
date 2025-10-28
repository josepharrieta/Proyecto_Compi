# Proyecto Compiladores - Analizador Olympiac

Sistema de análisis léxico y sintáctico para el lenguaje de dominio específico **Olympiac**, orientado a la gestión de deportistas y competencias deportivas.

## 📋 Descripción

Este proyecto implementa un analizador completo para archivos `.oly` (Olympiac) que incluye:
- **Analizador Léxico (Explorador)**: Tokeniza el código fuente
- **Analizador Sintáctico (Parser)**: Construye el Árbol de Sintaxis Abstracta (AST)
- **Lector**: Coordina el flujo completo de análisis

## 🏗️ Arquitectura del Sistema

```
┌─────────────┐
│   LECTOR    │  Lee archivo .oly
└──────┬──────┘
       │ envía líneas
       ▼
┌─────────────┐
│ EXPLORADOR  │  Analiza léxicamente (tokeniza)
│  (Léxico)   │
└──────┬──────┘
       │ retorna tokens
       ▼
┌─────────────┐
│   LECTOR    │  Recibe tokens
└──────┬──────┘
       │ envía tokens
       ▼
┌─────────────┐
│ ANALIZADOR  │  Genera AST
│ SINTÁCTICO  │
└──────┬──────┘
       │ retorna AST
       ▼
┌─────────────┐
│   LECTOR    │  Retorna resultado completo
└─────────────┘
```

## 📁 Estructura del Proyecto

```
Proyecto_Compi/
├── lector_olympiac.py           # Coordinador principal del flujo
├── explorador.py                # Analizador léxico (tokenizador)
├── analizador_sintactico.py     # Analizador sintáctico (parser)
├── nodo.py                      # Estructura de nodos del AST
├── ejemplo1.oly                 # Archivo de ejemplo en Olympiac
├── ejemplo_flujo.py             # Demostración del flujo completo
├── test_explorador.py           # Tests del analizador léxico
├── test_analizador_sintactico.py # Tests del parser
└── README.md                    # Este archivo
```

## 🚀 Uso

### Método 1: Flujo Completo Automático

```python
from lector_olympiac import procesar_archivo_completo

# Procesar archivo completo
resultado = procesar_archivo_completo("ejemplo1.oly")

# Acceder a los componentes
ast = resultado['ast']                    # Árbol de sintaxis
tokens = resultado['tokens']              # Lista de tokens
errores = resultado['errores_lexicos']    # Errores encontrados
resumen = resultado['resumen']            # Resumen del análisis

# Mostrar AST
for linea in ast.preorder_lines():
    print(linea)
```

### Método 2: Flujo Paso a Paso

```python
from lector_olympiac import (
    leer_archivo_olympiac,
    enviar_a_explorador,
    enviar_a_analizador_sintactico
)

# Paso 1: Leer archivo
lineas = leer_archivo_olympiac("ejemplo1.oly")

# Paso 2: Enviar al explorador (léxico)
tokens, analizador = enviar_a_explorador(lineas)

# Paso 3: Enviar al analizador sintáctico
ast = enviar_a_analizador_sintactico(tokens)
```

### Método 3: Desde Línea de Comandos

```bash
# Procesar archivo y mostrar resultado
python lector_olympiac.py ejemplo1.oly

# Ejecutar ejemplos de demostración
python ejemplo_flujo.py
```

## 🧪 Ejecutar Tests

```bash
# Tests del analizador léxico
python test_explorador.py

# Tests del analizador sintáctico
python -m pytest test_analizador_sintactico.py
```

## 📝 Ejemplo de Código Olympiac

```olympiac
; Programa de gestion deportiva basico
Deportista atleta1 25 80 75 Futbol Argentina
Deportista atleta2 28 85 78 Basquet Brasil
Lista Deportista competidores

si Comparar(atleta1, atleta2) > 0 entonces {
    narrar(atleta1)
} sino {
    narrar(atleta2)
} endif

Repetir(3) [
    input(entrenamiento)
    narrar(progreso)
] FinRep
```

## 🔍 Componentes del Lenguaje

### Tipos de Tokens Reconocidos

- **Comentarios**: Líneas que inician con `;`
- **Declaraciones**: `Deportista`, `Lista`
- **Tipos de Dato**: `Pais`, `Deporte`, `Resultado`
- **Control de Flujo**: `si`, `entonces`, `sino`, `endif`, `Repetir`, `RepetirHasta`
- **Funciones**: `narrar()`, `Comparar()`, `input()`
- **Operadores Aritméticos**: `+`, `-`, `*`, `/`, `%`
- **Operadores de Comparación**: `==`, `!=`, `>`, `<`, `>=`, `<=`
- **Identificadores**: Nombres de variables y entidades
- **Números**: Enteros y decimales
- **Símbolos**: `(`, `)`, `{`, `}`, `[`, `]`, `,`, `;`, etc.

### Estructuras Sintácticas

- **Declaración de Deportista**: `Deportista nombre edad fuerza velocidad deporte pais`
- **Listas**: `Lista TipoElemento nombreLista`
- **Condicionales**: `si condicion entonces { ... } sino { ... } endif`
- **Bucles**: `Repetir(n) [ ... ] FinRep`
- **Bucles Condicionales**: `RepetirHasta(condicion) [ ... ] FinRepHast`

## 👥 Autores

- Kevin Núñez
- Axel López
- Felipe Murillo
- Joseph Arrieta
- Arturo Chavarría

## 📅 Versión

- **Fecha**: Octubre 2025
- **Versión**: 2.0

## 📄 Licencia

Proyecto académico - Universidad [Nombre Universidad]