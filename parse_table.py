"""
Construcción de la tabla de análisis sintáctico predictivo M[A, a].
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Mapping, MutableMapping, Optional, Set, Tuple

from grammar import EPSILON, Grammar, Production
from first_follow import first_of_sequence


TableKey = Tuple[str, str]  # (nonterminal, terminal o $)


@dataclass
class ParseTable:

    grammar: Grammar
    entries: Dict[TableKey, Tuple[Production, ...]]
    conflicts: List[Tuple[str, str, Tuple[Production, ...]]] = field(default_factory=list)

    def get(self, nt: str, term: str) -> Tuple[Production, ...]:
        return self.entries.get((nt, term), ())

    def is_ll1(self) -> bool:
        return len(self.conflicts) == 0


def build_parse_table(
    grammar: Grammar,
    first_nt: Mapping[str, FrozenSet[str]],
    follow_nt: Mapping[str, FrozenSet[str]],
) -> ParseTable:
    """
    Para A -> α:
    - Para cada a ∈ FIRST(α) - {ε}, poner A -> α en M[A, a].
    - Si ε ∈ FIRST(α), para cada b ∈ FOLLOW(A), poner A -> α en M[A, b].
    """
    entries: MutableMapping[TableKey, List[Production]] = {}
    conflicts: List[Tuple[str, str, Tuple[Production, ...]]] = []

    # Columnas: terminales + $
    for prod in grammar.productions:
        A = prod.left
        alpha = prod.right
        first_alpha = first_of_sequence(alpha, first_nt, grammar)

        for a in first_alpha - {EPSILON}:
            _add_entry(entries, conflicts, A, a, prod)

        if EPSILON in first_alpha:
            for b in follow_nt[A]:
                _add_entry(entries, conflicts, A, b, prod)

    frozen: Dict[TableKey, Tuple[Production, ...]] = {
        k: tuple(v) for k, v in entries.items()
    }
    return ParseTable(grammar=grammar, entries=frozen, conflicts=conflicts)


def _add_entry(
    entries: MutableMapping[TableKey, List[Production]],
    conflicts: List[Tuple[str, str, Tuple[Production, ...]]],
    A: str,
    col: str,
    prod: Production,
) -> None:
    key = (A, col)
    if key not in entries:
        entries[key] = [prod]
        return
    existing = entries[key]
    if prod not in existing:
        existing.append(prod)
        conflicts.append((A, col, tuple(existing)))
