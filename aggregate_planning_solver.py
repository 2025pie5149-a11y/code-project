"""
Aggregate Planning Solver - Trial and Error Method
Problem 32: Children's Toy Robot (4-month planning horizon)

Run:  python aggregate_planning_solver.py
"""

from itertools import product as iterproduct

# ─────────────────────────────────────────────
# GIVEN DATA
# ─────────────────────────────────────────────
HOURS_PER_DAY   = 8
TIME_PER_UNIT   = 5 / 3          # 1 hr 40 min = 5/3 hrs
INITIAL_INV     = 600
TARGET_END_INV  = 800
INITIAL_WORKERS = 35
HIRING_COST     = 350            # $ per worker hired
FIRING_COST     = 850            # $ per worker fired
HOLDING_COST    = 4              # $ per unit held per month

MONTHS     = ["July", "August", "September", "October"]
WORKDAYS   = [23, 16, 20, 22]
DEMAND     = [3825, 7245, 2770, 4440]


def evaluate_plan(workers_per_month: list, allow_stockout: bool = False):
    inventory    = INITIAL_INV
    prev_workers = INITIAL_WORKERS
    total_cost   = 0
    details      = []

    for i, (month, days, demand, workers) in enumerate(
        zip(MONTHS, WORKDAYS, DEMAND, workers_per_month)
    ):
        production = workers * days * HOURS_PER_DAY / TIME_PER_UNIT
        hired  = max(0, workers - prev_workers)
        fired  = max(0, prev_workers - workers)
        inventory += production - demand

        if not allow_stockout and inventory < 0:
            return None
        if i == len(MONTHS) - 1 and inventory < TARGET_END_INV:
            return None

        hold_cost  = max(0, inventory) * HOLDING_COST
        hire_cost  = hired * HIRING_COST
        fire_cost  = fired * FIRING_COST
        month_cost = hold_cost + hire_cost + fire_cost
        total_cost += month_cost

        details.append({
            "Month":         month,
            "Workdays":      days,
            "Demand":        demand,
            "Workers":       workers,
            "Hired":         hired,
            "Fired":         fired,
            "Production":    round(production, 2),
            "Inventory End": round(inventory, 2),
            "Holding Cost":  round(hold_cost, 2),
            "Hiring Cost":   round(hire_cost, 2),
            "Firing Cost":   round(fire_cost, 2),
            "Month Cost":    round(month_cost, 2),
        })
        prev_workers = workers

    return {"Total Cost": round(total_cost, 2), "Plan": details}


def trial_and_error_search(w_min=35, w_max=80, step=5):
    candidates = range(w_min, w_max + 1, step)
    best_cost  = float("inf")
    best_result = None
    best_workers = None

    for combo in iterproduct(candidates, repeat=len(MONTHS)):
        result = evaluate_plan(list(combo), allow_stockout=False)
        if result and result["Total Cost"] < best_cost:
            best_cost    = result["Total Cost"]
            best_result  = result
            best_workers = list(combo)

    if best_result:
        return {"workers": best_workers, **best_result}
    return None


def print_plan(label, solution):
    print(f"\n{'='*68}")
    print(f"  {label}")
    print(f"  Workers: {solution['workers']}")
    print(f"  Total Cost: ${solution['Total Cost']:,.2f}")
    print(f"{'='*68}")
    hdr = ["Month","Workers","Prod","Inv End","Hired","Fired","Hold$","Hire$","Fire$","Mo Cost"]
    fmt = "{:<11}{:>8}{:>9}{:>9}{:>7}{:>7}{:>8}{:>8}{:>8}{:>10}"
    print(fmt.format(*hdr))
    print("-"*90)
    for r in solution["Plan"]:
        print(fmt.format(r["Month"],r["Workers"],f"{r['Production']:,.0f}",
            f"{r['Inventory End']:,.0f}",r["Hired"],r["Fired"],
            f"${r['Holding Cost']:,.0f}",f"${r['Hiring Cost']:,.0f}",
            f"${r['Firing Cost']:,.0f}",f"${r['Month Cost']:,.0f}"))
    print("-"*90)
    print(f"{'':>73} ${solution['Total Cost']:>9,.2f}")


if __name__ == "__main__":
    # 1. Reproduce Excel plan (stockout permitted)
    xlsx = evaluate_plan([50,45,55,45], allow_stockout=True)
    print_plan("EXCEL SOLVER PLAN [50,45,55,45]  (Note: Aug has stockout of ~1494)", {"workers":[50,45,55,45],**xlsx})

    # 2. Coarse search (fast)
    print("\nSearching for optimal FEASIBLE plan (step=5 workers)...")
    opt5 = trial_and_error_search(w_min=35, w_max=80, step=5)
    if opt5:
        print_plan("TRIAL-AND-ERROR OPTIMAL (step=5)", opt5)

    # 3. Fine search (may take ~10 sec)
    print("\nFine-grained search (step=1, range 45-75)...")
    opt1 = trial_and_error_search(w_min=45, w_max=75, step=1)
    if opt1:
        print_plan("FINE-GRAINED OPTIMAL (step=1)", opt1)
