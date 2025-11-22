# Documentación: Verificador Semántico — Proyecto_Compi

Resumen
- El verificador recorre el ASA (Árbol de Sintaxis Abstracta) generado por el parser y realiza comprobaciones semánticas:
  - Verificación de identificadores (declaración antes de uso, duplicados).
  - Inferencia de tipos básica y comprobaciones (p. ej. evitar suma de texto + número).
  - Registro de errores en formato legible.
  - Decoración del ASA: cada nodo puede recibir metadatos (tipo inferido, referencia a definición, arg_types, etc.).
  - Registro de snapshots parciales de la tabla de símbolos cada vez que cambia.

1. Impresión del ASA decorado
- Se imprime en pre-orden (raíz → subárboles).
- Formato por línea (ejemplo):
  - `<"TipoNodo", "Contenido", {...atributos...}>`
  - Si un nodo tiene decoraciones estas se imprimen inmediatamente después como:
    `Decorado: {...}`  
- La impresión distingue claramente la estructura del árbol y la parte decorada — facilita lectura humana.

2. Contenido del JSON exportado (`asa_decorated.json`)
- Estructura principal:
  - `decorations`: mapa node_uid → metadatos (tipo, definición, args_types, ref, method_of, etc.).
  - `errors`: lista de errores semánticos (mensaje, línea, columna, severidad).
  - `snapshots`: lista de snapshots de la tabla de símbolos (timestamp, nodo, línea, copia de la tabla).
- Nota: actualmente las claves de `decorations` usan id(node) de Python (no estable entre ejecuciones). Recomendado: introducir un `uid` estable por nodo si se necesita persistencia reproducible.

Ejemplo corto (extracto de `asa_decorated.json`):
```json
{
  "decorations": {
    "1942730051504": {
      "tipo": "unknown_call",
      "name": "Comparar(",
      "args": ["Mbappe","Jude"],
      "arg_types": ["entity:Deportista","entity:Deportista"]
    }
  },
  "errors": [],
  "snapshots": [
    {
      "when": "2025-11-08T23:54:45.165389",
      "node": "Deportista",
      "line": 5,
      "table": {
        "scope_0": {
          "Kaka": {"type":"entity:Deportista","defined_line":5}
        }
      }
    }
  ]
}
```

3. Verificación de identificadores
- Reglas principales:
  - Cuando se declara una entidad (p. ej. `Deportista X ...`) se añade a la symbol table con tipo `entity:Deportista`.
  - `declare` falla si ya existe en el mismo scope → error por duplicado.
  - `lookup` usado para referencias: si no existe → error "Identificador 'X' usado antes de ser declarado" (se reporta línea/columna).
- Salida de error amigable:
  - Formato: `[ERROR] línea:col - Mensaje` (ej. `[ERROR] 14:3 - Identificador 'progreso' usado antes de ser declarado`).

4. Inferencia de tipos (mínima)
- Literal cadena → `string`.
- Literal numérico → `int` (o `number` según tu preferencia).
- Entidades declaradas → `entity:<Tipo>` (ej. `entity:Deportista`).
- Listas declaradas → `list:<Tipo>`.
- Reglas de comprobación:
  - Operadores binarios: si encuentra `string + int` se reporta error semántico (“suma texto + número”).
  - Llamadas a funciones/builtins: comparador `Comparar` espera `entity, entity` → se valida aridad y tipos de argumentos.
- Decoración: el verificador añade `args_types` y `tipo` al nodo de llamada para inspección.

5. Tabla de símbolos (implementación y uso)
- Estructura:
  - `SymbolTable` soporta scopes anidados; internamente mantiene un diccionario por nivel (`scope_0`, `scope_1`, ...).
- API esencial:
  - `enter_scope()` — crear un nuevo scope.
  - `exit_scope()` — salir al scope padre.
  - `declare(name: str, info: dict)` — declarar un nombre en el scope actual; info incluye `type`, `defined_line`, `scope_level`.
  - `lookup(name: str) -> Optional[dict]` — buscar nombre en scopes (desde el más interno al externo); devuelve info o `None`.
  - `snapshot()` — devuelve una copia (serializable) del estado actual de la tabla (usada para exportar `snapshots`).
- Impresiones parciales:
  - Cada vez que se declara una nueva entidad/lista se registra y se imprime un snapshot con timestamp para facilitar trazabilidad.

6. Pruebas y escenarios
- Cobertura mínima a probar manualmente (sin pytest):
  - Declaración y uso correcto (global): declarar `Deportista A ...` y luego `narrar(A)`.
  - Uso antes de declarar: usar `X` sin declararlo → debe reportar error.
  - Duplicado en mismo scope: declarar `Deportista A` dos veces → error de duplicado.
  - Suma texto+numero: `narrar("hola" + 5)` o una operación binaria que mezcle tipos → error.
  - Scopes anidados: declarar variable en bloque y verificar shadowing y visibilidad.
