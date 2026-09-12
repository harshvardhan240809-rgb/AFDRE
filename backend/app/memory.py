from copy import deepcopy
from datetime import datetime, timezone
from typing import Any


class MemoryStore:
    def __init__(self) -> None:
        self.entries = self._seed_incidents()

    def _seed_incidents(self) -> list[dict[str, Any]]:
        base = []
        for index, item in enumerate(
            [
                {
                    "incident_id": "INC-101",
                    "timestamp": "2026-09-08T09:12:00Z",
                    "failure_type": "Payment Gateway Failure",
                    "root_cause": "Primary gateway provider outage",
                    "affected_services": ["Payment Service", "Order Service"],
                    "recovery_plan": "Backup gateway failover with queued retries.",
                    "actions": ["switch_payment_gateway", "queue_transactions", "retry_transactions"],
                    "chaos_events": [],
                    "verification_result": "RECOVERY VERIFIED",
                    "recovery_time": 42,
                    "data_integrity": 100,
                    "business_impact": 84,
                    "lessons_learned": "Backup routing should be pre-tested before peak traffic.",
                    "confidence": 92,
                },
                {
                    "incident_id": "INC-102",
                    "timestamp": "2026-09-08T16:44:00Z",
                    "failure_type": "Database Latency",
                    "root_cause": "Replica lag and read amplification",
                    "affected_services": ["Database", "Order Service", "Analytics"],
                    "recovery_plan": "Database replica activation and capacity increase.",
                    "actions": ["activate_database_replica", "increase_database_capacity"],
                    "chaos_events": ["Database latency increased to 900ms"],
                    "verification_result": "PARTIALLY RECOVERED",
                    "recovery_time": 58,
                    "data_integrity": 100,
                    "business_impact": 76,
                    "lessons_learned": "Read traffic should be shifted before applying retry pressure.",
                    "confidence": 88,
                },
                {
                    "incident_id": "INC-103",
                    "timestamp": "2026-09-09T08:15:00Z",
                    "failure_type": "Inventory Service Failure",
                    "root_cause": "Inventory cache saturation",
                    "affected_services": ["Inventory Service", "Order Service"],
                    "recovery_plan": "Restart cache and restore inventory consistency.",
                    "actions": ["restart_service", "restore_backup"],
                    "chaos_events": [],
                    "verification_result": "RECOVERY VERIFIED",
                    "recovery_time": 35,
                    "data_integrity": 99,
                    "business_impact": 80,
                    "lessons_learned": "Inventory service should use stale-safe fallback read paths.",
                    "confidence": 90,
                },
                {
                    "incident_id": "INC-104",
                    "timestamp": "2026-09-09T18:05:00Z",
                    "failure_type": "API Gateway Failure",
                    "root_cause": "Unexpected traffic surge and upstream timeout",
                    "affected_services": ["API Gateway", "Website", "Customer Support"],
                    "recovery_plan": "Traffic reroute and gateway restart.",
                    "actions": ["route_traffic", "restart_service"],
                    "chaos_events": ["Traffic burst created gateway saturation"],
                    "verification_result": "RECOVERY VERIFIED",
                    "recovery_time": 46,
                    "data_integrity": 100,
                    "business_impact": 78,
                    "lessons_learned": "Rate limiting should be applied before restoring full traffic.",
                    "confidence": 89,
                },
                {
                    "incident_id": "INC-105",
                    "timestamp": "2026-09-10T12:30:00Z",
                    "failure_type": "Notification Service Failure",
                    "root_cause": "Delivery queue overflow",
                    "affected_services": ["Notification Service", "Order Service", "Customer Support"],
                    "recovery_plan": "Restart notification workers and drain queue.",
                    "actions": ["restart_service", "queue_transactions"],
                    "chaos_events": [],
                    "verification_result": "RECOVERY VERIFIED",
                    "recovery_time": 24,
                    "data_integrity": 100,
                    "business_impact": 82,
                    "lessons_learned": "Queue drain should be automated with priority routing.",
                    "confidence": 94,
                },
            ]
        ):
            item["timestamp"] = item["timestamp"]
            base.append(item)
        return base

    def get_entries(self) -> list[dict[str, Any]]:
        return deepcopy(self.entries)

    def add_entry(self, entry: dict[str, Any]) -> None:
        self.entries.append(entry)

    def find_related(self, failure_type: str, affected_services: list[str]) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        failure_norm = failure_type.lower()
        for entry in self.entries:
            score = 0
            if failure_norm in entry["failure_type"].lower():
                score += 3
            for service in affected_services:
                if service in entry["affected_services"]:
                    score += 2
            if score:
                matches.append({**entry, "relevance": score})
        matches.sort(key=lambda item: item["relevance"], reverse=True)
        return matches[:3]
