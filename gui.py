import tkinter as tk
from tkinter import ttk, messagebox
from ll1 import parse_grammar, compute_first_sets, compute_follow_sets, generate_ll1_table

def display_results():
    grammar_text = grammar_input.get("1.0", tk.END).strip()
    if not grammar_text:
        messagebox.showwarning("Input Error", "Please enter grammar rules.")
        return

    rules = [line.strip() for line in grammar_text.splitlines() if line.strip()]
    grammar, start_symbol = parse_grammar(rules)
    first, first_steps = compute_first_sets(grammar)
    follow, follow_steps = compute_follow_sets(grammar, start_symbol, first)
    table, conflicts, table_steps = generate_ll1_table(grammar, first, follow)

    if conflicts:
        msg = ""
        for nt, term, prev, curr in conflicts:
            msg += f"Conflict in table[{nt}][{term}]: {' '.join(prev)} vs {' '.join(curr)}\n"
        messagebox.showwarning("Conflict", f"Grammar is not LL(1):\n{msg}")

    for tree in [first_tree, follow_tree, parsing_tree]:
        for item in tree.get_children():
            tree.delete(item)

    for nt in [start_symbol] + [k for k in grammar if k != start_symbol]:
        values = first.get(nt, set())
        pretty = ["ε" if x == "e" else x for x in sorted(values)]
        first_tree.insert("", "end", values=(nt, ", ".join(pretty)))

    for nt in [start_symbol] + [k for k in grammar if k != start_symbol]:
        values = follow.get(nt, set())
        pretty = ["ε" if x == "e" else x for x in sorted(values)]
        follow_tree.insert("", "end", values=(nt, ", ".join(pretty)))

    all_terminals = set()
    for entry in table.values():
        all_terminals.update(entry.keys())
    all_terminals = sorted(t for t in all_terminals if t != "e") + ["$"]

    columns = ["Non-Terminals"] + all_terminals
    parsing_tree["columns"] = columns
    for col in columns:
        parsing_tree.heading(col, text=col)
        parsing_tree.column(col, width=100, stretch=False)

    for nt in [start_symbol] + [k for k in grammar if k != start_symbol]:
        row = [nt]
        for t in all_terminals:
            prod = table[nt].get(t, [])
            if prod == ['e']:
                row.append("ε")
            else:
                row.append(" ".join(prod))
        parsing_tree.insert("", "end", values=row)

    explanation_output.delete("1.0", tk.END)
    explanation_output.insert("1.0", "--- FIRST Set Computation Steps ---\n" + "\n".join(first_steps) + "\n\n")
    explanation_output.insert(tk.END, "--- FOLLOW Set Computation Steps ---\n" + "\n".join(follow_steps) + "\n\n")
    explanation_output.insert(tk.END, "--- Parsing Table Construction ---\n" + "\n".join(table_steps))

def clear_input():
    grammar_input.delete("1.0", tk.END)
    explanation_output.delete("1.0", tk.END)

root = tk.Tk()
root.title("LL(1) Parser Generator")
root.geometry("1000x800")

main = ttk.Frame(root)
main.pack(fill="both", expand=True, padx=10, pady=10)

instructions = """
Instructions:
1. Enter grammar productions line by line (e.g., S -> A B).
2. Use 'e' to denote epsilon (ε).
3. Click 'Generate Parsing Table' to compute FIRST, FOLLOW sets and the LL(1) Parsing Table.
"""
ttk.Label(main, text=instructions, foreground="blue", wraplength=900, justify="left").pack(anchor="w")

ttk.Label(main, text="Enter Grammar (use 'e' for ε):").pack(anchor="w")
grammar_input = tk.Text(main, height=8, font=("Consolas", 10))
grammar_input.pack(fill="x", pady=(0, 10))
grammar_input.insert("1.0", "S -> A B C\nA -> a | e\nB -> b | e\nC -> c")

buttons = ttk.Frame(main)
buttons.pack(pady=5)
ttk.Button(buttons, text="Generate Parsing Table", command=display_results).pack(side="left", padx=5)
ttk.Button(buttons, text="Clear Input", command=clear_input).pack(side="left", padx=5)

# Create PanedWindow to split tabs and explanation
paned = tk.PanedWindow(main, orient=tk.VERTICAL, sashrelief=tk.RAISED)
paned.pack(fill="both", expand=True, pady=10)

# Tabs Section
tabs = ttk.Notebook(paned)
paned.add(tabs, stretch="always")

# FIRST Tab
first_tab = ttk.Frame(tabs)
tabs.add(first_tab, text="FIRST Sets")
first_tree = ttk.Treeview(first_tab, columns=("Non-Terminal", "FIRST"), show="headings")
first_tree.heading("Non-Terminal", text="Non-Terminal")
first_tree.heading("FIRST", text="FIRST")
first_tree.pack(fill="both", expand=True, padx=5, pady=5)

# FOLLOW Tab
follow_tab = ttk.Frame(tabs)
tabs.add(follow_tab, text="FOLLOW Sets")
follow_tree = ttk.Treeview(follow_tab, columns=("Non-Terminal", "FOLLOW"), show="headings")
follow_tree.heading("Non-Terminal", text="Non-Terminal")
follow_tree.heading("FOLLOW", text="FOLLOW")
follow_tree.pack(fill="both", expand=True, padx=5, pady=5)

# Parsing Table Tab
table_tab = ttk.Frame(tabs)
tabs.add(table_tab, text="Parsing Table")
parsing_tree = ttk.Treeview(table_tab, show="headings")
parsing_tree.pack(fill="both", expand=True, padx=5, pady=5)

# Explanation section
explanation_frame = ttk.LabelFrame(paned, text="Step-by-step Explanation")
paned.add(explanation_frame, stretch="always")

explanation_output = tk.Text(explanation_frame, wrap="word", font=("Consolas", 10))
explanation_output.pack(fill="both", expand=True, padx=5, pady=5)

root.mainloop()
