import csv
from html import escape
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent
DIMENSIONS = {"block": "Block", "variety": "Variety", "dose": "nitro"}
QUERY = """
SELECT v.label AS variety, d.label AS dose, count(*) AS plots,
       round(avg(f.yield), 2) AS average_yield,
       min(f.yield) AS minimum, max(f.yield) AS maximum
FROM harvest f JOIN variety v ON v.id = f.variety_id
JOIN dose d ON d.id = f.dose_id
GROUP BY v.id, d.id ORDER BY v.label, CAST(d.label AS REAL)
"""


def build(database, rows):
    with database:
        for name in DIMENSIONS:
            database.execute(f"CREATE TABLE IF NOT EXISTS {name} (id INTEGER PRIMARY KEY, label TEXT UNIQUE NOT NULL)")
        database.execute("""CREATE TABLE IF NOT EXISTS harvest (
            block_id INTEGER REFERENCES block(id), variety_id INTEGER REFERENCES variety(id),
            dose_id INTEGER REFERENCES dose(id), yield REAL NOT NULL,
            PRIMARY KEY (block_id, variety_id, dose_id)
        )""")
        database.execute("DELETE FROM harvest")
        lookups = {}
        for name, field in DIMENSIONS.items():
            labels = sorted({row[field] for row in rows})
            database.executemany(f"INSERT OR IGNORE INTO {name}(label) VALUES (?)", [(x,) for x in labels])
            lookups[name] = {label: key for key, label in database.execute(f"SELECT id,label FROM {name}")}
        database.executemany("INSERT INTO harvest VALUES (?, ?, ?, ?)", [
            (*[lookups[name][row[field]] for name, field in DIMENSIONS.items()], float(row["yield"]))
            for row in rows
        ])
    return database.execute(QUERY).fetchall()


def report(metrics):
    best = max(metrics, key=lambda row: row[3])
    headers = ("Variété", "Dose", "Parcelles", "Moyenne", "Minimum", "Maximum")
    table = "<tr>" + "".join(f"<th>{name}</th>" for name in headers) + "</tr>"
    table += "".join("<tr>" + "".join(f"<td>{escape(str(x))}</td>" for x in row) + "</tr>"
                     for row in metrics)
    return f"""<!doctype html><html lang="fr"><meta charset="utf-8">
<title>Rendements d’avoine</title><style>
body{{font:16px system-ui;max-width:900px;margin:3rem auto;padding:1rem}}
td,th{{padding:.65rem;border-bottom:1px solid #ddd;text-align:left}}
</style><h1>Rendements d’avoine par variété et dose</h1>
<p>72 parcelles, 6 blocs et 12 traitements.</p>
<p>Moyenne observée la plus élevée : {escape(best[0])}, dose {best[1]}, moyenne {best[3]}.</p>
<table>{table}</table>
<p>Analyse descriptive de l’expérience historique Oats. Source : documentation du paquet R nlme.</p></html>"""


if __name__ == "__main__":
    with (ROOT / "Oats.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    with sqlite3.connect(ROOT / "warehouse.sqlite") as database:
        database.execute("PRAGMA foreign_keys=ON")
        metrics = build(database, rows)
    assert len(rows) == 72 and len(metrics) == 12 and all(row[2] == 6 for row in metrics)
    (ROOT / "dashboard.html").write_text(report(metrics), encoding="utf-8")
    print(f"{len(rows)} parcelles, {len(metrics)} traitements. Rapport : dashboard.html")
