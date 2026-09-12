import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Railway path fix (ModuleNotFoundError se bachne ke liye)
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.simulation.engine import SimulationEngine

app = FastAPI(title="MAYDAY AI", version="1.0.0")

# CORS Middleware (Frontend communication ke liye)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = SimulationEngine()

@app.get("/health")
def health() -&gt; dict[str, str]:
    return {"status": "ok"}

@app.post("/api/simulation/create")
def create_simulation() -&gt; dict[str, object]:
    return engine.create_simulation()

@app.get("/api/simulation/{simulation_id}")
def get_simulation(simulation_id: str) -&gt; dict[str, object]:
    state = engine.get_state(simulation_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return state

@app.get("/api/simulation/{simulation_id}/events")
def get_events(simulation_id: str) -&gt; dict[str, object]:
    state = engine.get_state(simulation_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return {"simulation_id": simulation_id, "events": state["agent_events"]}

@app.post("/api/simulation/{simulation_id}/discover")
def discover_risks(simulation_id: str) -&gt; dict[str, object]:
    state = engine.get_state(simulation_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return engine.discover_risks(simulation_id)

@app.post("/api/simulation/{simulation_id}/failure")
def inject_failure(simulation_id: str, scenario: str = "Payment Gateway Failure") -&gt; dict[str, object]:
    state = engine.get_state(simulation_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return engine.inject_failure(simulation_id, scenario)

@app.post("/api/simulation/{simulation_id}/recover")
def run_recovery(simulation_id: str) -&gt; dict[str, object]:
    state = engine.get_state(simulation_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return engine.run_recovery(simulation_id)

@app.post("/api/simulation/{simulation_id}/chaos")
def apply_chaos(simulation_id: str) -&gt; dict[str, object]:
    state = engine.get_state(simulation_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return engine.apply_chaos(simulation_id)

@app.post("/api/simulation/{simulation_id}/verify")
def verify_system(simulation_id: str) -&gt; dict[str, object]:
    state = engine.get_state(simulation_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return engine.verify_system(simulation_id)

@app.post("/api/simulation/full-demo")
def full_demo() -&gt; dict[str, object]:
    return engine.run_full_demo()

@app.get("/api/incidents")
def incidents() -&gt; list[dict[str, object]]:
    return engine.get_incidents()

@app.get("/api/risks")
def risks() -&gt; list[dict[str, object]]:
    return engine.get_latest_risks()

@app.get("/api/memory")
def memory() -&gt; list[dict[str, object]]:
    return engine.get_memory_entries()

@app.get("/api/metrics")
def metrics() -&gt; dict[str, object]:
    return engine.get_latest_metrics()
