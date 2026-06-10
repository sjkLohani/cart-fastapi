import os
import random
import time

from sqlalchemy import MetaData, create_engine, func, select

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable is missing.")
    exit(1)

print("Connecting to cloud MySQL instance...")
engine = create_engine(DATABASE_URL)
metadata = MetaData()


def clear_old_test_data(connection, tables):
    """Safely clears out old items to ensure clean tracking for the 1M test."""
    print("Cleaning up old test entries to optimize execution...")
    connection.execute(tables["cart_items"].delete())
    connection.execute(tables["carts"].delete())
    connection.execute(tables["products"].delete())


def seed_database():
    start_time = time.time()
    metadata.reflect(bind=engine)

    # Verify all required tables exist
    required = ["products", "carts", "cart_items"]
    if not all(t in metadata.tables for t in required):
        print("Error: Missing core tables. Please initialize FastAPI first.")
        return

    tables = {t: metadata.tables[t] for t in required}
    BATCH_SIZE = 50000

    with engine.begin() as connection:
        # Optional: Uncomment if you want a completely fresh 1M state
        # clear_old_test_data(connection, tables)

        # -------------------------------------------------------------
        # STEP 1: SEED 100,000 PRODUCTS
        # -------------------------------------------------------------
        print("Phase 1: Injecting 100,000 products...")
        for i in range(0, 100000, BATCH_SIZE):
            p_batch = [
                {
                    "name": f"Product-SKU-{idx}",
                    "current_price": float((idx % 150) + 4.99),
                }
                for idx in range(i, i + BATCH_SIZE)
            ]
            connection.execute(tables["products"].insert(), p_batch)

        # Dynamically capture the valid product ID boundary
        min_p = (
            connection.execute(select(func.min(tables["products"].c.id))).scalar() or 1
        )
        max_p = (
            connection.execute(select(func.max(tables["products"].c.id))).scalar()
            or 100000
        )
        print(f"Products loaded. Valid ID range: [{min_p} to {max_p}]")

        # -------------------------------------------------------------
        # STEP 2: SEED 300,000 CARTS
        # -------------------------------------------------------------
        print("Phase 2: Injecting 300,000 carts...")
        statuses = ["ACTIVE", "ABANDONED", "COMPLETED"]
        for i in range(0, 300000, BATCH_SIZE):
            c_batch = [
                {"user_id": random.randint(1, 50000), "status": random.choice(statuses)}
                for _ in range(BATCH_SIZE)
            ]
            connection.execute(tables["carts"].insert(), c_batch)

        # Dynamically capture the valid cart ID boundary
        min_c = connection.execute(select(func.min(tables["carts"].c.id))).scalar() or 1
        max_c = (
            connection.execute(select(func.max(tables["carts"].c.id))).scalar()
            or 300000
        )
        print(f"Carts loaded. Valid ID range: [{min_c} to {max_c}]")

        # -------------------------------------------------------------
        # STEP 3: SEED 600,000 CART ITEMS
        # -------------------------------------------------------------
        print("Phase 3: Injecting 600,000 relational cart items...")
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
            connection.execute(tables["cart_items"].insert(), item_batch)
            print(f"Injected cart items chunk {i} to {i + BATCH_SIZE}")

    print(
        f"\nSUCCESS! 1 Million rows cleanly distributed across the ecosystem in {time.time() - start_time:.2f}s."
    )


if __name__ == "__main__":
    seed_database()
