"""Spend log and monthly budget guard. Every paid call is one row in <dir>/spend.csv."""
import csv, os


def path(proj):
    return proj.p("spend.csv")


def price(proj, model, size):
    tier = "flash" if "flash" in model else "pro"
    return float(proj.cfg["prices_usd"].get(f"{tier} {size}", 0.24))


def month_total(proj):
    f = path(proj)
    if not os.path.exists(f):
        return 0.0
    month = proj.now().strftime("%Y-%m")
    return sum(float(r.get("est_usd") or 0) for r in csv.DictReader(open(f)) if r.get("time", "").startswith(month))


def guard(proj, est, over_budget=False, dry_run=False):
    """Stop before a run that would cross the monthly budget, unless the approver said go over."""
    budget = float(proj.cfg.get("budget_usd_month") or 0)
    spent = month_total(proj)
    if budget and spent + est > budget and not over_budget:
        msg = (f"this run (about ${est:.2f}) would take the month to ${spent + est:.2f}, over the ${budget:.2f} budget. "
               f"Ask {proj.cfg['approver']} and pass --over-budget with a yes.")
        if dry_run:
            print("warning:", msg)
        else:
            from .config import die
            die(msg)
    return spent


def log(proj, model, size, what, approval=""):
    f = path(proj)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    new = not os.path.exists(f)
    with open(f, "a", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["time", "model", "size", "what", "est_usd", "approval"])
        w.writerow([proj.now().strftime("%Y-%m-%d %H:%M"), model, size, what, f"{price(proj, model, size):.3f}", approval])
