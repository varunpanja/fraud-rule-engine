#!/usr/bin/env python3
"""
Standalone Database Seeding Script for Fraud Rule Engine Demo.
Run with: python seed.py
"""
import sys
import os

# Ensure backend root is on python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models import Transaction, FraudFlag
from app.services.seed_service import seed_demo_database


def main():
    print("=" * 60)
    print("[+] Fraud Detection Rule Engine - Demo Data Seeder")
    print("=" * 60)

    # Initialize tables
    print("Creating database schema if not present...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Seeding demo transactions and fraud flags...")
        result = seed_demo_database(db)
        print("\n[SUCCESS] Database Seeding Completed Successfully!")
        print(f"   * Total Transactions:   {result['total_transactions']}")
        print(f"   * Flagged Transactions: {result['flagged_transactions']}")
        print("\nScenarios Loaded:")
        for sc in result["scenarios_included"]:
            print(f"   [x] {sc}")
        print("=" * 60)
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Seeding failed with error: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
