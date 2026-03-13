#!/usr/bin/env python3
"""Run schema and seed SQL, then perform basic CRUD checks against sqlite."""

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "test_hbnb.db"
SCHEMA = ROOT / "sql" / "schema.sql"
SEED = ROOT / "sql" / "seed.sql"

if DB.exists():
    DB.unlink()

conn = sqlite3.connect(str(DB))
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()

print("Applying schema...")
with open(SCHEMA, "r") as f:
    cur.executescript(f.read())

print("Applying seed...")
with open(SEED, "r") as f:
    cur.executescript(f.read())

print("Counts:")
for tbl in ("users", "places", "reviews", "amenities", "place_amenity"):
    cur.execute(f"SELECT COUNT(*) FROM {tbl}")
    print(f"  {tbl}:", cur.fetchone()[0])

print("Create a place by admin user...")
cur.execute(
    (
        "INSERT INTO places (id, name, description, number_rooms, number_bathrooms, "
        "max_guest, price_by_night, latitude, longitude, user_id, created_at, "
        "updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,datetime('now'),datetime('now'))"
    ),
    (
        "place-1",
        "Admin House",
        "Nice place",
        3,
        2,
        5,
        100,
        40.0,
        -74.0,
        "user-admin-1",
    ),
)
conn.commit()

cur.execute("SELECT id, name, user_id FROM places WHERE id = 'place-1'")
print("  inserted place:", cur.fetchone())

print("Associate an amenity to the place...")
cur.execute(
    "INSERT INTO place_amenity (place_id, amenity_id) VALUES (?,?)",
    ("place-1", "amenity-1"),
)
conn.commit()
cur.execute("SELECT amenity_id FROM place_amenity WHERE place_id = ?", ("place-1",))
print("  amenities for place-1:", [r[0] for r in cur.fetchall()])

print("Create a review by admin user...")
cur.execute(
    (
        "INSERT INTO reviews (id, user_id, place_id, text, created_at, updated_at) "
        "VALUES (?,?,?,?,datetime('now'),datetime('now'))"
    ),
    ("review-1", "user-admin-1", "place-1", "Great stay!"),
)
conn.commit()
cur.execute("SELECT id, text FROM reviews WHERE place_id = ?", ("place-1",))
print("  reviews for place-1:", cur.fetchall())

print("Update place price...")
cur.execute("UPDATE places SET price_by_night = ? WHERE id = ?", (120, "place-1"))
conn.commit()
cur.execute("SELECT price_by_night FROM places WHERE id = 'place-1'")
print("  updated price:", cur.fetchone()[0])

print("Delete review...")
cur.execute("DELETE FROM reviews WHERE id = ?", ("review-1",))
conn.commit()
cur.execute("SELECT COUNT(*) FROM reviews WHERE id = 'review-1'")
print("  review count after delete:", cur.fetchone()[0])

conn.close()
print("Done.")
