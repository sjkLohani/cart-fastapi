import os
import random
import time

from sqlalchemy import MetaData, create_engine, func, select

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable is missing.")
    exit(1)

print("🔗 Connecting to cloud MySQL instance...")
engine = create_engine(DATABASE_URL)
metadata = MetaData()


def seed_database():
    start_time = time.time()
    metadata.reflect(bind=engine)

    required = ["products", "carts", "cart_items"]
    if not all(t in metadata.tables for t in required):
        print("Error: Core tables missing.")
        return

    tables = {t: metadata.tables[t] for t in required}

    # Lowered chunk size to accommodate 1GB RAM limits perfectly
    BATCH_SIZE = 10000

    # -------------------------------------------------------------
    # PHASE 1: SEED 100,000 PRODUCTS (Micro-Transactions)
    # -------------------------------------------------------------
    print("Phase 1: Injecting 100,000 products...")
    for i in range(0, 100000, BATCH_SIZE):
        p_batch = [
            {"name": f"Product-SKU-{idx}", "current_price": float((idx % 150) + 4.99)}
            for idx in range(i, i + BATCH_SIZE)
        ]
        # Open a fresh connection per chunk, execute, and auto-commit instantly
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(tables["products"].insert(), p_batch)
        print(f"Products Chunk: Loaded rows {i} to {i + BATCH_SIZE}")

    # Capture boundaries
    with engine.connect() as connection:
        min_p = (
            connection.execute(select(func.min(tables["products"].c.id))).scalar() or 1
        )
        max_p = (
            connection.execute(select(func.max(tables["products"].c.id))).scalar()
            or 100000
        )

    # -------------------------------------------------------------
    # PHASE 2: SEED 300,000 CARTS (Micro-Transactions with Logging)
    # -------------------------------------------------------------
    print("\nPhase 2: Injecting 300,000 carts...")
    statuses = ["ACTIVE", "CONVERTED"]
    for i in range(0, 300000, BATCH_SIZE):
        c_batch = [
            {"user_id": random.randint(1, 50000), "status": random.choice(statuses)}
            for _ in range(BATCH_SIZE)
        ]
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(tables["carts"].insert(), c_batch)
        print(f"Carts Chunk: Loaded rows {i} to {i + BATCH_SIZE}")

    # Capture boundaries
    with engine.connect() as connection:
        min_c = connection.execute(select(func.min(tables["carts"].c.id))).scalar() or 1
        max_c = (
            connection.execute(select(func.max(tables["carts"].c.id))).scalar()
            or 300000
        )

    # -------------------------------------------------------------
    # PHASE 3: SEED 600,000 CART ITEMS (Micro-Transactions)
    # -------------------------------------------------------------
    print("\nPhase 3: Injecting 600,000 relational items...")
    for i in range(0, 600000, BATCH_SIZE):
        item_batch = [
            {
                "cart_id": random.randint(min_c, max_c),
                "product_id": random.randint(min_p, max_p),
                "quantity": random.randint(1, 5),
                "unit_price_at_addition": float(random.randint(5, 150) + 0.99),
            }
            for _ in range(BATCH_SIZE)
        ]
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(tables["cart_items"].insert(), item_batch)
        print(f"Relational Items Chunk: Loaded rows {i} to {i + BATCH_SIZE}")

    print(
        f"\nSUCCESS! 1 Million rows safely committed to disk in {time.time() - start_time:.2f}s."
    )


if __name__ == "__main__":
    seed_database()
