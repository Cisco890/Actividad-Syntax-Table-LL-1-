"""
Representación formal de una gramática G = (V, T, P, S).

Símbolos especiales:
- EPSILON: cadena vacía (ε)
- END_MARKER: fin de entrada ($)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import FrozenSet, List, Sequence, Tuple

EPSILON = "\u03b5"  # ε
END_MARKER = "$"


@dataclass(frozen=True)
class Production:
    """Producción A -> α como tupla inmutable de símbolos en el lado derecho."""

    left: str
    right: Tuple[str, ...]
    index: int = 0

    def __str__(self) -> str:
        rhs = " ".join(symbol_display(s) for s in self.right)
        return f"{self.left} -> {rhs}"


def symbol_display(sym: str) -> str:
    if sym == EPSILON:
        return "ε"
    return sym


@dataclass
class Grammar:
    """
    Gramática libre de contexto.

    - nonterminals (V): símbolos que aparecen al menos una vez en el LHS.
    - terminals (T): símbolos que aparecen en producciones y no están en V,
      excluyendo ε.
    - start: símbolo inicial (LHS de la primera producción).
    """

    nonterminals: FrozenSet[str]
    terminals: FrozenSet[str]
    productions: Tuple[Production, ...]
    start: str
    _nt_order: Tuple[str, ...] = field(default_factory=tuple)

    @property
    def ordered_nonterminals(self) -> Tuple[str, ...]:
        return self._nt_order if self._nt_order else tuple(sorted(self.nonterminals))


def _normalize_epsilon_token(tok: str) -> str:
    t = tok.strip()
    if t == "ε" or t.lower() in {"epsilon", "eps"}:
        return EPSILON
    return t


def _tokenize_alternative(alt: str) -> Tuple[str, ...]:
    if not alt.strip():
        return (EPSILON,)
    parts = alt.strip().split()
    return tuple(_normalize_epsilon_token(p) for p in parts)


def _parse_production_line(line: str) -> Tuple[str, List[Tuple[str, ...]]]:
    m = re.match(r"^\s*(\S+)\s*->\s*(.+)\s*$", line)
    if not m:
        raise ValueError(f"Línea de producción inválida: {line!r}")
    left = m.group(1).strip()
    rest = m.group(2)
    alternatives: List[Tuple[str, ...]] = []
    for part in rest.split("|"):
        alternatives.append(_tokenize_alternative(part))
    return left, alternatives


def parse_grammar(text: str) -> Grammar:
    """
    Parsea texto con producciones del estilo::

        E  -> T E'
        E' -> + T E' | ε

    """
    raw_lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not raw_lines:
        raise ValueError("La gramática está vacía.")

    lefts: List[str] = []
    rhs_lists: List[List[Tuple[str, ...]]] = []

    for line in raw_lines:
        left, alts = _parse_production_line(line)
        lefts.append(left)
        rhs_lists.append(alts)

    nonterminals = frozenset(lefts)
    if len(nonterminals) != len(set(lefts)):
        raise ValueError("Un mismo no terminal aparece en más de una línea como LHS; "
                         "use alternativas con | en una sola línea.")

    # Conjunto de todos los símbolos en RHS
    all_rhs_syms: List[str] = []
    for alts in rhs_lists:
        for alt in alts:
            all_rhs_syms.extend(s for s in alt if s != EPSILON)

    terminals: FrozenSet[str] = frozenset(
        s for s in all_rhs_syms if s not in nonterminals
    )

    productions: List[Production] = []
    idx = 0
    for left, alts in zip(lefts, rhs_lists):
        for alt in alts:
            _validate_rhs(left, alt, nonterminals, terminals)
            productions.append(Production(left=left, right=alt, index=idx))
            idx += 1

    start = lefts[0]
    nt_order = tuple(dict.fromkeys(lefts))  # orden de primera aparición

    return Grammar(
        nonterminals=nonterminals,
        terminals=terminals,
        productions=tuple(productions),
        start=start,
        _nt_order=nt_order,
    )


def _validate_rhs(
    left: str,
    rhs: Sequence[str],
    nonterminals: FrozenSet[str],
    terminals: FrozenSet[str],
) -> None:
    for sym in rhs:
        if sym == EPSILON:
            continue
        if sym in nonterminals or sym in terminals:
            continue
        raise ValueError(
            f"Símbolo {sym!r} en producción {left} -> ... no es terminal ni no terminal conocido."
        )


def grammar_to_string(g: Grammar) -> str:
    from collections import defaultdict

    by_left: dict[str, List[Tuple[str, ...]]] = defaultdict(list)
    order: List[str] = []
    for p in g.productions:
        if p.left not in order:
            order.append(p.left)
        by_left[p.left].append(p.right)

    lines: List[str] = []
    for left in order:
        alts_str = " | ".join(
            " ".join(symbol_display(s) for s in alt) if alt != (EPSILON,) else "ε"
            for alt in by_left[left]
        )
        lines.append(f"{left} -> {alts_str}")
    return "\n".join(lines)
