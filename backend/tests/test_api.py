from app.services import ctgov


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["database"] == "connected"


def test_analyze_saves_and_reads_back(client):
    r = client.post("/api/criteria/analyze", json={"text": "Age >= 18 years", "title": "t1"})
    assert r.status_code == 200
    aid = r.json()["analysis_id"]
    again = client.get(f"/api/criteria/analyses/{aid}").json()
    assert again["title"] == "t1"
    assert again["criteria"][0]["field"] == "age"


def test_analyze_rejects_empty(client):
    assert client.post("/api/criteria/analyze", json={"text": ""}).status_code == 422


def test_missing_analysis_404(client):
    assert client.get("/api/criteria/analyses/99999").status_code == 404


def test_trial_search_uses_simplified_output(client, monkeypatch):
    # Fake the network call so tests never depend on an external website.
    fake = {"count": 1, "next_page_token": None, "studies": [{"nct_id": "NCT00000000"}]}
    monkeypatch.setattr("app.routers.trials.fetch_studies", lambda *a, **k: fake)
    r = client.get("/api/trials/search", params={"condition": "lung cancer"})
    assert r.json()["studies"][0]["nct_id"] == "NCT00000000"


def test_simplify_extracts_fields():
    raw = {
        "protocolSection": {
            "identificationModule": {"nctId": "NCT1", "briefTitle": "T"},
            "statusModule": {"overallStatus": "TERMINATED", "whyStopped": "Slow accrual"},
            "designModule": {"enrollmentInfo": {"count": 12}, "phases": ["PHASE2"]},
        }
    }
    s = ctgov._simplify(raw)
    assert s["why_stopped"] == "Slow accrual" and s["enrollment"] == 12
