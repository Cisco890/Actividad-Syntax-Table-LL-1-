"""
Analizador sintáctico predictivo no recursivo (pila + tabla LL(1)).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

from grammar import EPSILON, Grammar, Production, symbol_display
from parse_table import ParseTable


@dataclass
class ParseStep:
    stack: List[str]
    input_tokens: List[str]
    action: str
    production: Optional[Production] = None


@dataclass
class ParseResult:
    ok: bool
    steps: List[ParseStep] = field(default_factory=list)
    error_message: Optional[str] = None


def tokenize_input(line: str) -> List[str]:
    parts = [p for p in line.strip().split() if p]
    if not parts:
        return ["$"]
    if parts[-1] != "$":
        parts.append("$")
    return parts


def parse_string(
    grammar: Grammar,
    table: ParseTable,
    input_line: str,
    trace: bool = True,
) -> ParseResult:
    """
    Algoritmo estándar:
    - Pila inicial: [$ , S] con S arriba (último elemento = cima).
    - Entrada con puntero al primer token.
    """
    tokens = tokenize_input(input_line)
    ip = 0
    stack: List[str] = ["$", grammar.start]
    steps: List[ParseStep] = []

    def record(action: str, prod: Optional[Production] = None) -> None:
        if trace:
            steps.append(
                ParseStep(
                    stack=stack.copy(),
                    input_tokens=tokens[ip:],
                    action=action,
                    production=prod,
                )
            )

    while True:
        top = stack[-1]
        a = tokens[ip]

        if top == "$" and a == "$":
            record("aceptar")
            return ParseResult(ok=True, steps=steps)

        if top == "$":
            msg = f"Error: pila vacía ($) pero entrada no consumida (token actual: {a!r})"
            record(msg)
            return ParseResult(ok=False, steps=steps, error_message=msg)

        if top in grammar.terminals:
            if top == a:
                record(f"hacer match con {symbol_display(top)}")
                stack.pop()
                ip += 1
            else:
                msg = (
                    f"Error: se esperaba {symbol_display(top)!r} pero la entrada tiene {a!r}"
                )
                record(msg)
                return ParseResult(ok=False, steps=steps, error_message=msg)
            continue

        # No terminal
        prods = table.get(top, a)
        if not prods:
            msg = f"Error: no hay producción en M[{top}, {a}]"
            record(msg)
            return ParseResult(ok=False, steps=steps, error_message=msg)

        if len(prods) > 1:
            msg = f"Error: conflicto en M[{top}, {a}] (tabla no LL(1) en uso)"
            record(msg)
            return ParseResult(ok=False, steps=steps, error_message=msg)

        prod = prods[0]
        rhs = prod.right
        action = f"aplicar {prod}"
        record(action, prod)
        stack.pop()
        if rhs == (EPSILON,) or (len(rhs) == 1 and rhs[0] == EPSILON):
            continue
        for sym in reversed(rhs):
            if sym != EPSILON:
                stack.append(sym)