- Cómo ejecutar (PowerShell desde la raíz del repo):
  - Ejecutar lector (pipeline completo):
    ```
    python .\lector_olympiac.py .\ejemplo_asa.oly
    ```
  - Ejecutar con archivo con errores para ver diagnóstico:
    ```
    python .\run_verifier.py .\ejemplo_errors.oly
    ```
  - Salida esperada:
    - En consola: ASA (pre-order), decoraciones (por nodo) y lista de errores semánticos.
    - Archivo: `asa_decorated.json` con `decorations`, `errors`, `snapshots`.

7. Buenas prácticas y recomendaciones
- Para correlación y herramientas externas: añadir un `uid` estable por nodo en `nodo.asaNode` y usar ese `uid` como clave en `decorations`.
- Separar claramente printing (console) y export (JSON). Usar logger con niveles (`INFO`, `DEBUG`, `ERROR`) para poder controlar la verbosidad.
- Ampliar inferencia de tipos si se introducen más construcciones en la gramática (funciones con tipos de retorno, estructuras).
- Mantener pruebas de ejemplo: uno válido (sin errores), otro sintácticamente válido pero semánticamente erróneo, y otro con errores léxicos/sintácticos para debugging.

8. Mapa rápido de archivos relevantes
- `explorador.py` — analizador léxico.
- `analizador_sintactico.py` — parser que devuelve `asaNode` (ASA).
- `nodo.py` — definición de `asaNode` y `preorder_lines()`.
- `symbol_table.py` — implementación de la tabla de símbolos.
- `verificador.py` — verificador semántico y generador de decoraciones / snapshots.
- `lector_olympiac.py` — flujo completo CLI (lee → lexea → parsea → verifica → imprime / exporta).
- `asa_decorated.json` — salida JSON generada por el verificador (decoraciones, errores, snapshots).

9. Ejemplo rápido de verificación manual
- Caso correcto:
  - `Deportista Kaka 91 80 90 Futbol Francia` → `Kaka` declarado como `entity:Deportista`.
- Caso con error semántico:
  - `narrar("hola" + 5)` → consola: `[ERROR] 12:5 - Operacion invalida: suma entre string e int`
  - JSON: `errors` contiene ese mensaje con línea y columna.

---

