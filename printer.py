"""
Salida legible: FIRST, FOLLOW, tabla LL(1), pasos del parser.
"""

from __future__ import annotations

from typing import Dict, FrozenSet, List, Mapping, Tuple

from grammar import Grammar, grammar_to_string, symbol_display
from parse_table import ParseTable
from predictive_parser import ParseResult


def format_first(first: Mapping[str, FrozenSet[str]], g: Grammar) -> str:
    lines: List[str] = []
    for nt in g.ordered_nonterminals:
        fs = first[nt]
        inner = ", ".join(symbol_display(x) for x in sorted(fs, key=_sort_key))
        lines.append(f"FIRST({nt}) = {{ {inner} }}")
    return "\n".join(lines)


def format_follow(follow: Mapping[str, FrozenSet[str]], g: Grammar) -> str:
    lines: List[str] = []
    for nt in g.ordered_nonterminals:
        fs = follow[nt]
        inner = ", ".join(symbol_display(x) for x in sorted(fs, key=_sort_key))
        lines.append(f"FOLLOW({nt}) = {{ {inner} }}")
    return "\n".join(lines)


def _sort_key(sym: str) -> Tuple[int, str]:
    if sym == "$":
        return (2, sym)
    if sym == "\u03b5":
        return (1, sym)
    return (0, sym)


def format_table(table: ParseTable, g: Grammar) -> str:
    cols: List[str] = sorted(g.terminals | {"$"}, key=_col_order)
    rows = list(g.ordered_nonterminals)

    def cell_str(nt: str, t: str) -> str:
        prods = table.get(nt, t)
        if not prods:
            return ""
        if len(prods) == 1:
            return str(prods[0])
        return " | ".join(str(p) for p in prods)

    col_widths: List[int] = []
    for j, c in enumerate(cols):
        w = len(c)
        for r in rows:
            w = max(w, len(cell_str(r, c)))
        col_widths.append(w)
    row_label_w = max((len(r) for r in rows), default=0)

    lines: List[str] = []
    header_line = "".ljust(row_label_w + 2) + "".join(
        cols[i].ljust(col_widths[i] + 2) for i in range(len(cols))
    )
    lines.append(header_line)
    lines.append("-" * len(header_line))
    for r in rows:
        line = r.ljust(row_label_w + 2)
        for i, c in enumerate(cols):
            line += cell_str(r, c).ljust(col_widths[i] + 2)
        lines.append(line)
    return "\n".join(lines)


def _col_order(sym: str) -> Tuple[int, str]:
    if sym == "$":
        return (1, sym)
    return (0, sym)


def format_ll1_status(table: ParseTable) -> str:
    if table.is_ll1():
        return "Resultado: Sí es LL(1) (sin conflictos en la tabla)."
    lines = ["Resultado: No es LL(1). Conflictos detectados:"]
    seen = set()
    for A, a, prods in table.conflicts:
        key = (A, a)
        if key in seen:
            continue
        seen.add(key)
        plist = " | ".join(str(p) for p in prods)
        lines.append(f"  - Celda M[{A}, {symbol_display(a)}]: {plist}")
    return "\n".join(lines)


def format_parse_trace(result: ParseResult) -> str:
    lines: List[str] = []
    for i, step in enumerate(result.steps, 1):
        stack_str = " ".join(symbol_display(s) for s in reversed(step.stack))
        inp_str = " ".join(symbol_display(s) for s in step.input_tokens)
        lines.append(f"Paso {i}:")
        lines.append(f"  Pila (de arriba abajo): {stack_str}")
        lines.append(f"  Entrada restante: {inp_str}")
        lines.append(f"  Acción: {step.action}")
        lines.append("")
    if result.ok:
        lines.append("Cadena aceptada.")
    else:
        lines.append(f"Cadena rechazada. {result.error_message or ''}")
    return "\n".join(lines).rstrip()


def print_grammar_section(title: str, g: Grammar) -> None:
    print(title)
    print(grammar_to_string(g))
    print()
