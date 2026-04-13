"""
Demostración: tres gramáticas (expresiones, ejemplo LL(1) adicional, no LL(1)).
"""

from __future__ import annotations

import sys


def _ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (OSError, ValueError):
            pass


_ensure_utf8_stdout()

from grammar import parse_grammar
from first_follow import first_follow_sets
from parse_table import build_parse_table
from predictive_parser import parse_string
from printer import (
    format_first,
    format_follow,
    format_ll1_status,
    format_parse_trace,
    format_table,
    print_grammar_section,
)


GRAMMAR_EXPR = """
E  -> T E'
E' -> + T E' | ε
T  -> F T'
T' -> * F T' | ε
F  -> ( E ) | id
"""

# Dos bloques C consecutivos.
GRAMMAR_CC = """
S -> C C
C -> c C | d
"""

# Mismo FIRST para dos alternativas de S.
GRAMMAR_AMBIG = """
S -> a A | a B
A -> a
B -> b
"""


def run_demo(name: str, text: str, strings: list[str] | None = None) -> None:
    print("=" * 72)
    print(name)
    print("=" * 72)
    g = parse_grammar(text)
    print_grammar_section("1) Gramática", g)

    first, follow = first_follow_sets(g)
    print("2) Conjuntos FIRST")
    print(format_first(first, g))
    print()
    print("3) Conjuntos FOLLOW")
    print(format_follow(follow, g))
    print()

    table = build_parse_table(g, first, follow)
    print("4) Tabla de análisis sintáctico predictivo")
    print(format_table(table, g))
    print()
    print("5) Verificación LL(1)")
    print(format_ll1_status(table))
    print()

    if strings and table.is_ll1():
        print("6) Simulación del analizador (tabla LL(1))")
        for s in strings:
            print("-" * 48)
            print(f"Cadena: {s!r}")
            res = parse_string(g, table, s, trace=True)
            print(format_parse_trace(res))
            print()
    elif strings and not table.is_ll1():
        print("6) No se ejecuta el parser con cadenas de ejemplo (tabla con conflictos).")
        print("   Motivo: una tabla LL(1) debe tener a lo sumo una producción por celda.")
        print()


def main() -> None:
    run_demo(
        "Gramática 1 — Expresiones aritméticas",
        GRAMMAR_EXPR,
        [
            "id + id * id",
            "( id + id ) * id",
            "id + * id",
            "( id + id",
        ],
    )

    run_demo(
        "Gramática 2 — Dos bloques C",
        GRAMMAR_CC,
        [
            "c c d d",
            "c d c d",
            "c c d",
        ],
    )

    run_demo(
        "Gramática 3 — Prefijo común ",
        GRAMMAR_AMBIG,
        None,
    )


if __name__ == "__main__":
    main()
