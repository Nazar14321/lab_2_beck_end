from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import text
from .models import db, User, Category, Record

USER_DATA = {
    1: "Vasya",
    2: "Petya",
    3: "Amogusetya",
    4: "Taras",
    5: "Nash Kaban",
}

CATEGORY_DATA = {
    1: "Food & Groceries",
    2: "Transport",
    3: "Utilities",
    4: "Entertainment",
}

RECORDS_DATA = {
    1: {"user_id": 1, "category_id": 1, "datetime": "2025-10-18 09:15:00", "amount": 235.50},
    2: {"user_id": 2, "category_id": 2, "datetime": "2025-10-18 18:40:00", "amount": 120.00},
    3: {"user_id": 3, "category_id": 3, "datetime": "2025-10-19 07:05:12", "amount": 980.75},
    4: {"user_id": 1, "category_id": 4, "datetime": "2025-10-19 12:10:33", "amount": 649.00},
    5: {"user_id": 2, "category_id": 1, "datetime": "2025-10-19 13:22:47", "amount": 89.90},
}

def run_seed(reset: bool = False):
    if reset:
        db.session.execute(
            text("TRUNCATE TABLE records, categories, users RESTART IDENTITY CASCADE")
        )
        db.session.commit()

    for uid, name in USER_DATA.items():
        db.session.merge(User(id=uid, name=name))

    for cid, name in CATEGORY_DATA.items():
        db.session.merge(Category(id=cid, name=name, owner_id=None))

    tz = ZoneInfo("Europe/Kyiv")
    for rid, r in RECORDS_DATA.items():
        dt = datetime.strptime(r["datetime"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
        db.session.merge(
            Record(
                id=rid,
                user_id=r["user_id"],
                category_id=r["category_id"],
                datetime=dt,
                amount=float(r["amount"]),
            )
        )

    db.session.commit()

    for table in ("users", "categories", "records"):
        db.session.execute(text(f"""
            SELECT setval(pg_get_serial_sequence('{table}','id'),
                          COALESCE(MAX(id), 0) + 1, false)
            FROM {table};
        """))
    db.session.commit()