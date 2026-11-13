from django.db import connection

with connection.cursor() as cursor:
    for table in ["goods_product", "goods_category", "goods_review"]:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=%s",
            [table],
        )
        exists = cursor.fetchone()
        print(f"\nTABLE: {table} | EXISTS: {bool(exists)}")

        if exists:
            cursor.execute(f"PRAGMA table_info({table})")
            print("COLUMNS:", [row[1] for row in cursor.fetchall()])

    cursor.execute(
        "SELECT app, name FROM django_migrations WHERE app=%s",
        ["goods"],
    )
    print("\nMIGRATIONS:", cursor.fetchall())
