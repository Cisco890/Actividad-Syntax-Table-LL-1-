# FIRST, FOLLOW, tabla LL(1) y analizador sintáctico predictivo

Implementación en Python alineada con la teoría estándar de compiladores (Libro del Dragón): gramática `G = (V, T, P, S)`, conjuntos **FIRST** y **FOLLOW** por punto fijo, construcción de la tabla predictiva **M[A,a]**, comprobación **LL(1)** y **simulación del parser no recursivo** (pila + puntero de entrada).

## Cómo ejecutar

Requisitos: Python 3.10+ (recomendado 3.11).

```bash
python main.py
```

Muestra las tres gramáticas de demostración, los conjuntos, la tabla, el resultado LL(1) y, para las gramáticas sin conflictos, trazas del parser.

## Formato de entrada de la gramática

- Una producción por línea: `LHS -> RHS`.
- El **símbolo inicial** es el lado izquierdo de la **primera** línea.
- Varios cuerpos para el mismo no terminal en una sola línea, separados por `|`.
- Los símbolos del lado derecho van **separados por espacios** (cada token es un símbolo: `id`, `+`, `(`, `E'`, etc.).
- La cadena vacía: `ε`, o bien `epsilon` / `eps` (sin distinguir mayúsculas en estos alias).

Ejemplo:

```text
E  -> T E'
E' -> + T E' | ε
F  -> ( E ) | id
```



## Cálculo de FIRST

- Si `X` es terminal, `FIRST(X) = {X}`.
- Si `X` es no terminal, se consideran todas las producciones `X -> α` y se une `FIRST(α)` al conjunto de `X`, hasta **punto fijo**.
- `FIRST(α)` para `α = Y₁…Yₙ`: se añade `FIRST(Y₁)-{ε}`; si `ε ∈ FIRST(Y₁)`, se continúa con `Y₂`, etc.; si todos derivan `ε`, se añade `ε`. La secuencia vacía tiene `FIRST = {ε}`.

## Cálculo de FOLLOW

- `$ ∈ FOLLOW(S)` si `S` es el axioma.
- Para `A -> α B β`: `FIRST(β)-{ε} ⊆ FOLLOW(B)`.
- Si `β =>* ε` (en particular si `β` es vacía): `FOLLOW(A) ⊆ FOLLOW(B)`.
- Iteración hasta **punto fijo**.

## Construcción de la tabla LL(1)

Para cada producción `A -> α`:

1. Para cada `a ∈ FIRST(α) \ {ε}`, se coloca `A -> α` en `M[A, a]`.
2. Si `ε ∈ FIRST(α)`, para cada `b ∈ FOLLOW(A)` se coloca `A -> α` en `M[A, b]`.

La gramática es **LL(1)** si ninguna celda contiene más de una producción. Si se intenta insertar una segunda producción distinta en la misma celda, se registra un **conflicto** (no terminal, terminal y producciones implicadas).

## Analizador predictivo con pila

1. Pila inicial: fondo `$` y **cima** el símbolo inicial `S` (implementación: lista con `stack[-1]` como cima).
2. La entrada es una lista de terminales terminada en `$` (si el usuario no escribe `$`, se añade al final).
3. Sea `X` la cima de la pila y `a` el token actual:
   - Si `X` es terminal: si `X == a`, `pop` y avanzar; si no, **error**.
   - Si `X` es no terminal: si `M[X,a]` está vacío, **error**; si hay una producción `X -> Y₁…Yₖ`, `pop`, empujar `Yₖ … Y₁` (omitiendo `ε`).
4. **Aceptación** cuando cima y entrada son ambos `$`.

## Gramáticas probadas en `main.py`

| Gramática | Rol | Resultado LL(1) |
|-----------|-----|-----------------|
| Expresiones con `E`, `T`, `F`, primas | Obligatoria (libro clásico) | Sí |
| `S -> C C`, `C -> c C \| d` | Ejemplo adicional LL(1) | Sí |
| `S -> a A \| a B`, `A -> a`, `B -> b` | Prefijo común: conflicto en `M[S,a]` | No |

**Por qué estas gramáticas:** la primera es el estándar didáctico; la segunda prueba el mismo pipeline con otra estructura (dos bloques `C`); la tercera muestra explícitamente **dos producciones compitiendo por el mismo terminal en la misma fila**, lo que viola LL(1).

## Cadenas de ejemplo (parser)

- **Expresiones:** `id + id * id` y `( id + id ) * id` se aceptan; `id + * id` y `( id + id` se rechazan (celda vacía o terminal inesperado).
- **Gramática `S -> C C`:** `c c d d` y `c d c d` aceptadas; `c c d` rechazada (falta símbolo para el segundo `C`).

## Estructura del código

| Módulo | Contenido |
|--------|-----------|
| `grammar.py` | Parseo y representación de `G`, producciones, ε y `$` |
| `first_follow.py` | FIRST globales y FIRST de secuencias; FOLLOW iterativo |
| `parse_table.py` | Tabla predictiva y lista de conflictos |
| `predictive_parser.py` | Parser con pila y traza opcional |
| `printer.py` | Formato de salida en texto |
| `main.py` | Demostraciones |


##Link Video

https://youtu.be/rgkZreo4OR4
