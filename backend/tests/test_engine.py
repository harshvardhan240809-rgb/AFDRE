from app.simulation.engine import SimulationEngine


def test_create_simulation_builds_seed_data():
    engine = SimulationEngine()
    state = engine.create_simulation()

    assert state["simulation_id"].startswith("SIM-")
    assert len(state["services"]) >= 10
    assert state["current_phase"] == "BASELINE"
    assert state["resilience_score"] == 100


def test_full_demo_executes_recovery_and_verification():
    engine = SimulationEngine()
    state = engine.run_full_demo()

    assert state["current_phase"] == "MEMORY"
    assert state["resilience_score"] > 0
    assert state["verification"]["status"] == "RECOVERY VERIFIED"
    assert len(state["memory_entries"]) >= 6


def test_failure_propagation_updates_dependents():
    engine = SimulationEngine()
    state = engine.create_simulation()
    state = engine.inject_failure(state["simulation_id"], "Payment Gateway Failure")

    payment = next(service for service in state["services"] if service["name"] == "Payment Service")
    order = next(service for service in state["services"] if service["name"] == "Order Service")

    assert payment["status"] == "FAILED"
    assert order["status"] == "DEGRADED"


def test_resilience_score_tracks_failure_and_recovery():
    engine = SimulationEngine()
    state = engine.create_simulation()

    state = engine.inject_failure(state["simulation_id"], "Payment Gateway Failure")

    assert state["metrics"]["system_stability"] < 100
    assert state["resilience_score"] < 100

    state = engine.run_recovery(state["simulation_id"])
    state = engine.apply_chaos(state["simulation_id"])
    state = engine.verify_system(state["simulation_id"])

    assert state["verification"]["status"] == "RECOVERY VERIFIED"
    assert state["resilience_score"] > 80
