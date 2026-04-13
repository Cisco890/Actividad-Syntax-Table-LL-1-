"""
Cálculo de FIRST y FOLLOW 
"""

from __future__ import annotations

from typing import Dict, FrozenSet, Mapping, MutableMapping, Set, Tuple

from grammar import EPSILON, Grammar


def first_of_sequence(
    alpha: Tuple[str, ...],
    first_nt: Mapping[str, FrozenSet[str]],
    grammar: Grammar,
) -> FrozenSet[str]:
    """
    FIRST(α) para α = X₁ X₂ ... Xₙ.

    Si α es vacía, FIRST(α) = {ε}.
    """
    if not alpha or alpha == (EPSILON,):
        return frozenset({EPSILON})

    result: Set[str] = set()
    for i, sym in enumerate(alpha):
        if sym == EPSILON:
            # ε en medio de secuencia
            if len(alpha) == 1:
                return frozenset({EPSILON})
            raise ValueError(f"ε en posición no válida dentro de la secuencia: {alpha!r}")

        if sym in grammar.terminals:
            result.add(sym)
            return frozenset(result)

        # No terminal
        fi = set(first_nt.get(sym, frozenset()))
        result |= fi - {EPSILON}
        if EPSILON not in fi:
            return frozenset(result)

    # Todos los símbolos derivan ε
    result.add(EPSILON)
    return frozenset(result)


def compute_first(grammar: Grammar) -> Dict[str, FrozenSet[str]]:
    """
    Calcula FIRST(A) para cada no terminal A
    """
    first: Dict[str, Set[str]] = {a: set() for a in grammar.nonterminals}

    changed = True
    while changed:
        changed = False
        for prod in grammar.productions:
            rhs = prod.right
            # A -> ε
            if rhs == (EPSILON,) or (len(rhs) == 1 and rhs[0] == EPSILON):
                if EPSILON not in first[prod.left]:
                    first[prod.left].add(EPSILON)
                    changed = True
                continue

            seq_first = first_of_sequence(rhs, {k: frozenset(v) for k, v in first.items()}, grammar)
            before = first[prod.left].copy()
            first[prod.left] |= set(seq_first)
            if first[prod.left] != before:
                changed = True

    return {k: frozenset(v) for k, v in first.items()}


def compute_follow(
    grammar: Grammar,
    first_nt: Mapping[str, FrozenSet[str]],
) -> Dict[str, FrozenSet[str]]:
    """
    FOLLOW(A) iterativo

    - $ ∈ FOLLOW(S)
    - A -> α B β  =>  FIRST(β)-{ε} ⊆ FOLLOW(B)
    - A -> α B o β =>* ε  =>  FOLLOW(A) ⊆ FOLLOW(B)
    """
    follow: Dict[str, Set[str]] = {a: set() for a in grammar.nonterminals}
    follow[grammar.start].add("$")

    changed = True
    while changed:
        changed = False
        for prod in grammar.productions:
            A = prod.left
            rhs = prod.right
            if rhs == (EPSILON,):
                continue

            for i, B in enumerate(rhs):
                if B not in grammar.nonterminals:
                    continue
                beta = rhs[i + 1 :]
                first_beta = first_of_sequence(beta, first_nt, grammar)

                before = follow[B].copy()
                follow[B] |= first_beta - {EPSILON}
                if EPSILON in first_beta or not beta:
                    follow[B] |= follow[A]
                if follow[B] != before:
                    changed = True

    return {k: frozenset(v) for k, v in follow.items()}


def first_follow_sets(grammar: Grammar) -> Tuple[Dict[str, FrozenSet[str]], Dict[str, FrozenSet[str]]]:
    """Calcula FIRST y FOLLOW para toda la gramática."""
    first_nt = compute_first(grammar)
    follow_nt = compute_follow(grammar, first_nt)
    return first_nt, follow_nt
