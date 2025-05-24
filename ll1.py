import re
from collections import defaultdict, OrderedDict

EPSILON = "e"
START_SYMBOL = ""

def parse_grammar(rules):
    global START_SYMBOL
    grammar = OrderedDict()

    for rule in rules:
        parts = re.match(r"(.*?)\s*->\s*(.+)", rule)
        if parts:
            lhs = parts.group(1).strip()
            rhs = parts.group(2).strip()
            if START_SYMBOL == "":
                START_SYMBOL = lhs
            alternatives = rhs.split('|')
            for alt in alternatives:
                symbols = alt.strip().replace(EPSILON, "e").split()
                grammar.setdefault(lhs, []).append(symbols)

    return grammar, START_SYMBOL

def compute_first_sets(grammar):
    explanation = []
    first = defaultdict(set)
    terminals = set()
    non_terminals = set(grammar.keys())

    for rules in grammar.values():
        for prod in rules:
            for sym in prod:
                if sym not in non_terminals and sym != EPSILON:
                    terminals.add(sym)

    for t in terminals:
        first[t] = {t}
    first[EPSILON] = {EPSILON}

    changed = True
    while changed:
        changed = False
        for lhs in grammar:
            for prod in grammar[lhs]:
                explanation.append(f"Checking FIRST({lhs}) from production {lhs} -> {' '.join(prod)}")
                for sym in prod:
                    add_set = first[sym] - {EPSILON}
                    if not add_set.issubset(first[lhs]):
                        first[lhs].update(add_set)
                        explanation.append(f"Added FIRST({sym}) - {{ε}} = {add_set} to FIRST({lhs})")
                        changed = True
                    if EPSILON not in first[sym]:
                        break
                else:
                    if EPSILON not in first[lhs]:
                        first[lhs].add(EPSILON)
                        explanation.append(f"Added ε to FIRST({lhs}) since all symbols can derive ε")
                        changed = True
    return dict(first), explanation

def first_of_sequence(seq, first_sets):
    result = set()
    for symbol in seq:
        result.update(first_sets[symbol] - {EPSILON})
        if EPSILON not in first_sets[symbol]:
            break
    else:
        result.add(EPSILON)
    return result

def compute_follow_sets(grammar, start, first_sets):
    explanation = []
    follow = {nt: set() for nt in grammar}
    follow[start].add("$")
    explanation.append(f"Added $ to FOLLOW({start}) since it's the start symbol")
    changed = True
    while changed:
        changed = False
        for lhs in grammar:
            for prod in grammar[lhs]:
                for i, B in enumerate(prod):
                    if B not in grammar:
                        continue
                    after_B = prod[i+1:]
                    first_beta = first_of_sequence(after_B, first_sets)
                    before_update = follow[B].copy()
                    follow[B].update(first_beta - {EPSILON})
                    if first_beta - {EPSILON}:
                        explanation.append(f"Added FIRST({after_B}) - {{ε}} = {first_beta - {EPSILON}} to FOLLOW({B})")
                    if EPSILON in first_beta:
                        follow[B].update(follow[lhs])
                        explanation.append(f"Since FIRST({after_B}) contains ε, added FOLLOW({lhs}) = {follow[lhs]} to FOLLOW({B})")
                    if follow[B] != before_update:
                        changed = True
    return follow, explanation

def generate_ll1_table(grammar, first, follow):
    table = {nt: {} for nt in grammar}
    explanation = []
    conflicts = []
    for lhs in grammar:
        for prod in grammar[lhs]:
            prod_first = first_of_sequence(prod, first)
            for term in prod_first - {EPSILON}:
                if term in table[lhs]:
                    conflicts.append((lhs, term, table[lhs][term], prod))
                table[lhs][term] = prod
                explanation.append(f"From FIRST({prod}) added {lhs} → {' '.join(prod)} to table[{lhs}][{term}]")
            if EPSILON in prod_first:
                for term in follow[lhs]:
                    if term in table[lhs]:
                        conflicts.append((lhs, term, table[lhs][term], prod))
                    table[lhs][term] = prod
                    explanation.append(f"From FOLLOW({lhs}) (ε in FIRST) added {lhs} → {' '.join(prod)} to table[{lhs}][{term}]")
    return table, conflicts, explanation
