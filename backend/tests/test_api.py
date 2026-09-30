from datetime import datetime, timedelta


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_normal_transaction(client):
    payload = {
        "account_id": "ACC_TEST_01",
        "amount": 2500.0,
        "currency": "INR",
        "timestamp": datetime.utcnow().isoformat(),
        "latitude": 17.3850,
        "longitude": 78.4867,
        "location": "Hyderabad",
        "transaction_type": "TRANSFER"
    }
    response = client.post("/api/transactions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["account_id"] == "ACC_TEST_01"
    assert data["fraud_evaluation"]["is_flagged"] is False
    assert data["fraud_evaluation"]["risk_score"] == 0
    assert data["fraud_evaluation"]["risk_level"] == "LOW"


def test_create_unusual_amount_transaction_flags_fraud(client):
    payload = {
        "account_id": "ACC_TEST_02",
        "amount": 250000.0,  # Exceeds 100,000 threshold
        "currency": "INR",
        "timestamp": datetime.utcnow().isoformat(),
        "latitude": 19.0760,
        "longitude": 72.8777,
        "location": "Mumbai",
        "transaction_type": "TRANSFER"
    }
    response = client.post("/api/transactions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["fraud_evaluation"]["is_flagged"] is True
    assert data["fraud_evaluation"]["risk_score"] == 30
    assert data["fraud_evaluation"]["risk_level"] == "MEDIUM"
    assert len(data["fraud_evaluation"]["triggered_rules"]) == 1
    assert data["fraud_evaluation"]["triggered_rules"][0]["rule_name"] == "UNUSUAL_AMOUNT"


def test_review_and_clear_workflow(client):
    # Ingest flagged transaction
    payload = {
        "account_id": "ACC_TEST_03",
        "amount": 300000.0,
        "currency": "INR",
        "timestamp": datetime.utcnow().isoformat(),
        "latitude": 19.0760,
        "longitude": 72.8777,
        "location": "Mumbai",
        "transaction_type": "TRANSFER"
    }
    create_res = client.post("/api/transactions", json=payload)
    assert create_res.status_code == 201

    # List fraud flags
    flags_res = client.get("/api/fraud/flags")
    assert flags_res.status_code == 200
    flags = flags_res.json()
    assert len(flags) > 0
    flag_id = flags[0]["id"]
    assert flags[0]["status"] == "PENDING"

    # Review flag
    review_res = client.put(f"/api/fraud/flags/{flag_id}/review", json={"reviewer_notes": "Reviewed and confirmed."})
    assert review_res.status_code == 200
    assert review_res.json()["status"] == "REVIEWED"
    assert review_res.json()["reviewer_notes"] == "Reviewed and confirmed."

    # Clear flag
    clear_res = client.put(f"/api/fraud/flags/{flag_id}/clear", json={"reviewer_notes": "Cleared false alarm."})
    assert clear_res.status_code == 200
    assert clear_res.json()["status"] == "CLEARED"
    assert clear_res.json()["reviewer_notes"] == "Cleared false alarm."


def test_dashboard_stats_and_demo_seed(client):
    # Seed demo data
    seed_res = client.post("/api/demo/seed")
    assert seed_res.status_code == 200
    seed_data = seed_res.json()
    assert seed_data["total_transactions"] > 0
    assert seed_data["flagged_transactions"] > 0

    # Get stats
    stats_res = client.get("/api/dashboard/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_transactions"] >= 10
    assert stats["flagged_transactions"] >= 4
    assert stats["pending_review_count"] >= 1
    assert stats["high_risk_count"] >= 1
