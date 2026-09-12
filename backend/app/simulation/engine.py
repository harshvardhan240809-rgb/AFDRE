from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from app.memory import MemoryStore
from app.retrieval import RetrievalEngine


class SimulationEngine:
    def __init__(self) -> None:
        self.memory = MemoryStore()
        self.retrieval = RetrievalEngine(self._docs_path())
        self.simulations: dict[str, dict[str, Any]] = {}

    def _docs_path(self) -> Any:
        from pathlib import Path

        return Path(__file__).resolve().parent.parent.parent / "docs"

    def create_simulation(self) -> dict[str, Any]:
        simulation = self._build_seed_state()
        self.simulations[simulation["simulation_id"]] = simulation
        simulation["step_count"] = 0
        return deepcopy(simulation)

    def get_state(self, simulation_id: str) -> dict[str, Any] | None:
        return deepcopy(self.simulations.get(simulation_id))

    def discover_risks(self, simulation_id: str) -> dict[str, Any]:
        state = self.simulations[simulation_id]
        state["current_phase"] = "DISCOVERY"
        state["agent_events"].append(
            {
                "timestamp": self._now_iso(),
                "agent": "DISCOVERY AGENT",
                "message": "Critical dependency identified: Payment Service is a single point of failure.",
            }
        )

        risk = {
            "id": "RISK-001",
            "service": "Payment Service",
            "severity": "CRITICAL",
            "probability": "HIGH",
            "impact": "Order processing may stop if Payment Service becomes unavailable.",
            "risk_score": 9.2,
            "recommended_action": "Introduce redundant payment routing.",
        }

        state["risks"] = [risk]
        state["resilience_score"] = self._calculate_score(state)
        return deepcopy(state)

    def inject_failure(self, simulation_id: str, scenario: str) -> dict[str, Any]:
        state = self.simulations[simulation_id]
        state["current_phase"] = "DOOMSDAY"
        state["scenario"] = scenario
        state["agent_events"].append(
            {
                "timestamp": self._now_iso(),
                "agent": "DOOMSDAY AGENT",
                "message": f"{scenario} injected into the Digital Twin.",
            }
        )

        self._apply_scenario(state, scenario)
        state["resilience_score"] = self._calculate_score(state)
        return deepcopy(state)

    def run_recovery(self, simulation_id: str) -> dict[str, Any]:
        state = self.simulations[simulation_id]
        state["current_phase"] = "RECOVERY"

        relevant_docs = self.retrieval.retrieve("payment failover backup gateway recovery")
        related_incidents = self.memory.find_related("Payment Gateway Failure", ["Payment Service"])

        state["retrieval"] = {
            "documents": relevant_docs,
            "related_incidents": related_incidents,
        }

        state["recovery_plan"] = {
            "plan_version": "v1",
            "steps": [
                "Route new payment requests to the backup gateway.",
                "Queue failed transactions.",
                "Validate backup gateway health.",
                "Retry queued transactions.",
            ],
        }

        state["agent_events"].append(
            {
                "timestamp": self._now_iso(),
                "agent": "RECOVERY AGENT",
                "message": "Retrieved Payment Failover SOP and prior incident context; preparing recovery plan.",
            }
        )

        self._apply_recovery(state)
        state["resilience_score"] = self._calculate_score(state)
        return deepcopy(state)

    def apply_chaos(self, simulation_id: str) -> dict[str, Any]:
        state = self.simulations[simulation_id]
        state["current_phase"] = "CHAOS"
        state["chaos_events"].append(
            {
                "timestamp": self._now_iso(),
                "agent": "CHAOS AGENT",
                "message": "Database latency increased to 900ms, invalidating the current recovery plan.",
            }
        )
        state["agent_events"].append(
            {
                "timestamp": self._now_iso(),
                "agent": "CHAOS AGENT",
                "message": "Database latency increased to 900ms.",
            }
        )

        database = self._get_service_by_name(state, "Database")
        database["status"] = "DEGRADED"
        database["latency"] = 900
        database["health"] = 58

        order = self._get_service_by_name(state, "Order Service")
        order["status"] = "DEGRADED"

        state["plan_version"] = "v2"
        state["recovery_plan"] = {
            "plan_version": "v2",
            "steps": [
                "Enable database replica.",
                "Reduce retry pressure.",
                "Queue requests.",
                "Stabilize database.",
                "Resume payment retries.",
                "Verify transaction consistency.",
            ],
        }
        state["agent_events"].append(
            {
                "timestamp": self._now_iso(),
                "agent": "RECOVERY AGENT",
                "message": "Recovery environment changed. Plan v1 invalidated; generating Plan v2.",
            }
        )
        state["resilience_score"] = self._calculate_score(state)
        return deepcopy(state)

    def verify_system(self, simulation_id: str) -> dict[str, Any]:
        state = self.simulations[simulation_id]
        state["current_phase"] = "VERIFICATION"

        for service in state["services"]:
            service["status"] = "HEALTHY"
            service["health"] = 100
            service["failure_state"] = False
            service["recovery_state"] = "READY"

        state["verification"] = {
            "status": "RECOVERY VERIFIED",
            "details": {
                "Payment Service": "HEALTHY",
                "Order Service": "HEALTHY",
                "Database": "HEALTHY",
                "Transaction Consistency": 100,
                "Data Loss": 0,
                "Recovery Time": 42,
            },
        }

        state["agent_events"].append(
            {
                "timestamp": self._now_iso(),
                "agent": "VERIFICATION AGENT",
                "message": "Recovery verified. Transaction consistency reached 100% and data loss remained at 0%.",
            }
        )

        state["resilience_score"] = self._calculate_score(state)
        state["current_phase"] = "MEMORY"
        state["memory_entries"] = self._append_memory_entry(state)
        return deepcopy(state)

    def run_full_demo(self) -> dict[str, Any]:
        sim = self.create_simulation()
        sim_id = sim["simulation_id"]

        self.discover_risks(sim_id)
        self.inject_failure(sim_id, "Payment Gateway Failure")
        self.run_recovery(sim_id)
        self.apply_chaos(sim_id)
        self.verify_system(sim_id)

        state = self.simulations[sim_id]
        state["current_phase"] = "MEMORY"
        state["timeline"] = [
            "BASELINE",
            "DISCOVERY",
            "DOOMSDAY",
            "FAILURE CASCADE",
            "RECOVERY",
            "CHAOS",
            "PLAN INVALIDATED",
            "REPLAN",
            "RECOVERY",
            "VERIFICATION",
            "RESILIENCE SCORE",
            "MEMORY UPDATED",
        ]
        state["agent_events"].append(
            {
                "timestamp": self._now_iso(),
                "agent": "CONTROLLER",
                "message": "Full MAYDAY scenario executed successfully.",
            }
        )
        state["resilience_score"] = self._calculate_score(state)
        state["memory_entries"] = self._append_memory_entry(state)
        return deepcopy(state)

    def get_incidents(self) -> list[dict[str, Any]]:
        return self.memory.get_entries()

    def get_latest_risks(self) -> list[dict[str, Any]]:
        latest: list[dict[str, Any]] = []
        for sim in self.simulations.values():
            latest.extend(sim.get("risks", []))
        return latest

    def get_memory_entries(self) -> list[dict[str, Any]]:
        return self.memory.get_entries()

    def get_latest_metrics(self) -> dict[str, Any]:
        if not self.simulations:
            sim = self.create_simulation()
            return sim["metrics"]
        latest_state = list(self.simulations.values())[-1]
        return latest_state["metrics"]

    def _build_seed_state(self) -> dict[str, Any]:
        services = [
            {"name": "Website", "status": "HEALTHY", "health": 100, "dependencies": ["API Gateway"], "current_load": 38, "failure_state": False, "recovery_state": "READY", "criticality": "HIGH", "latency": 94, "availability": 99.99},
            {"name": "API Gateway", "status": "HEALTHY", "health": 100, "dependencies": ["Order Service"], "current_load": 45, "failure_state": False, "recovery_state": "READY", "criticality": "HIGH", "latency": 81, "availability": 99.97},
            {"name": "Auth Service", "status": "HEALTHY", "health": 100, "dependencies": ["Database"], "current_load": 32, "failure_state": False, "recovery_state": "READY", "criticality": "MEDIUM", "latency": 76, "availability": 99.96},
            {"name": "Order Service", "status": "HEALTHY", "health": 100, "dependencies": ["Payment Service", "Inventory Service", "Notification Service", "Database"], "current_load": 55, "failure_state": False, "recovery_state": "READY", "criticality": "HIGH", "latency": 120, "availability": 99.95},
            {"name": "Payment Service", "status": "HEALTHY", "health": 100, "dependencies": ["API Gateway", "Payment Provider"], "current_load": 68, "failure_state": False, "recovery_state": "READY", "criticality": "HIGH", "latency": 120, "availability": 99.98},
            {"name": "Inventory Service", "status": "HEALTHY", "health": 100, "dependencies": ["Database"], "current_load": 43, "failure_state": False, "recovery_state": "READY", "criticality": "MEDIUM", "latency": 88, "availability": 99.95},
            {"name": "Notification Service", "status": "HEALTHY", "health": 100, "dependencies": ["Database"], "current_load": 36, "failure_state": False, "recovery_state": "READY", "criticality": "MEDIUM", "latency": 72, "availability": 99.94},
            {"name": "Database", "status": "HEALTHY", "health": 100, "dependencies": ["Backup Database"], "current_load": 57, "failure_state": False, "recovery_state": "READY", "criticality": "CRITICAL", "latency": 58, "availability": 99.99},
            {"name": "Backup Database", "status": "HEALTHY", "health": 100, "dependencies": [], "current_load": 22, "failure_state": False, "recovery_state": "READY", "criticality": "HIGH", "latency": 40, "availability": 99.90},
            {"name": "Customer Support", "status": "HEALTHY", "health": 100, "dependencies": ["Order Service"], "current_load": 24, "failure_state": False, "recovery_state": "READY", "criticality": "MEDIUM", "latency": 55, "availability": 99.92},
            {"name": "Analytics", "status": "HEALTHY", "health": 100, "dependencies": ["Database"], "current_load": 29, "failure_state": False, "recovery_state": "READY", "criticality": "LOW", "latency": 68, "availability": 99.93},
        ]

        state = {
            "simulation_id": f"SIM-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "current_phase": "BASELINE",
            "scenario": "Payment Gateway Failure",
            "services": services,
            "dependencies": {
                "Website": ["API Gateway"],
                "API Gateway": ["Order Service"],
                "Order Service": ["Payment Service", "Inventory Service", "Notification Service", "Database"],
                "Payment Service": ["API Gateway", "Payment Provider"],
                "Inventory Service": ["Database"],
                "Notification Service": ["Database"],
                "Database": ["Backup Database"],
                "Analytics": ["Database"],
                "Customer Support": ["Order Service"],
                "Auth Service": ["Database"],
            },
            "failures": [],
            "active_incidents": [],
            "agent_events": [
                {
                    "timestamp": self._now_iso(),
                    "agent": "CONTROLLER",
                    "message": "SYSTEM STATUS: ALL SYSTEMS NOMINAL",
                },
                {
                    "timestamp": self._now_iso(),
                    "agent": "DISCOVERY AGENT",
                    "message": "Baseline analysis complete. Safety checks passed.",
                },
            ],
            "recovery_plan": {"plan_version": "v0", "steps": []},
            "plan_version": "v0",
            "chaos_events": [],
            "metrics": {
                "recovery_time": 0,
                "system_stability": 100,
                "data_integrity": 100,
                "adaptability": 100,
                "business_impact": 100,
            },
            "resilience_score": 100,
            "memory_entries": self.memory.get_entries(),
            "risks": [],
            "verification": {"status": "SYSTEM NOMINAL", "details": {}},
            "timeline": ["BASELINE"],
            "retrieval": {"documents": [], "related_incidents": []},
        }
        return state

    def _apply_scenario(self, state: dict[str, Any], scenario: str) -> None:
        failure_map = {
            "Payment Gateway Failure": ["Payment Service"],
            "Database Latency": ["Database"],
            "Inventory Service Failure": ["Inventory Service"],
            "API Gateway Failure": ["API Gateway"],
            "Notification Service Failure": ["Notification Service"],
            "Authentication Service Failure": ["Auth Service"],
            "Backup System Unavailable": ["Backup Database"],
            "Network Dependency Failure": ["Website"],
        }

        targets = failure_map.get(scenario, ["Payment Service"])
        for target in targets:
            service = self._get_service_by_name(state, target)
            service["status"] = "FAILED"
            service["health"] = 15
            service["failure_state"] = True
            service["recovery_state"] = "FAILED"
            service["latency"] = 500

        # simplify cascade impact for visible degradation
        for service in state["services"]:
            if service["name"] in {"Order Service", "Customer Support", "Analytics"}:
                service["status"] = "DEGRADED"
                service["health"] = 55
                service["latency"] = 240

        state["timeline"] = ["BASELINE", "RISK DISCOVERED", "FAILURE INJECTED", "CASCADE", "RECOVERY PLAN"]
        state["failures"] = [scenario]

    def _apply_recovery(self, state: dict[str, Any]) -> None:
        payment = self._get_service_by_name(state, "Payment Service")
        payment["status"] = "RECOVERING"
        payment["health"] = 72
        payment["recovery_state"] = "RECOVERING"
        payment["failure_state"] = False
        payment["latency"] = 150

        order = self._get_service_by_name(state, "Order Service")
        order["status"] = "HEALTHY"
        order["health"] = 82
        order["latency"] = 140

        database = self._get_service_by_name(state, "Database")
        database["health"] = 80

        state["recovery_plan"]["steps"] = [
            "Route new payment requests to the backup gateway.",
            "Queue failed transactions.",
            "Validate backup gateway health.",
            "Retry queued transactions.",
        ]

        state["timeline"].append("RECOVERY")

    def _append_memory_entry(self, state: dict[str, Any]) -> list[dict[str, Any]]:
        note = {
            "incident_id": f"INC-{len(self.memory.entries) + 101}",
            "timestamp": self._now_iso(),
            "failure_type": state["scenario"],
            "root_cause": "Detected single point of failure with dynamic chaos event.",
            "affected_services": [service["name"] for service in state["services"] if service["status"] != "HEALTHY"],
            "recovery_plan": state["recovery_plan"]["plan_version"],
            "actions": [step for step in state["recovery_plan"]["steps"]],
            "chaos_events": state["chaos_events"],
            "verification_result": state["verification"]["status"],
            "recovery_time": state["metrics"]["recovery_time"],
            "data_integrity": state["metrics"]["data_integrity"],
            "business_impact": state["metrics"]["business_impact"],
            "lessons_learned": "The environment changed, so the system adapted and revalidated recovery using fresh evidence.",
            "confidence": 91,
        }
        self.memory.add_entry(note)
        return self.memory.get_entries()

    def _calculate_score(self, state: dict[str, Any]) -> int:
        self._refresh_metrics(state)
        metrics = state["metrics"]
        recovery_time = max(0, 100 - metrics["recovery_time"])
        system_stability = metrics["system_stability"]
        data_integrity = metrics["data_integrity"]
        adaptability = metrics["adaptability"]
        business_impact = metrics["business_impact"]

        score = (
            0.25 * recovery_time
            + 0.25 * system_stability
            + 0.20 * data_integrity
            + 0.15 * adaptability
            + 0.15 * business_impact
        )
        return int(round(score))

    def _refresh_metrics(self, state: dict[str, Any]) -> None:
        if not state["services"]:
            return

        total_health = sum(service["health"] for service in state["services"])
        service_count = len(state["services"])
        avg_health = total_health / service_count

        failed_services = sum(1 for service in state["services"] if service["status"] == "FAILED")
        degraded_services = sum(1 for service in state["services"] if service["status"] == "DEGRADED")
        recovering_services = sum(1 for service in state["services"] if service["status"] == "RECOVERING")

        state["metrics"]["system_stability"] = int(round(avg_health))
        state["metrics"]["data_integrity"] = max(0, 100 - (failed_services * 20) - (degraded_services * 10) - (recovering_services * 6))
        state["metrics"]["adaptability"] = max(0, min(100, 100 - (failed_services * 5) - (degraded_services * 3) - (recovering_services * 2) + (20 if state["recovery_plan"]["steps"] else 0)))
        state["metrics"]["business_impact"] = max(0, 100 - (failed_services * 12) - (degraded_services * 7))

        verification_details = state.get("verification", {}).get("details", {})
        if verification_details.get("Recovery Time") is not None:
            state["metrics"]["recovery_time"] = int(verification_details["Recovery Time"])
        elif state["current_phase"] in {"DISCOVERY", "DOOMSDAY", "RECOVERY", "CHAOS"}:
            state["metrics"]["recovery_time"] = max(0, min(100, 100 - len(state["active_incidents"])))
        else:
            state["metrics"]["recovery_time"] = 0

    def _get_service_by_name(self, state: dict[str, Any], name: str) -> dict[str, Any]:
        for service in state["services"]:
            if service["name"] == name:
                return service
        raise KeyError(f"Service not found: {name}")

    def _dependencies_of(self, service_name: str, state: dict[str, Any]) -> list[str]:
        return state["dependencies"].get(service_name, [])

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