Fin del documento.  
Guárdalo como `docs/verifier_documentation.md` y enlázalo desde el README del proyecto para que el equipo lo consulte. Si quieres, implemento la mejora rápida de añadir `uid` estable por nodo (opción recomendada) y actualizo el JSON para que use ese uid en lugar de id(node).
```<!-- filepath: c:\Users\Axel\Documents\Compiladores\github\docs\verifier_documentation.md -->
# Documentación: Verificador Semántico — Proyecto_Compi

Resumen
- El verificador recorre el ASA (Árbol de Sintaxis Abstracta) generado por el parser y realiza comprobaciones semánticas:
  - Verificación de identificadores (declaración antes de uso, duplicados).
  - Inferencia de tipos básica y comprobaciones (p. ej. evitar suma de texto + número).
  - Registro de errores en formato legible.
  - Decoración del ASA: cada nodo puede recibir metadatos (tipo inferido, referencia a definición, arg_types, etc.).
  - Registro de snapshots parciales de la tabla de símbolos cada vez que cambia.

1. Impresión del ASA decorado
- Se imprime en pre-orden (raíz → subárboles).
- Formato por línea (ejemplo):
  - `<"TipoNodo", "Contenido", {...atributos...}>`
  - Si un nodo tiene decoraciones estas se imprimen inmediatamente después como:
    `Decorado: {...}`  
- La impresión distingue claramente la estructura del árbol y la parte decorada — facilita lectura humana.

2. Contenido del JSON exportado (`asa_decorated.json`)
- Estructura principal:
  - `decorations`: mapa node_uid → metadatos (tipo, definición, args_types, ref, method_of, etc.).
  - `errors`: lista de errores semánticos (mensaje, línea, columna, severidad).
  - `snapshots`: lista de snapshots de la tabla de símbolos (timestamp, nodo, línea, copia de la tabla).
- Nota: actualmente las claves de `decorations` usan id(node) de Python (no estable entre ejecuciones). Recomendado: introducir un `uid` estable por nodo si se necesita persistencia reproducible.

Ejemplo corto (extracto de `asa_decorated.json`):
```json
{
  "decorations": {
    "1942730051504": {
      "tipo": "unknown_call",
      "name": "Comparar(",
      "args": ["Mbappe","Jude"],
      "arg_types": ["entity:Deportista","entity:Deportista"]
    }
  },
  "errors": [],
  "snapshots": [
    {
      "when": "2025-11-08T23:54:45.165389",
      "node": "Deportista",
      "line": 5,
      "table": {
        "scope_0": {
          "Kaka": {"type":"entity:Deportista","defined_line":5}
        }
      }
    }
  ]
}
```

3. Verificación de identificadores
- Reglas principales:
  - Cuando se declara una entidad (p. ej. `Deportista X ...`) se añade a la symbol table con tipo `entity:Deportista`.
  - `declare` falla si ya existe en el mismo scope → error por duplicado.
  - `lookup` usado para referencias: si no existe → error "Identificador 'X' usado antes de ser declarado" (se reporta línea/columna).
- Salida de error amigable:
  - Formato: `[ERROR] línea:col - Mensaje` (ej. `[ERROR] 14:3 - Identificador 'progreso' usado antes de ser declarado`).

4. Inferencia de tipos (mínima)
- Literal cadena → `string`.
- Literal numérico → `int` (o `number` según tu preferencia).
- Entidades declaradas → `entity:<Tipo>` (ej. `entity:Deportista`).
- Listas declaradas → `list:<Tipo>`.
- Reglas de comprobación:
  - Operadores binarios: si encuentra `string + int` se reporta error semántico (“suma texto + número”).
  - Llamadas a funciones/builtins: comparador `Comparar` espera `entity, entity` → se valida aridad y tipos de argumentos.
- Decoración: el verificador añade `args_types` y `tipo` al nodo de llamada para inspección.

5. Tabla de símbolos (implementación y uso)
- Estructura:
  - `SymbolTable` soporta scopes anidados; internamente mantiene un diccionario por nivel (`scope_0`, `scope_1`, ...).
- API esencial:
  - `enter_scope()` — crear un nuevo scope.
  - `exit_scope()` — salir al scope padre.
  - `declare(name: str, info: dict)` — declarar un nombre en el scope actual; info incluye `type`, `defined_line`, `scope_level`.
  - `lookup(name: str) -> Optional[dict]` — buscar nombre en scopes (desde el más interno al externo); devuelve info o `None`.
  - `snapshot()` — devuelve una copia (serializable) del estado actual de la tabla (usada para exportar `snapshots`).
- Impresiones parciales:
  - Cada vez que se declara una nueva entidad/lista se registra y se imprime un snapshot con timestamp para facilitar trazabilidad.

6. Pruebas y escenarios
- Cobertura mínima a probar manualmente (sin pytest):
  - Declaración y uso correcto (global): declarar `Deportista A ...` y luego `narrar(A)`.
  - Uso antes de declarar: usar `X` sin declararlo → debe reportar error.
  - Duplicado en mismo scope: declarar `Deportista A` dos veces → error de duplicado.
  - Suma texto+numero: `narrar("hola" + 5)` o una operación binaria que mezcle tipos → error.
  - Scopes anidados: declarar variable en bloque y verificar shadowing y visibilidad.
- Cómo ejecutar (PowerShell desde la raíz del repo):
  - Ejecutar lector (pipeline completo):
    ```
    python .\lector_olympiac.py .\ejemplo_asa.oly
    ```
  - Ejecutar con archivo con errores para ver diagnóstico:
    ```
    python .\run_verifier.py .\ejemplo_errors.oly
    ```
  - Salida esperada:
    - En consola: ASA (pre-order), decoraciones (por nodo) y lista de errores semánticos.
    - Archivo: `asa_decorated.json` con `decorations`, `errors`, `snapshots`.

7. Buenas prácticas y recomendaciones
- Para correlación y herramientas externas: añadir un `uid` estable por nodo en `nodo.asaNode` y usar ese `uid` como clave en `decorations`.
- Separar claramente printing (console) y export (JSON). Usar logger con niveles (`INFO`, `DEBUG`, `ERROR`) para poder controlar la verbosidad.
- Ampliar inferencia de tipos si se introducen más construcciones en la gramática (funciones con tipos de retorno, estructuras).
- Mantener pruebas de ejemplo: uno válido (sin errores), otro sintácticamente válido pero semánticamente erróneo, y otro con errores léxicos/sintácticos para debugging.

8. Mapa rápido de archivos relevantes
- `explorador.py` — analizador léxico.
- `analizador_sintactico.py` — parser que devuelve `asaNode` (ASA).
- `nodo.py` — definición de `asaNode` y `preorder_lines()`.
- `symbol_table.py` — implementación de la tabla de símbolos.
- `verificador.py` — verificador semántico y generador de decoraciones / snapshots.
- `lector_olympiac.py` — flujo completo CLI (lee → lexea → parsea → verifica → imprime / exporta).
- `asa_decorated.json` — salida JSON generada por el verificador (decoraciones, errores, snapshots).

9. Ejemplo rápido de verificación manual
- Caso correcto:
  - `Deportista Kaka 91 80 90 Futbol Francia` → `Kaka` declarado como `entity:Deportista`.
- Caso con error semántico:
  - `narrar("hola" + 5)` → consola: `[ERROR] 12:5 - Operacion invalida: suma entre string e int`
  - JSON: `errors` contiene ese mensaje con línea y columna.

---

Fin del documento.  
Guárdalo como `docs/verifier_documentation.md` y enlázalo desde el README del proyecto para que el equipo lo consulte. Si quieres, implemento la mejora rápida de añadir `uid` estable por nodo (opción recomendada) y actualizo el JSON para que use ese uid en lugar de id(node).